import pygame as pg
from settings import *
import random
vec2 = pg.math.Vector2

class Sprite(pg.sprite.Sprite): #Lager en forelder-class med en funksjon som alle spritsene kommer til å bruke for å unngå repetisjon
    def __init__(self,pos, size, color = None, image = False):
        pg.sprite.Sprite.__init__(self) #pygame-funksjon som setter basisen for sprites
        
        if image == False: #Hvis spilleren ikke har bilde får den en farge
            self.image = pg.Surface(size)
            self.image.fill(color)
        else:
            self.image = pg.transform.scale(pg.image.load(image).convert_alpha(), (size)) # Setter bildet med størrelse
            
        self.rect = self.image.get_rect() #Funksjon som tar rectangelet rundt bildet
        self.pos = vec2(pos) #Lager en vektor for posisjonen
        

class Player(Sprite): # ASpillerens klasse
    def __init__(self,game,pos, size, color = None, image = False):
        Sprite.__init__(self, pos, size, color, image)
    
        self.time = 50 #Bestemmer tid mellom hver animasjonsframe
        self.lastTime = pg.time.get_ticks()
        self.size = size
        self.vel = vec2(0,0) #Fartsvektoren til spilleren
        self.acc = vec2(0,0) #Aksellerasjonsvektor
        self.game = game
        self.moveCount = 1 #Variabel som bestemmer hvilket bilde som vises i en liste over bilder
        
        #bools
        self.img = image
        self.bouncing = False 
        self.imgFlipped = False #Bestemmer om bildet flippes eller ikke
        
        self.image = pg.transform.scale(pg.image.load(self.img).convert_alpha(), (self.size))
    
    def update(self): #Oppdaterer spiller spritens positsjon, fart, bilde og akselerasjon
        
        if pg.time.get_ticks() - self.lastTime > self.time:
            self.lastTime = pg.time.get_ticks()
            self.moveCount+=1
        self.acc = vec2(0, GRAVITY)
        
        keys = pg.key.get_pressed() # sjekker hvilket keys som blir trykket ned
        
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = -PLAYER_ACC
            if not self.imgFlipped:
                self.imgFlipped = True
                
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x = PLAYER_ACC
            if self.imgFlipped:
                self.imgFlipped = False

        
        
        
        if self.game.scrollTo == None:
            self.vel.y += self.acc.y
            
            self.vel.x += self.acc.x +self.vel.x * PLAYER_FRICTION #FRICTION - uten kan spilleren akselerere til det uendelige
            
            self.pos += self.vel + 0.5 * self.acc #veiformel 2 s(t) = v(t) + 1/2at^2
        else:  #Hvis scrollToPlayer() er aktivert står spilleren stille
            self.vel.x = 0
            self.vel.y = 0
        
        
        #spilleren wrapper rundt skjermen
        if self.pos.x > WIDTH + self.rect.width/2:
            self.pos.x = 0 - self.rect.width/2
        elif self.pos.x < 0 - self.rect.width/2:
            self.pos.x = WIDTH + self.rect.width/2
            
        

        self.rect.midbottom = self.pos # posisjonen regnes utifra midtbunenn til spilleren
        
        if (abs(self.vel.x) <=1 and not self.bouncing): #IDLE animasjonen spilles hvis spilleren har under 1 i fart i x retning
            self.time = 50
            self.image = pg.transform.scale(pg.image.load(PLAYER_IDLE[self.moveCount]),(self.size))
            
        elif abs(self.vel.x) > 1 and not self.bouncing: #Løpe animasjon spilles av
            self.time = 50-abs(self.vel.x)*2
            self.image = pg.transform.scale(pg.image.load(PLAYER_RUN[self.moveCount]),(self.size))
        
        if self.bouncing: #Hoppe animasjonen spilles av
            self.time = 50
            if self.vel.y == 0:
                self.moveCount=(int(len(PLAYER_JUMP)/2))
            self.image = pg.transform.scale(pg.image.load(PLAYER_JUMP[self.moveCount]),(self.size))
        
        if self.imgFlipped:
                self.image = pg.transform.flip(self.image, True, False)
        
        if self.moveCount == 14: #Det er bare 15 bilder 
            self.moveCount = 0 
        
    def bounce(self): #Spilleren bounces opp hvis bouncing = True
        self.vel.y = 0
        
        if self.bouncing: 
            self.vel.y = BOUNCE_FACTOR
            self.moveCount =0
        

class Platform(Sprite): #Definerer platformen som calles
    def __init__(self, game, pos, size, moving, breaking, platSpeed, color = None, image = False):
        
        self.color = color
        self.speed = random.randint(1,platSpeed)
        self.moving = moving #Bestemmer om den beveger seg eller ikke
        self.breaking = breaking #Bestemmer om den faller eller ikke
        self.pos = pos #posisjon
        self.face = False # Bestemmer ansiktet
        self.game = game
        self.dir = 1 #Bestemmer retningen platformen beveger seg hvis rød
        self.doBreak = False #Gjør at platformen faller hvis True
        self.vel = vec2(0,0)
        self.size = vec2(size)
        self.faceShift = 0 #Bestemmer hvor langt ned ansiktet skal være på platformen
        
        if color == None: #Hvis den ikke har fått en farge, får den en
            
            if self.moving == 1 or (breaking == 1 and self.moving == 1): #Rød platform
                self.platType = 2
                self.faceShift = 7
                
            elif breaking == 1: #Oransje platform
                self.platType = 1
                self.faceShift = 10
                
            else: #Grønn platform
                self.platType =0
                self.faceShift = 5
            
            self.color = PLAT_COLORS[self.platType] # Henter farge fra settings
            self.face = pg.transform.scale(pg.image.load(PLAT_FACES[self.platType]).convert_alpha(), (int(self.size.y*2),int(self.size.y*2))) #Ansiktbilde settes
            self.faceImage = self.face.get_rect()
            

            
        Sprite.__init__(self, pos, size, self.color, image)
        
        self.rect.x, self.rect.y = self.pos.x, self.pos.y #setter spritens posisjon til posisjonsvariablene
        
        
    def update(self): #oppdaterer platformens posisjon
    
        if self.moving == 1: #hvis grønn, gå fra side til side
            if self.rect.right >= WIDTH-self.speed:
                self.dir*=-1
            elif self.rect.left <= self.speed:
                self.dir *=-1
            
            self.rect.x += self.speed*self.dir
            
            
        if self.doBreak: #Platformen faller hvis aktivert
            
            self.vel.y += GRAVITY
            self.rect.y += self.vel.y * 0.5 *GRAVITY
        
        if self.face != False: #setter posisjonen til ansiktet
            self.faceImage.centery = self.rect.centery + self.faceShift
            self.faceImage.centerx = self.rect.centerx
            
        

class Cloud(Sprite): #Sky-objekt
    def __init__(self,pos, size, image):
        Sprite.__init__(self, pos, size, None, image)
        self.rect.center = self.pos.x,self.pos.y #posisjon regnes fra midten
        self.scrollSpeed = random.randint(2, 4)
        
        
    
        
class Button(Sprite): #definerer knapper(ikke tatt i bruk enda)
    def __init__(self,game, pos, size, text, textsize, textcolor, color, image = False):
        Sprite.__init__(self, pos, size, color, image)
        self.rect.center = (self.pos.x, self.pos.y)
        self.text = text
        self.textSize = textsize
        self.textColor = color
        self.game = game
        
    def draw(self): #Tegner knappens text
        self.game.drawText(self.text, self.textSize , self.textColor, self.rect.center)
        
    