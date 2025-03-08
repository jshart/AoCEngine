from enum import Enum, auto

class VDUMODES(Enum):
    INITIAL_DRAW=auto()
    CLI=auto()
    CONTINUOUS_VIDEO=auto()



# create an OPCODE enum
class OPCODE(Enum):
    ADD = 1
    MUL = 2
    INPUT = 3
    OUTPUT = 4
    JIT = 5
    JIF = 6
    LT = 7
    EQ = 8
    RBASE = 9
    HALT = 99

class ADDRESS_MODE(Enum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2

class IOBuffer:
    def __init__(self):
        self.buffer=[]

    def write(self, value):
        self.buffer.append(value)

    def read(self):
        if len(self.buffer)>0:
            return self.buffer.pop(0)
        else:
            return None

    def print(self):
        print("IO Buffer:")
        for o in self.buffer:
            print("\\_[",o,"]")

class CPU:
    def __init__(self):
        #self.registers=dict()
        self.PC=0 # program counter
        self.rBase=0
        self.rawProgram=[]
        self.program=[]
        self.outputBuffer=None
        self.inputBuffer=None

        self.defineRegisters()

    def attachInputBuffer(self, buffer):
        self.inputBuffer=buffer
    
    def attachOutputBuffer(self, buffer):
        self.outputBuffer=buffer

    def pollForInput(self):
        if self.inputBuffer==None:
            return None
        return self.inputBuffer.read()

        
    def splitCode(self,cStr):
        m=""

        # first lets get the opcode, which maybe 1 or 2 digits
        if len(cStr)==1:
            c=int(cStr[-1])
        elif len(cStr)>=2:
            c=int(cStr[-2:])

        # for any other digits, these are mode controls, so we simply
        # return those
        if len(cStr)>=3:
            # the rest of string is mode controls
            m=cStr[:-2]
            # reverse the string
            m=m[::-1]

        # we should always have 3 mode control bits, so if the string is
        # less than 3 chars, lets pad out the end with 0s
        m=m.ljust(3, "0")
        # convert to ints
        m=[int(x) for x in m]
        return c,m


    def step(self):

        lhs=0
        rhs=0
        dest=0
        c,m=self.splitCode(str(self.program[self.PC]))
        #print("OP:",c," Modes:",m)

        c=OPCODE(c)
        # do we have a param left in the program?
        if self.PC+1<len(self.program):
            if m[0]==ADDRESS_MODE.POSITION.value:
                lhs=self.program[self.PC+1]
            elif m[0]==ADDRESS_MODE.IMMEDIATE.value:
                lhs=self.PC+1
            elif m[0]==ADDRESS_MODE.RELATIVE.value:
                lhs=self.program[self.PC+1]+self.rBase

        if self.PC+2<len(self.program):
            if m[1]==ADDRESS_MODE.POSITION.value:
                rhs=self.program[self.PC+2]
            elif m[1]==ADDRESS_MODE.IMMEDIATE.value:
                rhs=self.PC+2
            elif m[1]==ADDRESS_MODE.RELATIVE.value:
                rhs=self.program[self.PC+2]+self.rBase
 
        if self.PC+3<len(self.program):
            if m[2]==ADDRESS_MODE.POSITION.value:
                dest=self.program[self.PC+3]
            elif m[2]==ADDRESS_MODE.IMMEDIATE.value:
                dest=self.PC+3    
            elif m[2]==ADDRESS_MODE.RELATIVE.value:
                dest=self.program[self.PC+3]+self.rBase
 
        #print("---ADDRESSES LHS:", lhs, "RHS:", rhs, "DEST:", dest, end=" --OPCODE=")

        match c:
            case OPCODE.ADD:
                #print("[ADD]")
                self.program[dest]=self.program[lhs]+self.program[rhs]

                # move on the PC
                self.PC+=4

            case OPCODE.MUL:
                #print("[MUL]")
                self.program[dest]=self.program[lhs]*self.program[rhs]

                # move on the PC
                self.PC+=4
        
            case OPCODE.INPUT:
                #print("[INPUT]")
                # get input from the user
                i=self.pollForInput()

                # if this found something, update
                # the LHS and mpve the PC. If it
                # found None then we "no-op" as
                # that leaves the PC pointing at this
                # and means we'll poll again (effectively
                # pause here until we get an input)
                if i!=None:
                    print("[INPUT]=", i)
                    self.program[lhs]=i

                    # move on the PC
                    self.PC+=2

            case OPCODE.OUTPUT:
                #print("[OUTPUT]")
                # output to the user
                #print("--Value:", self.program[lhs])
                self.outputBuffer.write(self.program[lhs])

                # move on the PC
                self.PC+=2

            case OPCODE.JIF:
                #print("[JIF]")
                if self.program[lhs]==0:
                    self.PC=self.program[rhs]
                else:
                    self.PC+=3
                
            case OPCODE.JIT:
                #print("[JIT]")
                if self.program[lhs]!=0:
                    self.PC=self.program[rhs]
                else:
                    self.PC+=3

            case OPCODE.LT:
                #print("[LT]")
                if self.program[lhs]<self.program[rhs]:
                    self.program[dest]=1
                else:
                    self.program[dest]=0

                # move on the PC
                self.PC+=4

            case OPCODE.EQ:
                #print("[EQ]")
                if self.program[lhs]==self.program[rhs]:
                    self.program[dest]=1
                else:
                    self.program[dest]=0

                # move on the PC
                self.PC+=4
        
            case OPCODE.RBASE:
                #print("[RBASE]")
                self.rBase+=self.program[lhs]

                # move on the PC
                self.PC+=2

            case OPCODE.HALT:
                #print("[HALT]")
                # move on the PC
                self.PC+=1
                return False

        # if we've completed the program return False
        # to indicate there are no more steps
        if self.PC >= len(self.program):
            return False
        
        # Otherwise if we hit here there are more
        # steps - so return True to indicate there
        # is still more to do
        return True
  
    def defineRegisters(self):
        # example code to setup registers based on upper case letters
        # for i in range(0, 26):
        #     self.registers[chr(ord("A")+i)]=0

        # example code to setup registers named 0 thru 3
        # for i in range(0, 4):
        #     self.registers[str(i)]=0

        # example code to setup registers 'a' thru 'd'
        # for i in range(ord("a"), ord("d")+1):
        #     self.registers[chr(i)]=0
        pass

    def setRegister(self,key,value):
        self.registers[key]=value

    # load a comma seperated value string of numbers, splitting by comma
    def loadCSVNumbers(self, filehandle, minLen):
        lines=filehandle.readlines()
        for l in lines:
            l=l.strip()
            for n in l.split(","):
                self.program.append(int(n))
                print(len(self.program),":[", n, "]")

        # Pad the end of the program with empty memory
        if len(self.program)<minLen:
            for i in range(len(self.program), minLen):
                self.program.append(0)

    def loadProgram(self, filehandle):
        lines=filehandle.readlines()
        for l in lines:
            self.rawProgram.append(l.strip())

        for l in self.rawProgram:
            self.program.append(cpuCommand(l))

    def print(self):
        self.printCPUState()
        #self.printRegisters()
        self.printProgram()

    def printCPUState(self):
        print("PC:", self.PC, "=>", self.program[self.PC])

    def printRegisters(self):
        for k in self.registers:
            print(k, "=>", self.registers[k], end="  ")
        print("")

    def printProgram(self):
        for c in self.program:
            print("C:",str(c))

class cpuCommand:
    def __init__(self, rawStr):
        self.rawStr=rawStr
        self.opCode=rawStr.split(" ")[0]
        self.operands=rawStr.split(" ")[1:]

    def print(self):
        print(self.opCode,"=>",self.operands)

