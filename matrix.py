import random
from compass import *
from sprite import *


# track any one cell (x/y) location a matrix
class Cell:
    # this dictionary class var (shared by all instances of cell) is used
    # to define rules for what valid next states (cell values) a cell
    # may have. We lookup using the key, and it returns a list of allowable
    # options
    validTransitions = {True:[False],False:[True]}

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.colour = (0, 0, 0)
        self.value=value
        self.payload=None

    def setColour(self,c):
        self.colour=c

    def __str__(self):
        return f"Cell: {self.x}, {self.y}, {self.value}"
    
    # check the valid transitions based on current value
    def checkValidTransitions(self):
        if self.value in Cell.validTransitions:
            return Cell.validTransitions[self.value]
        else:
            return None

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
    
    # Creates a duplicate of this cell and returns the copy
    def copy(self):
        c=Cell(self.x, self.y, self.value)
        c.colour=self.colour
        c.payload=self.payload
        return c
    
    # sets this cell to the contents of cell 'c'
    # this effectively overwrites this cell with whatever is in 'c'
    def set(self,c):
        self.x=c.x
        self.y=c.y
        self.value=c.value
        self.colour=c.color
        self.payload=c.payload
    

# TODO - re-coded all the code that deals with copy whole or part matrices to copy the entire
# cell and not just the value. However this is mostly untested in this version of the code,
# so keeping this note to remind me that there maybe bugs (refer to older versions of 2018/day11.py to see old tested code if needed for debug)
# This is a 2D matrix (map or table) to track any cells and related processing for the display
class Matrix:
    def __init__(self, width, height, defaultValue='.', csw=1, csh=1):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y, defaultValue) for x in range(width)] for y in range(height)]
        self.cellSizeW = csw
        self.cellSizeH = csh
        self.spriteManager = SpriteManager()

        self.mouseClickHandler=None

        # These values are just used to track the min and max values currently in the matrix
        self.minCellValue=0
        self.maxCellValue=0
        self.numberFound=False
        # TODO - could also add a automatic total function, by keeping a class member
        # containing the total, and update setCell to dec old value and add new value
        # just need to make sure we're always working with ints

    def registerMouseClickHandler(self, func):
        self.mouseClickHandler=func

    def defaultMouseClickHandler(self, cellx, celly):
        print("Default mouse click handler called for:", cellx, celly)
        # check to see if this cell has a valid next transition
        # if so, then update the cell value
        validTransitions=self.cells[celly][cellx].checkValidTransitions()
        if validTransitions!=None:
            #print("Valid transitions:", validTransitions)
            self.cells[celly][cellx].value=validTransitions[0]
            self.cells[celly][cellx].color=(255, 0, 0)

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
    
    def setAllTo(self,value):
        for y in range(0, self.height):
            for x in range(0, self.width):
                self.setCellValue(x, y, value)

    # TODO - think about if this is "pure" by being at this level - should I really
    # allow a matrix level function to set a cell velue, or should I push this
    # down to the cell. The only real difference is that the indices come out
    # of the paramters and got on the cells var i.e. shoudl this be
    # matrix.setCellValue(0,0,0)
    # or
    # matrix.cells[0][0].setValue(0)
    def setCellValue(self, x, y, value):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        self.cells[y][x].value = value

        if isinstance(value,int):
            value=int(value)
            if self.numberFound==False:
                self.numberFound=True
                self.minCellValue=value
                self.maxCellValue=value
                print("lerp: first number found is:",value)
            else:
                if value < self.minCellValue:
                    self.minCellValue=value
                if value > self.maxCellValue:
                    self.maxCellValue=value

    def getCellValue(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None
        return self.cells[y][x].value

    def randomiseMatrix(self,min,max):
        for y in range(0, self.height):
            for x in range(0, self.width):
                self.setCellValue(x, y, random.randint(min, max))

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
                new_matrix.cells[y][x].set(cell)
        return new_matrix
    
    def count(self, value):
        count = 0
        for row in self.cells:
            for cell in row:
                if cell.value == value:
                    count += 1
        return count
    
    # customise this function to look for cells that match
    # a specific condition
    def cellsMatchCondition(self, value):
        candidates=[]
        for row in self.cells:
            for cell in row:
                count = 0
                if cell.value == value:
                    neighbours = self.check4Neighbours(cell.x, cell.y)
                    for n in neighbours:
                        if n is not None:
                            if n.value == value:
                                count += 1
                    if count >= 3:
                        candidates.append((cell.x, cell.y))

        return candidates

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
                self.setCellValue(cellx,celly,value)

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
                newMatrix.cells[x+n, y+n].set(self.getCell(x, y))

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
                newMatrix.cells[x, y].set(self.getCell(x, y))

        return newMatrix

    # this function takes a copy of a sub-matrix out of the main matrix using
    # the x1,y1 to x2,y2 co-ords of the rect area of interest
    def subMatrix(self, x1, y1, x2, y2):
        # Create the new matrix with the size we want
        newWidth=x2-x1+1
        newHeight=y2-y1+1
        newMatrix=Matrix(newWidth, newHeight)

        # Copy the existing matrix over into the new bigger matrix
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                newMatrix.cells[x-x1][y-y1].set(self.getCell(x, y))

        return newMatrix
    
    # Calculate the total of values in the matrix
    def total(self):
        total=0
        for y in range(0, self.height):
            for x in range(0, self.width):
                total+=self.getCell(x, y).value
        return total
    
    def totalSubMatrix(self,x1,y1,x2,y2):
        total=0
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                total+=self.getCell(x, y).value
        return total

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
                newMatrix.setCellValue(x, y, self.getCell(x,y).value)

                # End custom rules

        return newMatrix

