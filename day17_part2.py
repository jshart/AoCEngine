from enum import Enum, auto
import time
import re
import math
from collections import defaultdict
import pygame
import sys
import networkx as nx


from utils import *
from hashTracker import *
from compass import *
from sprite import *
from searchSpace import *
from systemConfig import *
from cpu import *
from display import *


sc=SystemConfig()

part2=False
if sc.testMode:
    file1 = open(sc.dataPath+'/input_test.txt', 'r')
    cellSizeW=20
    cellSizeH=20
    initMatrixX=50
    initMatrixY=50
else:
    file1 = open(sc.dataPath+'/input.txt', 'r')
    cellSizeW=15
    cellSizeH=15
    initMatrixX=41
    initMatrixY=47
    robotCommands=["A","R","L,10,L,12,R,6,R,10,L,4,L,4,L,12","R","R","y"]
    #               1234567890123456789   1234567890123   12345678901234567   12345678901234567
    robotCommands=["A,B,A,B,A,C,B,C,A,C","L,10,L,12,R,6","R,10,L,4,L,4,L,12","L,10,R,10,R,6,L,4","y"]


configMatrix=sc.createConfigMatrix()
sc.addMatrix("config",configMatrix, True)
configMatrix.registerMouseClickHandler(configMatrix.defaultMouseClickHandler)

# **** Start of puzzle specific setup code
vdu=Matrix(initMatrixX,initMatrixY,defaultValue=0,csw=cellSizeW,csh=cellSizeH)
vdu.setAllTo(0)
sc.addMatrix("vdu", vdu, True)    

cpu = CPU()
CPUToVDU=IOBuffer()
InputToCPU=IOBuffer()
cpu.loadCSVNumbers(file1,10000)
cpu.attachOutputBuffer(CPUToVDU)
cpu.attachInputBuffer(InputToCPU)

screenDrawX=0
screenDrawY=0

# sm = SpriteManager()
# repairRobot=Robot(initMatrixX//2, initMatrixY//2, cellSizeW, cellSizeH)
# repairRobot.recordLocation()
# sm.addSprite(repairRobot.sprite)

# lets load the input buffer with our programs
for r in robotCommands:
    asciiProgram=asciiDigitsList(r)
    print(r,"-->",asciiProgram)
    InputToCPU.buffer.extend(asciiProgram.copy())

print("**** Forcing control mode")
cpu.program[0]=2
print("**** IO Buffer configured")
InputToCPU.print()

print ("=== PROGRAM STARTING ===")

# **** End of puzzle specific setup code


# create a pygame window
pygame.init()
sc.sw=sc.currentMatrix.width * sc.currentMatrix.cellSizeW
sc.sh=sc.currentMatrix.height * sc.currentMatrix.cellSizeH
screen = pygame.display.set_mode((sc.sw, sc.sh))
pygame.display.set_caption(sc.screenCaption+" M: "+str(sc.currentMatrix.width)+"x"+str(sc.currentMatrix.height))
#font = pygame.font.Font(None, scaleFactor)
display = Display(sc, screen, sc.currentMatrix)
# end standard pygame setup code


# Main game loop - will repeatedly draw whilst the running flag
# is set and the maxRuns (iterations) limit has not been hit.
# Adjust either exit condition to suit. Can also put into an infinite
# loop and rely on user hitting the window close button which will be
# caught with the pygame QUIT event
running = True
runs=0
maxRuns=100000

lastCharSeen=None
screenDrawMode=VDUMODES.INITIAL_DRAW

sc.frameRate=100
proposedRobotDirection=None
while running: #and runs<maxRuns:
#while running:
    # print out the run and payload status
    if runs==0:
        print("Run:", runs)  

    joystick=0
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                # add -1 to the input buffer
                joystick=1
            if event.key == pygame.K_s:
                # add -1 to the input buffer
                joystick=2
            if event.key == pygame.K_a:
                # add -1 to the input buffer
                joystick=3
            if event.key == pygame.K_d:
                # add -1 to the input buffer
                joystick=4

        display.processEvents(sc, event)

    # if the joystick has been moved, add to the IO buffer
    if joystick!=0:
        match joystick:
            case 1:
                proposedRobotDirection=CompassDirection.NORTH
            case 2:
                proposedRobotDirection=CompassDirection.SOUTH
            case 3:
                proposedRobotDirection=CompassDirection.WEST
            case 4:
                proposedRobotDirection=CompassDirection.EAST
            case _:
                print("invalid joystick value:", joystick)

        print("joystick:", joystick, " mapped to:",proposedRobotDirection)
        #InputToCPU.write(joystick)


    if runs%sc.frameRate==0:
        #display.updateDisplay(sc, runs=0, sprites=sm.sprites)
        display.updateDisplay(sc, runs=0)

        #time.sleep(1/sc.frameRate) # now sleep for 0.25 seconds
        #cpu.printCPUState()
        #time.sleep(0.01)

    running=cpu.step()

    # lets fetch a pair of numbers from the robot commands
    if len(CPUToVDU.buffer)>=1:

        #print("CPUToVDU:", CPUToVDU.buffer)
        asciiValue=CPUToVDU.read()
        r=int(asciiValue)
        #print(r)
        # map r to an ascii char
        drawChar=chr(r)
        if r>255:
            print("*** FINAL RESULT?= ",r)
        match r:
            case 10:
                screenDrawX=0
                screenDrawY+=1
                if lastCharSeen==10:
                    print("*** DOUBLE LINE FEED SEEN - SWITCHING MODES")
                    match screenDrawMode:
                        case VDUMODES.INITIAL_DRAW:
                            # we have a double line feed, so we have finished the screen
                            print("End of screen - flipping to CLI mode")
                            print("draw area computed: ", screenDrawX, screenDrawY)
                            print("Screen size preset to: ", vdu.width, vdu.height)
                            screenDrawMode=VDUMODES.CLI
                            screenDrawX=0
                            screenDrawY=0
                        case VDUMODES.CLI:
                            # we have a double line feed, so we have finished the screen
                            print("End of CLI - flipping to continuous Draw mode")
                            screenDrawMode=VDUMODES.CONTINUOUS_VIDEO
                            screenDrawX=0
                            screenDrawY=0
                        case VDUMODES.CONTINUOUS_VIDEO:
                            print("NEW FRAME")
                            screenDrawX=0
                            screenDrawY=0
                            sc.frameRate=100
            case _:
                match screenDrawMode:
                    case VDUMODES.INITIAL_DRAW | VDUMODES.CONTINUOUS_VIDEO:
                        vdu.setCellValue(screenDrawX, screenDrawY, drawChar)
                        screenDrawX+=1
                    case _:
                        if screenDrawMode==False:
                            print("CPU:", r, " --> ", drawChar)
        lastCharSeen=r
    runs+=1


# Puzzle specific results - print out key counters here
print("=== PROGRAM COMPLETE === [after: ",runs," runs]")

#cpu.printProgram()
#sc.inspectConfig()
cpu.outputBuffer.print()

running=True

# if we exited the previous loop due to the run count, we now just sit with the
# window open/idle waiting to be closed. This allows us to see the final state
# of the display after completing the puzzle.
while running:

    for event in pygame.event.get():
        display.processEvents(sc, event)

    # update the display
    #display.updateDisplay(sc, runs=0, sprites=sm.sprites)
    display.updateDisplay(sc, runs=0)

# Clean up and exit
pygame.quit()


# box unicode chars; https://en.wikipedia.org/wiki/Box_Drawing

# Fixed up so that the sprite will draw, and that the matrix cell will paint based on the numeric value (e.g. 0/black 1/white)
# Need to implement sprite behaviour to move and paint
# Need to link program execution to spire behaviour


#Found oxygen system at: 5 7
#377 too high
