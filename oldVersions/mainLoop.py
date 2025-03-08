while running: 
    # print out the run and payload status
    if runs==0:
        print("Run:", runs)  

    if runs%sc.frameRate==0:
        #display.updateDisplay(sc, runs=0, sprites=sm.sprites)
        display.updateDisplay(sc, runs=0)

    # Run one CPU statement
    running=cpu.step()

    # Check the I/O buffer
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
