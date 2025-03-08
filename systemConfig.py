from matrix import *

class SystemConfig:
    def __init__(self):
        # Screen (i.e. pygame) level parameters
        self.sw=1000 # screen width
        self.sh=1000 # screen height
        self.frameRate=5 # currently unused

        # data load parameters
        self.screenCaption="Day17_v2"
        self.dataPath=self.screenCaption+"/data"
        self.saveName="saveMatrix.txt"

        # system control flags - configure key behaviours
        self.drawEmoji=True
        self.drawRects=False
        self.fillRects=False
        self.drawCellValues=True
        self.drawGrid=False
        self.testMode=False

        # dict of all matrices we might want to display (i.e. a matrix = a thing to display)
        self.matrices={}
        self.currentMatrix=None

        self.dummy="not set"

    # this function does a simple save of the current matrix to a file
    def simpleMatrixSave(self):
        if self.currentMatrix==None:
            return

        filehandle=open(self.dataPath+"/"+self.saveName, "w")
        for y in range(self.currentMatrix.height):
            for x in range(self.currentMatrix.width):
                filehandle.write(str(self.currentMatrix.cells[y][x].value))
            filehandle.write("\n")
        filehandle.close()

    # this assumes that the matrix is one character per cell
    def simpleMatrixLoad(self, filehandle, csw=10,csh=10):
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

        matrix = Matrix(maxLine, len(lines),csw=csw,csh=csh)
        for y, line in enumerate(lines):
            for x, c in enumerate(line):
                matrix.cells[y][x].value = c
        self.addMatrix("Loaded",matrix,makeCurrent=True)
        return matrix
    
    def addMatrix(self, name, matrix, makeCurrent=True):
        self.matrices[name]=matrix
        if makeCurrent==True:
            self.currentMatrix=matrix

    def simpleCoordsLoad(self, filehandle):
        lines=filehandle.readlines()
        coords=[]
        for l in lines:
            nums=extract_numbers(l.strip())
            coords.append((nums[0],nums[1]))

        return coords

    def simpleIntLoad(self, filehandle):
        lines=filehandle.readlines()
        nums=[]
        for l in lines:
            nums.append(int(l.strip()))
        return nums
    
    def createConfigMatrix(self):
        configParams=dict()
    
        for name, value in vars(self).items():
            configParams[name]=value

        matrix=Matrix(2, len(configParams),"",csw=200,csh=20)
        for y, key in enumerate(configParams):
            # lets only consider the booleans for now
            if isinstance(configParams[key], bool)==False:
                continue
            matrix.setCellValue(0,y, key)
            matrix.setCellValue(1, y, configParams[key])
            print(f"Key: {matrix.cells[y][0].value}, Value: {matrix.cells[y][1].value}")
            print("--> Valid next step:",matrix.getCell(1,y).checkValidTransitions())

        return(matrix)
    
    def updateConfigFromMatrix(self):
        # check each row of the matrix, if the second cell is a bool, then update the config
        for y in range(self.currentMatrix.height):
            if isinstance(self.currentMatrix.getCell(1, y).value, bool)==False:
                continue
            setattr(self, self.currentMatrix.getCell(0, y).value, self.currentMatrix.getCell(1, y).value)

    def inspectConfig(self):
        contents=dir(self)
        print(contents)
        boolDict=dict()
        otherDict=dict()
    
        for name, value in vars(self).items():
            print(f"Var: {name}, Valie: {value}")
            if isinstance(value, bool)==True:
                boolDict[name]=value
            else:
                otherDict[name]=value

        print("Bool Dict:")
        for item in boolDict:
            print(f"--> Bool: {item} = {boolDict[item]}")
        
        print("Other Dict:")
        for item in otherDict:
            print(f"---> Other: {item} = {otherDict[item]}")

        attr_name = 'dummy'
        print(getattr(self, attr_name))  # Prints the value of obj.dummy

        setattr(self, attr_name, "NOW SET!")

        print(getattr(self, attr_name))  # Prints the value of obj.dummy
