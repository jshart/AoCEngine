from enum import Enum, auto

from compass import *

class Robot:
    def __init__(self, x, y, w, h):
        self.sprite=Sprite(x,y,w,h)
        self.sprite.setEmoji("🤖")
        self.input=None
        self.output=None
        self.locationHistory=set()

    # record the current location in the history
    # we get the location from the sprite
    def recordLocation(self):
        self.locationHistory.add(self.sprite.getLocation())

    def attachInputBuffer(self, buffer):
        self.input=buffer
    
    def attachOutputBuffer(self, buffer):
        self.output=buffer

class SpriteManager:
    def __init__(self):
        self.sprites=[]
        self.deadSprites=[]
        self.spriteMap={}

    def addSprite(self, s):
        self.sprites.append(s)
        self.spriteMap[s.ID]=s

    def getSprite(self, ID):
        return self.spriteMap[ID]

    def getSpriteAtLocation(self, x, y):
        ret=None
        for s in self.sprites:
            if s.x==x and s.y==y:
                ret=s
                break
        return ret

    def getSpriteCount(self):
        return len(self.sprites)

    def removeSprite(self, s):
        self.sprites.remove(s)
        del self.spriteMap[s.ID]

    # remove any sprites marked as dead
    def removeDeadSprites(self):
        # iterate over a copy of the list, and remove anything in the original list marked as dead
        for s in self.sprites[:]:
            if s.dead:
                # for now we actually move the sprites to a deadSprite list, incase we want to
                # recycle them or interrogate them in anyway. However we can always completely
                # clear the list seperately if we wanted to
                self.deadSprites.append(s)
                self.removeSprite(s)

    # for a given sprite, we need to check if it is at the same matrix location as any other sprite.
    # for any sprite that is at the same location, we mark all as "dead" indicating they have been in a collision
    def checkForSpriteCollisions(self, s):
        for s2 in self.sprites:
            if s2.ID!=s.ID and s2.x==s.x and s2.y==s.y:
                s.dead=True
                s2.dead=True

                # not sure if this is necessary - but for now lets mark this as processed this tick
                # so we don't process it again
                s.processedThisTick=True
                s2.processedThisTick=True

    # reset processed ticks
    def resetTicks(self):
        for s in self.sprites:
            s.processedThisTick=False

    # lets update all the sprite positions
    def updateSpriteLocations(self, m):
        for s in self.sprites:
            s.checkNextValidMoves(m)
            s.processedThisTick=True

# useful sprite emojis, 🚶‍♂️🚂
class Sprite:
    def __init__(self, x, y, w, h, d=CompassDirection.NORTH, c=(255,255,255)):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.direction=d
        self.colour=c
        self.locationHistory=Path(x, y)
        self.solution=""
        self.emoji=""
        self.state=0
        self.ID=(self.x,self.y) # Default ID is just initial location tuple, but can be over-ridden to any useful value
        self.processedThisTick=False
        self.dead=False
        self.payload=None # generic location to store any puzzle specific data we need to track on a per sprite basis.

    def setEmoji(self,e):
        self.emoji=e
        
    def updateLocation(self, destCell):
        self.x=destCell.x
        self.y=destCell.y
        self.locationHistory.moveTo((self.x, self.y), destCell.value)

    def getLocation(self):
        return (self.x, self.y)
    
    # TODO - implement some basic collision detection and behaviours?
    def checkNextValidMoves(self, m):

        #print("Checking Moves from:",self.x,self.y)
        deltaX=0
        deltaY=0
        
        # depending on what the next cell in this direction contains we
        # may need to change our direction setting.
        #v=m.getCell(self.x+deltaX, self.y+deltaY).value
        v=m.getCell(self.x, self.y).value


        if v=='#': #infected
            self.direction=self.direction.turnRight()
            m.setCell(self.x, self.y, '@') # flagged
        elif v=='o': # weakened
            m.setCell(self.x, self.y, '#') # infected
            self.payload+=1
        elif v=='@': # Flagged
            m.setCell(self.x, self.y, '.') # cleaned
            self.direction=self.direction.turn180()
        else: # Clean
            self.direction=self.direction.turnLeft()
            m.setCell(self.x, self.y, 'o') # weaken

        deltaX,deltaY=self.direction.getMovementDelta()

        # now we know where our next step is, so lets move there
        self.updateLocation(m.getCell(self.x+deltaX, self.y+deltaY))

    def setCellAtCurrentLocation(self,m,v):
        m.setCellValue(self.x, self.y, v)

    def getCellValueAtCurrentLocation(self,m):
        return m.getCell(self.x, self.y).value
    
    def turnLeft(self):
        self.direction=self.direction.turnLeft()
    
    def turnRight(self):
        self.direction=self.direction.turnRight()

    def moveForward(self):
        deltaX,deltaY=self.direction.getMovementDelta()
        self.x+=deltaX
        self.y+=deltaY

    def moveDirection(self,d):
        self.direction=d
        deltaX,deltaY=self.direction.getMovementDelta()
        self.x+=deltaX
        self.y+=deltaY

    def print(self):
        print("Sprite at:", self.x, self.y, "with direction:", self.direction, "Completed:", self.locationHistory.completed)

