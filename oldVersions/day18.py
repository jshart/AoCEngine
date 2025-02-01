from enum import Enum, auto
import time
import random
import re
import math
from collections import defaultdict
import pygame
import sys
import networkx as nx
import pygame.freetype


class SystemConfig:
    def __init__(self):
        self.sw=800 # screen width
        self.sh=600 # screen height
        self.gs=1
        self.screenCaption="Day18"
        self.frameRate=5 # currently unused
        self.dataPath=self.screenCaption+"/data"
        self.drawEmoji=False
        self.drawRects=False
        self.drawCellValues=True
        self.drawGrid=False
        self.testMode=False

        # this assumes that the matrix is one character per cell
    def simpleMatrixLoad(self, filehandle):
        lines = filehandle.readlines()

        # we calculate the longest line len, as sometimes
        # the load may encounter different length rows if
        # everything is whitespaced correctly with trailing
        # white space
        maxLine=0
        for i,l in enumerate(lines):
            lines[i]=l.rstrip("\n")
            print(len(l),": [",lines[i],"]")
            maxLine=max(maxLine, len(lines[i]))

        matrix = Matrix(maxLine, len(lines))
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                matrix.cells[y][x].value = c
        return matrix

    def simpleCoordsLoad(self, filehandle):
        lines=filehandle.readlines()
        coords=[]
        for l in lines:
            nums=extract_numbers(l.strip())
            coords.append((nums[0],nums[1]))

        return coords

# Simple enum to track compass directions
# TODO - NE,NW,SE,SW not fully implemented yet as not had a need
class CompassDirection(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3
    NORTHEAST = 4
    NORTHWEST = 5
    SOUTHWEST = 6
    SOUTHEAST = 7

    def asciiToCompassDirection(self,c):
        if c=='^':
            return CompassDirection.NORTH
        elif c=='v':
            return CompassDirection.SOUTH
        elif c=='>':
            return CompassDirection.EAST
        elif c=='<':
            return CompassDirection.WEST
        else:
            return None
        
    def turnRight(self):
        if self==CompassDirection.NORTH:
            return CompassDirection.EAST
        elif self==CompassDirection.SOUTH:
            return CompassDirection.WEST
        elif self==CompassDirection.EAST:
            return CompassDirection.SOUTH
        elif self==CompassDirection.WEST:
            return CompassDirection.NORTH
        else:
            return None
        
    def turnLeft(self):
        if self==CompassDirection.NORTH:
            return CompassDirection.WEST
        elif self==CompassDirection.SOUTH:
            return CompassDirection.EAST
        elif self==CompassDirection.EAST:
            return CompassDirection.NORTH
        elif self==CompassDirection.WEST:
            return CompassDirection.SOUTH
        else:
            return None

    def turn180(self):
        if self==CompassDirection.NORTH:
            return CompassDirection.SOUTH
        elif self==CompassDirection.SOUTH:
            return CompassDirection.NORTH
        elif self==CompassDirection.EAST:
            return CompassDirection.WEST
        elif self==CompassDirection.WEST:
            return CompassDirection.EAST
        else:
            return None        

    def getMovementDelta(self):
        if self==CompassDirection.NORTH:
            return (0,-1)
        elif self==CompassDirection.SOUTH:
            return (0,1)
        elif self==CompassDirection.EAST:
            return (1,0)
        elif self==CompassDirection.WEST:
            return (-1,0)
        else:
            return None
        


# Node weights are used to aid in the calculation of shortest paths as
# it gives us the ability to track weights and costs of computed
# paths
class NodeWeights:
    def __init__(self):
        self.direction=CompassDirection.NORTH
        self.weight=-1 #unitialised value

    def update(self, weight):
        ret=False
        if self.weight==-1:
            # first visit, just overwrite
            self.weight=weight
            ret=True
        else:
            # already visited, take the minimum
            # NOTE - if you want to find all equally good
            # paths, you need to set this to >= however
            # if there are "open" areas this can generate
            # a lot of paths.
            if self.weight>weight:
                self.weight=weight
                ret=True
            else:
                ret=False
        
        return ret

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
    def __init__(self, x, y, w, h, d, c):
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.direction=d
        self.c=c
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

    def print(self):
        print("Sprite at:", self.x, self.y, "with direction:", self.direction, "Completed:", self.locationHistory.completed)


# A common action needed on the matrix is to record a path through the map/matrix.
# One example would be for searching from a start to an end location.
class Path:
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.path=[]
        self.path.append((x,y))
        #print("Path created at:", x, y, "with direction:", direction)
        self.completed=False
        self.cost=0
        self.directionChanges=0
        self.steps=0
        self.targetSet=False
        self.targetX=0
        self.targetY=0

    def __lt__(self,other):
        # choose the return condition depending on if you want to focus on
        # minimum cost so far or minimum distance to target so far
        #return self.cost<other.cost
        return self.calcDistToTarget()<other.calcDistToTarget()

    def setTarget(self, x,y):
        self.targetSet=True
        self.targetX=x
        self.targetY=y
    
    def calcDistToTarget(self):
        return abs(self.targetX-self.x)+abs(self.targetY-self.y)
        
    def fork(self):
        newPath=Path(self.getX(), self.getY())
        newPath.path.clear()
        newPath.path=self.getPath().copy()
        newPath.cost=self.cost
        newPath.steps=self.steps
        newPath.directionChanges=self.directionChanges
        newPath.targetSet=self.targetSet
        newPath.targetX=self.targetX
        newPath.targetY=self.targetY
        return newPath

    def moveTo(self, dest, destChar):
        self.x=dest[0]
        self.y=dest[1]
        self.cost+=1

        self.steps+=1

        self.path.append((self.x, self.y))
        # Add exit conditions for the search here
        # add a len(self.path)>x check here to limit
        # the number of steps a path can take
        #if destChar=='E' or len(self.path)>50:
        if destChar==' ':
            #print("Destination reached")
            self.completed=True

    def nextStepCost(self):
        s=self.cost+1
        return s

    def validNextSteps(self, m, w):
        vns=[] # valid next steps
        #print("Path so far:",self.path)
        #print("Checking Valid steps from Current position:", self.x, self.y)   

        pns=[] # any possible next steps
        pns=m.check4Neighbours(self.x, self.y)

        for ns in pns:
            if ns==None:
                continue
            if m.getCell(ns.x,ns.y).value!='#':
                # if this potential path has a cheaper cost than the current
                # cheapest weight for this cost/direction combo we will allow
                # it, if its more expensive then we drop it as it can never
                # get to a more optimal path than some other path that already
                # visited this site at a cheaper cost
                if w[ns.y][ns.x].update(self.nextStepCost()):
                    vns.append((ns.x, ns.y,m.cells[self.x][self.y].directionToCell(ns.x,ns.y)))


        # if any of these nodes have already been visited in this path
        # we need to ignore it, so check if any of these vns entries are in the list so far
        # if they are, remove them from the list
        #print("---> Candidates:",vns)
        for p in self.path:
            for v in vns:
                if v[0]==p[0] and v[1]==p[1]:
                    #print("---> Removing:", v)
                    vns.remove(v)

        #print("Returning vns:",vns)
        return vns

    def getDirection(self):
        return self.direction

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getPath(self):
        return self.path

    def setDirection(self, direction):
        self.direction=direction

    def __str__(self):
        return f"Path: {self.x}, {self.y} to {self.targetX}, {self.targetY}: {self.path}"
    
# SearchSpace object provides us a way to track the current state of
# a search algorthim such as A*. This holds all of the partial or
# completed paths we've tested so far. Each call to this will progress
# the search, by doing "steps" this way, we can draw the intermediate
# state of the search as it progresses
class SearchSpace:
    def __init__(self, m, sp, h, w):
        self.width=w
        self.height=h
        self.map=m
        self.searchPaths=sp
        self.completedPaths=[]
        self.badPaths=[] # detours or deadends - we calculate these anyway so may as well save them
        self.nodeWeights=[]
        self.initNodeWeights(sp[0])
        self.exitAfterOneComplete=False
        self.running=True

    def resetField(self,m,sp):
        self.map=m
        self.searchPaths=sp
        self.completedPaths=[]
        self.badPaths=[]
        self.nodeWeights=[]
        self.initNodeWeights(sp[0])
        self.running=True

    # TODO - consider reworking the NodeWeights so that X/Y are abstracted and represented the right way round
    def initNodeWeights(self,p):
        for y in range(0, self.height):
            self.nodeWeights.append([])
            for x in range(0, self.width):
                self.nodeWeights[y].append(NodeWeights())

        self.nodeWeights[p.getY()][p.getX()].update(p.cost)
        print("Weight nodes init'd")

    def update(self):

        #print("Update")
        newSearchPaths=[]
        if len(self.searchPaths)>0:
        # for s in self.searchPaths:

            # grab the first preferred path (e.g. for A* this will be the one closest to our target)
            s=self.searchPaths.pop(0)

            # if this path has already been completed, move it to the
            # completed path list and move on
            if s.completed==True:
                self.completedPaths.append(s)
                if self.exitAfterOneComplete==True:
                    # if we're set to stop after we found one complete path
                    # lets just clear the searchPaths so the code doesn't
                    # have anything to re-enter with and we'll move to the
                    # finalise process

                    self.searchPaths.clear()
                return

            # calculate all the valid next steps we could take from this path
            validMoves=s.validNextSteps(self.map,self.nodeWeights)

            # for each candidate validMove, we need to fork the path and copy the
            # path so far, then add 1 of the new validMoves to the newSearchPaths
            if len(validMoves)==0:
                #print("No valid moves")
                # nothing could be done further with this path so we simply return
                # the bad path has already been popped from the seach paths so 
                # nothing further will happen with that path, we simply wait
                # to re-enter the function and will look at the next path

                # for this puzzle only, this should be marked as a completed path
                # as we can't get anywhere from here
                s.completed=True
                self.badPaths.append(s)
                return
            
            elif len(validMoves)==1:
                #print("Only one valid move")
                v=validMoves[0]
                s.moveTo(v, self.map.getCell(v[0],v[1]).value)
                #s.moveTo(v, self.map[v[1]][v[0]])

                newSearchPaths.append(s)
            else:
                print("Forking:",len(validMoves))
                for v in validMoves:
                    newPath=s.fork()
                    #newPath.moveTo(v,self.map[v[1]][v[0]])
                    newPath.moveTo(v, self.map.getCell(v[0],v[1]).value)

                    newSearchPaths.append(newPath)

        # bring over any untouched paths and then resort the list
        newSearchPaths.extend(self.searchPaths)
        self.searchPaths=sorted(newSearchPaths)

    def finalise(self):
        print("Finalising...")
        if self.searchPaths==[]:
            self.running=False
            count=0
            for c in self.completedPaths:
                print("Completed path:", c.cost)
                count+=len(c.path)

            subList=[]
            for c in self.completedPaths:
                t=(c.cost, c.directionChanges, c.steps,c)
                subList.append(t)


            # sort the list by cost
            sortedList=sorted(subList, key=lambda x: x[0])

            uniqueStops=set()
            for c in self.completedPaths:
                # is this a lowest cost path?
                if c.cost==self.completedPaths[0].cost:
                    for p in c.getPath():
                        uniqueStops.add((p[0], p[1]))
            
            print("Num Unique stops:", len(uniqueStops))
            self.forceFinalDraw=True


# track any one cell (x/y) location a matrix
class Cell:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.color = (0, 0, 0)
        self.value=value
        self.payload=None

    def __str__(self):
        return f"Cell: {self.x}, {self.y}, {self.value}"
    
    def directionToCell(self, nx, ny):
        # TODO - I need to add the diagonal NE/NW/SE/SW
        # here, need to add them first as they are the combo
        # of both nx/ny being differnt to x/y
        if nx > self.x:
            return CompassDirection.EAST
        elif nx < self.x:
            return CompassDirection.WEST
        elif ny > self.y:
            return CompassDirection.SOUTH
        elif ny < self.y:
            return CompassDirection.NORTH
        else:
            return None

# This is a 2D matrix (map or table) to track any cells and related processing for the display
class Matrix:
    def __init__(self, width, height, defaultValue='.'):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y, defaultValue) for x in range(width)] for y in range(height)]

    def print(self):
        for row in self.cells:
            for cell in row:
                print(cell.value, end='')
            print()

    def getCell(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[y][x]
    
    # return a specific row
    def getRow(self,r):
        return(self.cells[r])

    def setCell(self, x, y, value):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        self.cells[y][x].value = value

    # value can typically be a single char e.g. find "S"
    # or if value is a string, we'll return the next instance
    # of a value that matches any char in that string
    def findAllCharMatchesInString(self, value):
        retval=[]
        for x in range(0, self.width):
            for y in range(0, self.height):
                if self.getCell(x,y).value in value:
                    retval.append((x, y))
        return retval


    def check8Neighbours(self, x, y):
        neighbours = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbours.append(self.getCell(x + dx, y + dy))
        return neighbours
    
    def check4Neighbours(self, x, y):
        neighbours = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbours.append(self.getCell(x + dx, y + dy))
        return neighbours
    
    def duplicate(self):
        new_matrix = Matrix(self.width, self.height)
        for y, row in enumerate(self.cells):
            for x, cell in enumerate(row):
                new_matrix.cells[y][x].value = cell.value
        return new_matrix
    
    def count(self, value):
        count = 0
        for row in self.cells:
            for cell in row:
                if cell.value == value:
                    count += 1
        return count

    # TODO - untested    
    def rotateRowLeft(self,rowIndex,times):
        for _ in range(times):
            self.cells[rowIndex]=[self.cells[rowIndex][1:]] + self.cells[rowIndex][0]


    def rotateRowRight(self,rowIndex,times):
        for _ in range(times):
            self.cells[rowIndex]=[self.cells[rowIndex][-1]] + self.cells[rowIndex][:-1]

    def setArea(self,x,y,w,h,value):
        for cellx in range(x,x+w):
            for celly in range(y,y+h):
                self.setCell(cellx,celly,value)

    def rotateColumnDown(self, columnIndex,times):
        arr=[self.cells[i][columnIndex] for i in range(self.height)]
        for _ in range(times):
            arr=[arr[-1]] + arr[:-1]
        for i in range(self.height):
            self.cells[i][columnIndex]=arr[i]

    # TODO - untested
    def rotateColumnUp(self, columnIndex,times):
        arr=[self.cells[i][columnIndex] for i in range(self.height)]
        for _ in range(times):
            arr=arr[1:] + [arr[0]]
        for i in range(self.height):
            self.cells[i][columnIndex]=arr[i]   

    def manhattenDistance(self, start, end):
        # calculcate the manhatten distance between two points
        return abs(start[0]-end[0])+abs(start[1]-end[1])


    def extendMatrixAllDirections(self,n):
        # create the new matric with the size we want
        newWidth=self.width+(n*2)
        newHeight=self.height+(n*2)
        newMatrix=Matrix(newWidth, newHeight)

        # Copy the exiting matrix over into the new bigger matrix
        for y in range(0, self.height):
            for x in range(0, self.width):
                newMatrix.setCell(x+n, y+n, self.getCell(x, y).value)

        return newMatrix
    
    # this function adds n rows to the matrix only at the bottom of the matrix
    # effectively making it longer
    def extendMatrixBottom(self, n):
        # Create the new matrix with the size we want
        newHeight=self.height+n
        newMatrix=Matrix(self.width, newHeight)

        # Copy the existing matrix over into the new bigger matrix
        for y in range(0, self.height):
            for x in range(0, self.width):
                newMatrix.setCell(x, y, self.getCell(x, y).value)

        return newMatrix


    # this floodfill simply collects all points within a maxdist distance
    # of the start point. Will stop at a manhatten distance of maxDist from
    # start, or if we specify (and then encounter) a "stopChar"
    def floodFill(self, map, startp, p, visitedPoints, maxDist=0, stopChar=None):

        # if we've run out of spaces to explore then return an empty set
        #if self.manhattenDistance(startp,p)>=19 or map[p[1]][p[0]]=='#':
        if self.manhattenDistance(startp,p)>=maxDist-1:
            return set()
            
        # once we calculated all of the possible short
        # cut locations, we need to record it in a list
        # so we can return it
        deltas=(-1,0),(+1, 0),(0, -1),(0, +1)
        x=0
        y=0
        

        for d in deltas:
            # for this path location, we need to check the n,s,e,w locations
            # to see if it is a wall.
            x=p[0]+d[0]
            y=p[1]+d[1]

            #print("Deltas:",d,d[0],d[1])

            # need to check if the y/x co-ords are in bounds (note also there is no
            # need to check the edge as there is a wall border around the grid)
            #print("Checking boundaries, max X/Y:",len(map[0]),len(map))
            if x>=0 and x<self.width and y>=0 and y<self.height:

                # is this location already in the visited list?
                if (x, y) not in visitedPoints:

                    # its not in the visited list - but lets also make
                    # sure this isnt a border/stop char. if it is, then
                    # we just skip this and check any other deltas
                    if stopChar!=None:
                        if self.getCell(x,y).value==stopChar:
                            continue

                    visitedPoints.add((x,y))

                    #print("[", remainingSteps,"]",end="")
                    #pad="-"*(20-remainingSteps)
                    #print(pad,end=">")
                    #print("new loc:", x, y)
                    visitedPoints|=self.floodFill(map, startp, (x, y), visitedPoints, maxDist, stopChar)
            else:
                #print("Out of bounds:", x, y)
                pass
 
        return visitedPoints
    
    # This function can be rewritten as needed, the intent is to provide a way
    # to "summarise" the current matrix status as a hash ready for comparison
    # with a previous matrix status. This is useful for detecting when the
    # matrix has stopped changing and we can stop processing
    def matrixHash(self):
        hashString=""
        for y in range(self.height):
            for x in range(self.width):
                hashString=hashString+self.getCell(x, y).value
        return hashString

    # for cellular automata it is useful to create a new matrix with some custom
    # rules applied to the current matrix. Typically we want to walk the current
    # matrix, checking the state of each cell and its neighbours, and then setting
    # a value in a new matrix. Once we've built the new matrix we return it
    def cellularAutomata(self, defaultValue=' '):
        newMatrix=Matrix(self.width, self.height, defaultValue)

        for y in range(self.height):
            for x in range(self.width):
                nValues=[]
                neighbours=self.check8Neighbours(x, y)
                for n in neighbours:
                    if n==None:
                        continue
                    nValues=nValues+[n.value]
                # *** this the custimisation area where we can put in our specific rules
                # *** this cellular automata

                # what is the state of this cell? We need fetch the current cell value
                # and then we need to count the number of neighbours that are also active
                # so we can apply our rules
                cellValue=self.getCell(x,y).value

                # add this to the newMatric
                newMatrix.setCell(x, y, self.getCell(x,y).value)

                # End custom rules

        return newMatrix

class HashTracker:
    def __init__(self):
        self.count = 0
        self.hash = dict()
    
    def add(self, hash):
        # does this already exist in the dict?
        if hash in self.hash:
            self.hash[hash] += [self.count]
            self.count += 1
            return(self.hash[hash])
        else:
            self.hash[hash] = [self.count]
            self.count += 1
            return(None)
    

# This is a 2D matrix (map or table) to track any cells and related processing for the display
class Display:
    def __init__(self, sc, screen):
        self.sc = sc
        self.width = sc.sw
        self.height = sc.sh 
        self.screen = screen
        self.matrixDrawWindow = (0,0,sc.sw//sc.gs,sc.sh//sc.gs)

        # common emoji
        self.brickWall="🧱"
        self.tree="🌲"
        self.wood="🪵"
        self.plant="🌱"
        self.grass="🟩"
        self.sick="🤢"

    def isInDrawWindow(self,x,y):
        if x>=self.matrixDrawWindow[0] and x<self.matrixDrawWindow[2] and y>=self.matrixDrawWindow[1] and y<self.matrixDrawWindow[3]:
            return True
        return False
    
    # This adjusts all of the sizing parameters to deal with the fact that the screen has changed
    # size and/or position
    def adjustDrawWindow(self, sc, x, y, matrixSF):
        global font

        # Set the new scale factor - TODO - think about if we want to put any boundary checks on the size of this
        self.sc.gs+=matrixSF
        self.sc.gs=1 if self.sc.gs<1 else self.sc.gs
        sc.gs=self.sc.gs


        # Adjust the draw window start positions based on the new delta (+/-1 for x or y)
        x=self.matrixDrawWindow[0]+x
        y=self.matrixDrawWindow[1]+y

        # if x or y are negative after the adjustment, reset them to 0 as we dont want to move past the
        # upper left corner of the matrix
        x=max(0, x)
        y=max(0, y)

        # TODO - this chunk of code is broken (hence commented out) as it needs more knowledge about the matrix
        # sizing, so for now we just allow the display to draw "empty space" beyond the edge of the screen
        # whats the max number of matrix cells we can fit into our display window (divide by the scaling factor)
        matrixMaxXCells=self.width//self.sc.gs
        matrixMaxYCells=self.height//self.sc.gs
        # we now want to make sure that the furthest right or down we go is to the point where we would
        # draw the last cell of the matrix. So we need to calculate the max x and y values that we can draw
        # based on the current scaling factor and the size of the matrix
        # x=min(x,(self.width-matrixMaxXCells))
        # y=min(y,(self.height-matrixMaxYCells))


        # OK now we're comfortable with the boundary/edge cases being taken care of lets reset our draw window
        self.xMatrixDrawOffset = x
        self.yMatrixDrawOffset = y

        # note that matrixMaxX/Y are the max number we *could* draw
        # but we may not have enough cells to draw all of these, so
        # whenever we draw we need to factor in we need to stop at the
        # matrix end
        self.matrixDrawWindow = (x, y, x+matrixMaxXCells, y+matrixMaxYCells)

        #print("Setting Draw Window to:",self.matrixDrawWindow)
        font = pygame.font.SysFont('Segoe UI Emoji', self.sc.gs) # emoji capable font

    def drawSprites(self, sc, sprites):
        for sprite in sprites:
            sx1=(sprite.x-self.matrixDrawWindow[0])*sc.gs
            sy1=(sprite.y-self.matrixDrawWindow[1])*sc.gs

            if sc.drawRects:
                pygame.draw.rect(screen, sprite.c, pygame.Rect(sprite.x*sc.gs, sprite.y*sc.gs, sprite.w, sprite.h))
            if sc.drawEmoji:
                screen.blit(font.render(sprite.emoji, True, sprite.c), (sx1, sy1))

    def drawPathToScreen(self, sc, path,lColor=(255,0,0)):
        for p in range(0, len(path)-1):
            # for each box in turn, lets draw a line from the centre of that box to the centre of the next box
            # in the pathSofar
            if self.isInDrawWindow(path[p][0], path[p][1])==False:
                continue
 
            px1=(path[p][0]-self.matrixDrawWindow[0])*sc.gs
            py1=(path[p][1]-self.matrixDrawWindow[1])*sc.gs
            px2=(path[p+1][0]-self.matrixDrawWindow[0])*sc.gs
            py2=(path[p+1][1]-self.matrixDrawWindow[1])*sc.gs  

            pygame.draw.line(self.screen, lColor, (px1+sc.gs/2, py1+sc.gs/2), (px2+sc.gs/2, py2+sc.gs/2), 2 )

    def drawMatrixToScreen(self, sc, matrix):
        for matrixY in range(self.matrixDrawWindow[1], self.matrixDrawWindow[3]):
            for matrixX in range(self.matrixDrawWindow[0], self.matrixDrawWindow[2]):
                screenX = (matrixX - self.matrixDrawWindow[0]) * sc.gs
                screenY = (matrixY - self.matrixDrawWindow[1]) * sc.gs
                cell = matrix.getCell(matrixX, matrixY)
                if cell is not None:
                    #pygame.draw.rect(self.screen, cell.color, (screenX, screenY, sf, sf))

                    if cell.value=="#": # infected
                        if sc.drawRects:
                            pygame.draw.rect(self.screen, (255,255,0), (screenX, screenY, sc.gs, sc.gs))
                            #pygame.draw.rect(self.screen, (255, 255, 255), (screenX, screenY, sc.gs, sc.gs), 1)
                        if sc.drawEmoji:
                            #text_surface = font.render(self.brickWall, True, (255, 255, 0))
                            text_surface = font.render(self.sick, True, (255, 255, 0))
                            self.screen.blit(text_surface, (screenX, screenY))
                    elif cell.value=="o": # weakened
                        if sc.drawRects:
                            pygame.draw.rect(self.screen, (125, 125, 125), (screenX, screenY, sc.gs, sc.gs))
                            #pygame.draw.rect(self.screen, (255, 255, 255), (screenX, screenY, sc.gs, sc.gs), 1)
                    elif cell.value=="@":
                        if sc.drawRects:
                            pygame.draw.rect(self.screen, (125, 0, 0), (screenX, screenY, sc.gs, sc.gs))
                            #pygame.draw.rect(self.screen, (255, 255, 255), (screenX, screenY, sc.gs, sc.gs), 1)
                        if sc.drawEmoji:
                            text_surface = font.render(self.tree, True, (255, 255, 0))
                            self.screen.blit(text_surface, (screenX, screenY))
                    elif cell.value==".": # Clean
                        # if sc.drawEmoji:
                        #     text_surface = font.render(self.grass, True, (0, 255, 0))
                        #     self.screen.blit(text_surface, (screenX, screenY))
                        pass

                    if sc.drawCellValues:
                        #if cell.value!=".":
                        v=cell.value
                        # because we maybe storing ints in the matrix, we need to check if we need to map them to a str first
                        v = v if type(cell.value) == str else str(cell.value)
                        text_surface = font.render(v, True, (255, 255, 255))
                        self.screen.blit(text_surface, (screenX, screenY))

    def drawGridOnMatrix(self, sc, matrix):
        for y in range(0, matrix.height):
            for x in range(0, matrix.width):
                pygame.draw.rect(self.screen, (255, 255, 255), (x*sc.gs, y*sc.gs, sc.gs, sc.gs), 1)

    def processCommands(self, sc, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.adjustDrawWindow(sc, -1, 0, 0)
            elif event.key == pygame.K_RIGHT:
                self.adjustDrawWindow(sc, +1, 0, 0)
            elif event.key == pygame.K_UP:
                self.adjustDrawWindow(sc, 0, -1, 0)
            elif event.key == pygame.K_DOWN:
                self.adjustDrawWindow(sc, 0, +1, 0)
            elif event.key == pygame.K_EQUALS:
                self.adjustDrawWindow(sc, 0, 0, +1)
            elif event.key == pygame.K_MINUS:
                self.adjustDrawWindow(sc, 0, 0, -1)
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def updateDisplay(self,sc, m=None, bps=None, cps=None, runs=0, sprites=None):
        # Update the display
        self.screen.fill((0, 0, 0))  # Fill the screen with black (or any other color)



        # draw the screen
        if m!=None:
            display.drawMatrixToScreen(sc, m)

        if sc.drawGrid:
            self.drawGridOnMatrix(sc, m)

        if bps!=None:
            for p in bps:
                #draw path p
                display.drawPathToScreen(sc, p.path, (255, 0, 0))
        if cps!=None:
            for p in cps:
                #draw path p
                display.drawPathToScreen(sc, p.path, (0, 255, 0))

        if sprites!=None:
            display.drawSprites(sc, sprites)

        if runs>0:
            text_surface = font.render("Runs: "+str(runs), True, (255, 255, 255))
            self.screen.blit(text_surface, (0, 0))

        pygame.display.flip()  # Refresh the display



# Useful utility function to regex match and/all numbers in a line
# handy for quick and dirty parsing of the input data
def extract_numbers(s):
    return [int(num) for num in re.findall(r'-?\d+', s)]

def decimalToAlphabeticLabel(n):
    if n == 0:
        return "A"
    
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = []
    
    while n > 0:
        n, remainder = divmod(n, 26)
        result.append(alphabet[remainder])
    
    return ''.join(reversed(result))


sc=SystemConfig()

part2=False
if sc.testMode:
    file1 = open(sc.dataPath+'/input_test2.txt', 'r')
    matrixExtend=10-1
    sc.gs=30
else:
    file1 = open(sc.dataPath+'/input.txt', 'r')
    matrixExtend=40-1
    sc.gs=15

matrix=sc.simpleMatrixLoad(file1)
matrix=matrix.extendMatrixBottom(matrixExtend)
matrixIndex=0

trapPatterns=["^^.",".^^","^..","..^"]
    
if part2:
    maxRuns=600
else:
    maxRuns=10


# **** Puzzel specific setup code

# **** End of puzzle specific setup code


# create a pygame window
pygame.init()
sc.sw=matrix.width * sc.gs
sc.sh=matrix.height * sc.gs
screen = pygame.display.set_mode((sc.sw, sc.sh))
pygame.display.set_caption(sc.screenCaption+" M: "+str(matrix.width)+"x"+str(matrix.height))
#font = pygame.font.Font(None, scaleFactor)
font = pygame.font.SysFont('Segoe UI Emoji', sc.gs) # emoji capable font
display = Display(sc, screen)
# end standard pygame setup code





# Main game loop - will repeatedly draw whilst the running flag
# is set and the maxRuns (iterations) limit has not been hit.
# Adjust either exit condition to suit. Can also put into an infinite
# loop and rely on user hitting the window close button which will be
# caught with the pygame QUIT event
running = True
runs=0
maxRuns=matrixExtend
while running and runs<maxRuns:
#while running:
    for event in pygame.event.get():
        display.processCommands(sc, event)

    #if runs%100000==0:
    display.updateDisplay(sc, matrix, runs=0)
    #time.sleep(1/sc.frameRate) # now sleep for 0.25 seconds

    # lets take a copy of the current row (matrixIndex), and add a "." to the start and
    # end of that copy
    rowCopy=matrix.getRow(matrixIndex).copy()
    # add a '.' to the start and end
    rowCopy.append(Cell(0,0,'.'))
    rowCopy.insert(0,Cell(0,0,'.'))
    sampleRange=3
    nextTileIndex=0
    for i in range(len(rowCopy)-sampleRange+1):
        # next sampleRange characters as a substring:
        sample=""
        for s in range(i, i+sampleRange):
            sample+=rowCopy[s].value
        
        print(sample,"->", (sample in trapPatterns), "Set at:",nextTileIndex,matrixIndex+1)
        if sample in trapPatterns:
            matrix.setCell(nextTileIndex, matrixIndex+1, '^')
        else:
            matrix.setCell(nextTileIndex, matrixIndex+1, '.')
        nextTileIndex+=1

    matrixIndex+=1

    # print out the run and payload status
    #if runs%100000==0:
    print("Run:", runs)  


    runs+=1

# Puzzle specific results - print out key counters here
print("Final Run:", runs)  
print("Final Matrix safe count:",matrix.count('.'))

running=True

# if we exited the previous loop due to the run count, we now just sit with the
# window open/idle waiting to be closed. This allows us to see the final state
# of the display after completing the puzzle.
while running:

    for event in pygame.event.get():
        display.processCommands(sc, event)

    # update the display
    display.updateDisplay(sc, matrix, runs=0)

# Clean up and exit
pygame.quit()


# box unicode chars; https://en.wikipedia.org/wiki/Box_Drawing


# Need to rework this to *not* use the matrix for part2. instead we should simply;
# 1) count the number of safe tiles on *This* row.
# 2) calculate the next row.
# 3) swap the rows
# 4) repeat