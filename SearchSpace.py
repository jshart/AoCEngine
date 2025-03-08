from compass import *

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

    def longestPath(self, paths):
        longest=0
        for p in paths:
            if len(p.path)>longest:
                longest=len(p.path)
        return longest

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
