import pygame as pg
import sys
import random
from settings import *
from sprites import *
from getworkingpath import *
from os import path


class Game:
    def __init__(self):
        
        #starter pygame
        pg.init()
        pg.mixer.init()
        pg.display.set_caption(TITLE)
        
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        self.running = True
        self.clock = pg.time.Clock()
        self.fontName = pg.font.match_font(FONT_NAME)
        
        self.cloudImages = [getworkingpath() + '/multimedia/images/backgroundObjects/cloud.png'] #Skybilder

        
        self.firstTime = True #Hvis True starter spilleren i menyen
        self.loadData()
    
    def loadData(self): #Laster inn highscore fra highscore.txt
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, PLAYER_DATA), 'r') as f: #Åpner filen så den kan leses
            try:
                self.highScore = int(f.read())
            except:
                self.highScore = 0
        
    def new(self): # Calles når spilleren faller av skjermen, resetter alle variabler
    
        #game variables
        self.posShift = HEIGHT #Variabel som tilsier hvor bunnen av "kameraet" er
        self.menuOpen = True #Hvis åpen kan spilleren nå "menyen"
        self.groundHeight = 20 #Hvor store de grå platformene er
        self.scrollTo = None #Boolian som bestemmer om scrollToPlayer() calles eller ikke
        self.score = 0 #Setter score til 0
        self.oldScore = 0 #Variabel som brukes for å bestemme når vanskelighetsgraden skal øke
        
        #bgObjects variables
        self.bgObjectsNum = 5 #antall skyer totalt
        
        #platform variables
        self.platSpacing = 180 #Avstand mellom platformer
        self.platWidth = 100 #Platformenes bredde
        self.platHeight = 25 #Platformenes tykkelse
        self.platSpeed = 2 #Max hastigheten på de rød platformene
        self.platMovingProb = 0 # høyere betyr lavere sannsynlighet for at platform beveger seg
        self.platBreakingProb = 0 # høyere betyr lavere sannsynlighet for oransje platform som faller
        self.platNum = int(HEIGHT/self.platSpacing) + 1 #Antall platformer er så  mange som er på plass på skjermen
        
        #spriteggroups
        self.bgObjects = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.startPlats = pg.sprite.Group()
        self.allSprites = pg.sprite.Group()
        self.buttons = pg.sprite.Group()
        self.menuSprites = pg.sprite.Group()
        
        #spawner spilleren
        self.player = Player(self,(WIDTH / 2, HEIGHT-self.groundHeight), (40,60), WHITE, PLAYER_IDLE[0])
        self.allSprites.add(self.player)

        #Hvis det er første gang spawner man i menyen. Hvis ikke spawner man over, hoppende
        if self.firstTime:
            self.posShift = 0
        elif not self.firstTime: 
            self.player.bouncing = True
        
        for pn in range(0,self.platNum+1): #lager start platformene og bakken
            if pn == 0 : #lager neserste grå platformer
                p = Platform(self,(-self.player.rect.width,HEIGHT-self.groundHeight),(WIDTH+self.player.rect.width*2,self.groundHeight),0,0,1, GREY)
            elif pn == self.platNum: #Lager øverste grå platform
                p = Platform(self,(self.player.rect.width*2,-self.groundHeight),(WIDTH-self.player.rect.width*4,self.groundHeight),0,0,1, GREY) 
            else:
                p = Platform(self,(WIDTH/self.platNum * pn,HEIGHT-self.platSpacing*pn),(self.platWidth,self.platHeight),0,0,1, None)
            p.rect.y += self.posShift
            self.allSprites.add(p)
            self.startPlats.add(p)
        
        self.lastPlatPos = HEIGHT - (len(self.startPlats)-1)*self.platSpacing #Setter hvor neste platform skal spawne
        
        if not self.firstTime:
            self.lastPlatPos = HEIGHT
        else:
            self.lastPlatPos = 0
    
        #spawner skyer
        for bgObj in range(self.bgObjectsNum):

            cPos = self.lastPlatPos - random.randint(HEIGHT, HEIGHT*2) -bgObj*(random.randint(0,HEIGHT*2)) #Bestemmer skyens posisjon - spawner over skjermen
            cWidth = int(random.randint(180, 240)) #Bestemmer skyens bredde
            c = Cloud((random.randint(-cWidth,WIDTH) , cPos),(cWidth,random.randint(70, 140)), self.cloudImages[0]) #lager skyen
            self.bgObjects.add(c)


        self.run() #kjører gameloopen
        
        
    
            
   
        
            
    def run(self):
        self.playing = True 
        while self.playing: #gameloop
            self.clock.tick(FPS) # Holder fps på max 60
            self.events()  #Sjekker events
            self.update() #Oppdaterer tingene på skjermen 
            self.draw() #Tegner tingene på skjermen med oppdatert info
        
            
    def update(self): # Oppdaterer alle spillvariabler og skjermobjekter 
          
        #Vankelighetsgraden øker
        if self.score > 0 and self.platBreakingProb == 0:
            self.oldScore = self.score
            self.platBreakingProb = 8
            self.platMovingProb = 8
        elif self.score-self.oldScore >= 100+self.oldScore/2 and self.platMovingProb > 1:
            self.oldScore = self.score
            self.platMovingProb -=1#Større sansynlighet for rød platform
            self.platBreakingProb -=1 #Større sansynlighet for oransje platform
            self.platSpeed +=1 #Økning i røde platformers hastighet
        
        #Sjekker kollisjoner
        if self.player.vel.y >= 0: # bare sprett opp hvis spilleren er på vei ned
            if self.menuOpen and self.posShift + HEIGHT - self.groundHeight-(self.player.pos.y-HEIGHT) < HEIGHT*2: #sjekker om menyen er åpen og at spilleren ikke er over øverste grå platform
                hits = pg.sprite.spritecollide(self.player, self.startPlats, False) #sjekker kollisjon mellom startplatformene og spillert
            elif self.scrollTo == None: 
                hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            else: hits = None
            
            if hits and hits != None: 
                #Hvis spilleren er oppå platformen
                if self.player.rect.bottom - (self.player.vel.y*2+self.player.acc.y*0.5) <= hits[0].rect.top and self.player.rect.right-self.player.rect.width/4 > hits[0].rect.left and self.player.rect.left+self.player.rect.width/4 < hits[0].rect.right: #spillerens bein må være over platformen (trekker fra vel fordi hiten ofte ikke registrerer før spilleren er inni platformen)
                    self.player.pos.y = hits[0].rect.top
                    self.player.bounce() #Spilleren hopper
                    
                   
                    if hits[0].color == ORANGE: #Hvis fargen til platformen er orange
                        hits[0].doBreak = True#Platformen faller
                        pg.mixer.Sound.play(pg.mixer.Sound(JUMP_SOUND)) #SPiller av hoppelyd
                        pg.mixer.Sound.play(pg.mixer.Sound(BREAK_SOUND)) #Spiller lyd
                        hits[0].face = pg.transform.scale(pg.image.load(PLAT_FACES[-1]).convert_alpha(), (int(hits[0].rect.height*2),int(hits[0].rect.height*2))) #Bytter ansikt til overrasket
                        
                    elif hits[0].color == GREEN or hits[0].color == RED:
                         pg.mixer.Sound.play(pg.mixer.Sound(JUMP_SOUND)) #SPiller av hoppelyd
                    
                    #Hvis fragen til platformen er grå kameraet beveger seg, står spilleren stille
                    if (hits[0].color == GREY or hits[0].color == WHITE) and self.scrollTo != None:
                        if self.menuOpen:
                            self.player.bouncing = False
                            self.player.rect.bottom=hits[0].rect.top
            
                    
            
            
        #hvis spilleren faller av skjermen / GAMEOVER
        if self.player.rect.top + self.player.vel.y > HEIGHT:
            if not pg.mixer.get_busy() and not self.menuOpen:# Spiller falle luden hvis den ikke spiller fra får og man ikke går ned til menyen
                pg.mixer.Sound.play(pg.mixer.Sound(FALL_SOUND)) 
            if not self.menuOpen and self.player.rect.top > HEIGHT + 50:
                self.firstTime = False
                self.playing = False
            
            
        
        self.updateCamera() 
        self.allSprites.update() #funksjon som oppdaterer alle objektene
        
        
        
        #lager ny platformer
        if len(self.platforms) < self.platNum:
            platPos = self.lastPlatPos - self.platSpacing
            p = Platform(self,(random.randrange(0,WIDTH - int(self.platWidth)) , platPos), (self.platWidth, self.platHeight), random.randint(0, int(self.platMovingProb)),random.randint(0, int(self.platBreakingProb)), self.platSpeed )
            self.allSprites.add(p)
            self.platforms.add(p)
            self.lastPlatPos = platPos
                

    
    def events(self): #sjekker input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.menuOpen = False
                self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN: #gjør at spilleren begynner å bounce
                if event.key == pg.K_SPACE:
                    self.player.bouncing = True 
            
    def draw(self): #tegner det som skal på skjermen
        self.screen.fill(BACKGROUND_COLOR) #Bakgrunn
        
         
        
        self.bgObjects.draw(self.screen)
        self.allSprites.draw(self.screen) #tegner alle sprites
        
        #Tegner ansikt
        for plat in self.platforms:
            self.drawFace(plat)
        
        if self.menuOpen: #Tegner ansiktene til startplatformene
            for plat in self.startPlats:
                self.drawFace(plat)
    
        #text
        self.drawText("SCORE: " + str(self.score), 20, WHITE, (20 ,20), 'topleft')
        self.drawText("HIGHSCORE: " + str(self.highScore), 20, WHITE, (20 , 44), 'topleft')
        
        #menu
        if self.menuOpen: #Hvis spiller kan komme til menyen
            
            self.drawText("hop(e)", 40, WHITE, (WIDTH/2, 48 + self.posShift))
            self.drawText("Credits: Emil Lunde-bakke", 16, WHITE, (5,HEIGHT-self.groundHeight + self.posShift), 'topleft')
            
            self.menuSprites.draw(self.screen)
            
            for button in self.buttons: #gir knappene text (ikke tatt i bruk enda)
                self.drawText(button.text, 14 , BLACK, button.rect.center)
            
            #Instructions
            self.drawText("HOP TOWARDS THE SKY!", 20, WHITE, (WIDTH/2, HEIGHT/2 - 100 + self.posShift))
            self.drawText("(PRESS SPACE TO START JUMPING)", 16, WHITE, (WIDTH/2, HEIGHT/2 - 40+self.posShift))
            self.drawText("MOVE LEFT AND RIGHT WITH ARROW KEYS", 16, WHITE, (WIDTH/2, HEIGHT/2-60+self.posShift))
          
        #sjekker om scoren er høyere enn highscore
        self.highScore = max(self.score,self.highScore)
        
        pg.display.update()
    
    def updateCamera(self): #oppdaterer kamera posisjonen / dytter alle objekter på skjermen opp eller ned
     # hvis spilleren er over 3/4 av skjermen og man er over menyen følger kameraet spilleren
        if self.player.rect.top <= HEIGHT / 4 and self.posShift >= HEIGHT:
            self.cameraPos = -(self.player.vel.y) 
            self.player.pos.y += self.cameraPos
            self.posShift += self.cameraPos
            self.score +=1
            self.lastPlatPos += self.cameraPos #skyver neste platforms spawn ned
            
            #gjør størrelsen på platformene mindre og mellomrommet mellom dem større
            if self.platSpacing < 260:
                self.platSpacing += 0.01
            if self.platWidth > self.player.rect.width:
                self.platWidth -= 0.01
            
            #Passer på at scoren er 0 før gamet starter og skrur av menyen hvis kameraet er over den grå platformen
            if self.menuOpen:
                self.score = 0
                if self.posShift > HEIGHT:
                    self.menuOpen = False
                
            if self.posShift < HEIGHT + self.groundHeight:
                for plat in self.startPlats:
                        plat.rect.y += self.cameraPos
            elif self.posShift > HEIGHT + self.groundHeight and len(self.startPlats) > 0: # fjerner startplatformene
                for plat in self.startPlats:
                    plat.kill()
            
            #Dytter platformene ned
            for plat in self.platforms:
                plat.rect.y += self.cameraPos
                #Hvis platformen kommer under skjermen får den nye verdier
                if plat.rect.top >= HEIGHT and not self.menuOpen:
                    self.updateObj(plat)
            
            #flytter bakgrunnsobjektene (skyene) ned. De har en variabel som tilsier hvor fort de flyttes nedover
            for thing in self.bgObjects:
                thing.rect.y += self.cameraPos/thing.scrollSpeed
                
                if thing.rect.top >= HEIGHT:
                    self.updateObj(thing)
                    
                
        
        if self.menuOpen and self.posShift <= HEIGHT:#Hvis menyen er åpen og mulig å komme til
            #Hvis spilleren er over/under skjermen og oppå en grå platform, flyttes kameraet til spilleren
            if self.player.rect.bottom < 0 and self.player.rect.right > self.player.rect.width and self.player.rect.x < WIDTH-self.player.rect.width*2:
                self.scrollTo = 'UP'
            elif self.player.rect.top > HEIGHT  and self.posShift > 0:
                self.scrollTo = 'DOWN'
            

            if self.scrollTo != None:
                self.scrollToPlayer(self.scrollTo,10)
            

    def updateObj(self,obj): #gir obj nye verdier
        
        #Hvis obj er en platform, får den ny posisjon, størrelse og farge
        if obj in self.platforms:
            platPos = self.lastPlatPos - self.platSpacing
            obj.__init__(self,(random.randrange(0,WIDTH - int(self.platWidth)) , platPos), (int(self.platWidth), self.platHeight), random.randint(0, int(self.platMovingProb)),random.randint(0, int(self.platBreakingProb)), self.platSpeed )
            self.lastPlatPos = platPos
        
        #Hvis obj er en sky får den ny posisjon og størrelse
        elif obj in self.bgObjects:
            cPos = self.lastPlatPos - random.randint(500, HEIGHT*2)
            cWidth = int(random.randint(180, 240))
            obj.rect.x,obj.rect.y = random.randint(-cWidth,WIDTH) , cPos
            obj.size = (cWidth,random.randint(70, 140))


    def scrollToPlayer(self, way,speed): #Beveger alt på skjermen ned/ opp med hastigheten speed til spilleren er på bunnen av skjermen igjen
        
        if way =='DOWN':
            direction = -1
        elif way == 'UP':
            direction = 1
        
        self.player.bouncing = False #Spilleren spretter ikke
        
        for sprite in self.allSprites:#Beveger alle sprites
            if sprite != self.player:
                sprite.rect.y +=speed*direction
        
        self.posShift += speed*direction #endrer posShift til å hvor "kameraet er"
        self.lastPlatPos += speed *direction
        
        if direction == -1: #Holder spilleren på grå platform når kameraet går ned
            
            self.player.pos.y = HEIGHT-self.groundHeight+ self.posShift
        else: #Holder spilleren på grå platform når kameraet går opp
            
            self.player.rect.bottom, self.player.pos.y = -self.groundHeight + self.posShift,-self.groundHeight + self.posShift
            self.player.vel.y = 0
        
        if (self.posShift >= HEIGHT and direction ==1) or (self.posShift <= 0 and direction == -1): #Sjekker om skjermen er scrollet nok
            self.scrollTo = None 


    def drawFace(self,plat): #Tenger ansikt på platformen
        if plat.face != False:
            self.screen.blit(plat.face, plat.faceImage) #Tegner ansiktet

    def drawText(self, text, size, color, pos, fromWhere = 'center'): #funksjon for å lage text
        font = pg.font.Font(self.fontName, size)
        textSurface = font.render(text, True, color)
        textRect = textSurface.get_rect()
        #Bestem hvor posisjonen skal regnes utifra
        if fromWhere == 'center':
            textRect.center = (pos) #Posisjon regnet fra midten
        elif fromWhere == 'topleft':
            textRect.topleft = (pos) #Posisjon regnet fra øverst til venstre
        
        self.screen.blit(textSurface, textRect) #tegner teksten til skjermen
    
            

g = Game() # lager en forekomst av game-classen
while g.running:
    g.new() #gamet reseter nødvendige variabler hver gang man faller ned
    
with open(path.join(g.dir, PLAYER_DATA), 'w') as f: #lagrer highscore
    f.write(str(g.highScore))
    f.close()

#lukker pygame
pg.quit()
sys.exit()
    