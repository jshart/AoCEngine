import tkinter as tk
from enum import Enum, auto
import re
from rich import print

def extract_numbers(s):
    return [int(num) for num in re.findall(r'-?\d+', s)]

class CompassDirection(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

class NodeWeights:
    def __init__(self):
        self.direction=CompassDirection.NORTH
        self.weight=-1

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


# create a new class to track the path we are taking through the map
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
        if destChar=='E':
            #print("Destination reached")
            self.completed=True

    def nextStepCost(self):
        s=self.cost+1
        return s

    def validNextSteps(self, lines, w):
        vns=[]
        #print("Path so far:",self.path)
        #print("Checking Valid steps from Current position:", self.x, self.y)
   
        # check all 4 directions, if they are valid, add them to the list
        # if they are not valid, do nothing
        tx=self.x
        ty=self.y-1
        if lines[ty][tx]!='#':
            # if this potential path has a cheaper cost than the current
            # cheapest weight for this cost/direction combo we will allow
            # it, if its more expensive then we drop it as it can never
            # get to a more optimal path than some other path that already
            # visited this site at a cheaper cost
            if w[ty][tx].update(self.nextStepCost()):
                vns.append((tx, ty,CompassDirection.NORTH))
            #print("-->up")

        tx=self.x
        ty=self.y+1
        if lines[ty][tx]!='#':
            if w[ty][tx].update(self.nextStepCost()):
                vns.append((tx, ty,CompassDirection.SOUTH))
            #print("-->down")

        tx=self.x-1
        ty=self.y
        if lines[ty][tx]!='#':
            if w[ty][tx].update(self.nextStepCost()):
                vns.append((tx, ty,CompassDirection.WEST))
            #print("-->left")

        tx=self.x+1
        ty=self.y
        if lines[ty][tx]!='#':
            if w[ty][tx].update(self.nextStepCost()):
                vns.append((tx, ty,CompassDirection.EAST))
            #print("-->right")

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
        return f"Path: {self.x}, {self.y}, {self.direction}"
    
    
    def drawPath(self, canvas, grid_size,colour):
        for p in range(0, len(self.path)-1):
            # for each box in turn, lets draw a line from the centre of that box to the centre of the next box
            # in the pathSofar
            canvas.create_line(self.path[p][0]*grid_size+grid_size/2, self.path[p][1]*grid_size+grid_size/2, self.path[p+1][0]*grid_size+grid_size/2, self.path[p+1][1]*grid_size+grid_size/2, fill=colour, width=2)

class SearchSpace:
    def __init__(self, m, sp, h, w):
        self.width=w
        self.height=h
        self.map=m
        self.searchPaths=sp
        self.completedPaths=[]
        self.nodeWeights=[]
        self.initNodeWeights(sp[0])
        self.exitAfterOneComplete=False
        self.running=True

    def resetField(self,m,sp):
        self.map=m
        self.searchPaths=sp
        self.completedPaths=[]
        self.nodeWeights=[]
        self.initNodeWeights(sp[0])
        self.running=True

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
                return
            
            elif len(validMoves)==1:
                #print("Only one valid move")
                v=validMoves[0]
                s.moveTo(v, self.map[v[1]][v[0]])
                newSearchPaths.append(s)
            else:
                #print("Forking:",len(validMoves))
                for v in validMoves:
                    newPath=s.fork()
                    newPath.moveTo(v,self.map[v[1]][v[0]])
                    newSearchPaths.append(newPath)

        # bring over any untouched paths and then resort the list
        newSearchPaths.extend(self.searchPaths)
        self.searchPaths=sorted(newSearchPaths)

    def finalise(self):
        #print("Finalising...")
        if self.searchPaths==[]:
            self.running=False
            count=0
            for c in self.completedPaths:
                #print("Completed path:", c.cost)
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
            
            #print("Num Unique stops:", len(uniqueStops))
            self.forceFinalDraw=True



# General purpose display class
class TKDrawingSpace:
    def __init__(self, root, w, h, gs, fs, ps, ss):
        self.root = root
        self.canvas = tk.Canvas(root, width=w, height=h, bg='white')
        self.exit_button = tk.Button(root, text="Exit", command=self.on_exit)
        self.text_box = tk.Text(root, height=1, width=40)

        self.text_box.pack(pady=10)
        self.canvas.pack()
        self.exit_button.pack(pady=10)
        self.running = True
        self.forceFinalDraw=True

        self.searchSpace=ss
        self.width=w
        self.height=h
        self.grid_size=gs
        self.font_size=fs
        self.pad_size=ps

        #self.root.after(0, self.game_loop)
        self.drawBaseGrid()
        displayStr="Completed:"+str(len(self.searchSpace.completedPaths))+" Incomplete:"+str(len(self.searchSpace.searchPaths))
        self.text_box.insert(tk.END, displayStr)
    
    def on_exit(self):
        self.root.destroy()

    # use this code if you want to hand over control of the main proceessing loop to TK
    # def game_loop(self):
    #         updatesPerDraw=500
    #         i=0
    #         #print("GL called")
    #         if self.running:
    #             while i<updatesPerDraw and self.running==True:
    #                 self.update()
    #                 self.finalise()
    #                 i+=1
    #             #self.root.after(1, self.game_loop)  # Run the game loop approximately 60 times per second (1000ms / 60 ≈ 16.67ms)
    #             #self.root.after(16, self.game_loop)  # Run the game loop approximately 60 times per second (1000ms / 60 ≈ 16.67ms)
    #             #self.root.after(100, self.game_loop)  # Run the game loop approximately 60 times per second (1000ms / 60 ≈ 16.67ms)

    #         if self.running or self.forceFinalDraw:
    #             #if self.runs % self.drawFrequence==0 or self.forceFinalDraw==True:
    #             self.draw()
    #             self.forceFinalDraw=False


    def drawBaseGrid(self):
        bombCode="\U0001F4A3"
        footPrint="\U0001F463"
        guard="\U0001F46E"
        obstacle="\U0001F9F1"
        robot="\U0001F916"
        box="\U0001F4E6"
        # Clear the canvas - note this is only needed because I'm creating new stuff rather than moving tagged items around
        self.canvas.delete('all')

        # Generic grid based on size of loaded data
        for i in range(0, self.width, self.grid_size):
            self.canvas.create_line([(i, 0), (i, self.height)], tag='grid_line', dash=(1,4))
        for i in range(0, self.height, self.grid_size):
            self.canvas.create_line([(0, i), (self.width, i)], tag='grid_line', dash=(1,4))

        # Problem specific drawing code
        y=0
        x=0
        # go across (width - this is x co-ord, or the 2nd dimension of the array)
        for i in range(0, self.width, self.grid_size):
            # go down (height - this is y co-ord or the 1st dimension of the array)
            for j in range(0, self.height, self.grid_size):
 
                if self.searchSpace.map[y][x]=="#":
                    self.canvas.create_text(i + self.grid_size/2, j + self.grid_size/2, text=obstacle, font=('Arial', self.font_size),fill='brown')
                else:
                    self.canvas.create_text(i + self.grid_size/2, j + self.grid_size/2, text=self.searchSpace.map[y][x], font=('Arial', self.font_size), fill='black')

                y+=1
            x+=1
            y=0

    def draw(self):
        print("Draw called, active search count:",len(self.searchSpace.searchPaths))
        self.drawBaseGrid()

        for s in self.searchSpace.searchPaths:
            s.drawPath(self.canvas, self.grid_size,"blue")

        for s in self.searchSpace.completedPaths:
            s.drawPath(self.canvas, self.grid_size,"green")

        displayStr="Completed:"+str(len(self.searchSpace.completedPaths))+" Incomplete:"+str(len(self.searchSpace.searchPaths))
        self.text_box.delete('1.0', tk.END)
        self.text_box.insert(tk.END, displayStr)


def main():

    # Problem specific loading code etc

    testing=False

    if testing:
        file1 = open('Day18/data/input_test.txt', 'r')
        font_size=24
        pad=4
        
        width=6+1+2
        height=6+1+2
        numBytesToTest=12
    else:
        file1 = open('Day18/data/input.txt', 'r')
        font_size=10
        pad=1
    
        width=70+1+2
        height=70+1+2
        numBytesToTest=1024


    # initialise map[] to a 2 dim array the size of width and height
    map=[]
    for y in range(0, height+2):
        map.append([])
        for x in range(0, width+2):
            if x==0 or y==0 or x==width-1 or y==height-1:
                map[y].append('#')
            else:
                map[y].append('.')

    map[1][1]='S'
    map[height-2][width-2]='E'

    bytes=[]
    lines = file1.readlines()
    for l in lines:
        nums=extract_numbers(l)
        bytes.append((nums[0]+1,nums[1]+1))


    print(bytes)
    #for b in bytes:
    for i in range(0,numBytesToTest):
        b=bytes[i]
        map[b[1]][b[0]]='#'

    print(map)

    #exit(0)

    # find the start location to init our path
    for i in range(0, len(map)):
        for j in range(0, len(map[0])):
            if map[i][j]=='S':
                start=[i,j]

    searchPaths=[]
    p=Path(start[1], start[0])
    p.setTarget(width-2, height-2)
    searchPaths.append(p)

    searchSpace=SearchSpace(map, searchPaths, height, width)

    print("Map loaded W/H:", width, height)

    # Start of TK processing and game loop handling
    canvas_width = (font_size+pad) * width
    canvas_height = (font_size+pad) * height
    grid_size = font_size+pad


    root = tk.Tk()
    root.title("Grid Drawing")

    displayField=TKDrawingSpace(root, canvas_width, canvas_height, grid_size, font_size, pad, searchSpace)

    # Run once to get baseline:
    while searchSpace.running==True:
        searchSpace.update()
        searchSpace.finalise()

    currentSolution=searchSpace.completedPaths[0]
    print("Current solution path:", currentSolution.getPath())

    for block in range(numBytesToTest, len(bytes)):
        b=bytes[block]
        map[b[1]][b[0]]='#'

        if ((b[1],b[0]) in currentSolution.getPath())==False:
            print("Block", block, " not in current solution path - skipping to next iteration")
            continue

        searchPaths=[]
        p=Path(start[1], start[0])
        p.setTarget(width-2, height-2)
        searchPaths.append(p)

        searchSpace.resetField(map, searchPaths)

        # Run again to find new solution
        while searchSpace.running==True:
            searchSpace.update()
            searchSpace.finalise()

        displayField.draw()
        root.update()
        print("Tested for block=",block," co-ords",bytes[block]," remove one due to border")
        if searchSpace.completedPaths==[]:
            print("No path found")
            exit(0)
        else:
            #print("New solution path:", searchSpace.completedPaths[0].getPath())
            print("New solution path")

            currentSolution=searchSpace.completedPaths[0]


    print("Exited main search loop")
    root.mainloop()

if __name__ == "__main__":
    main()