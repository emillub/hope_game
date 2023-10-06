import sys, os

def getworkingpath():          
    pathname = os.path.dirname(sys.argv[0])    
    return os.path.abspath(pathname)