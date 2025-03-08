import pygame
import sys

from utils import *

# This is a 2D matrix (map or table) to track any cells and related processing for the display
class Display:
    def __init__(self, sc, screen, matrix):
        self.sc = sc
        self.width = sc.sw
        self.height = sc.sh 
        self.screen = screen
        self.matrixDrawWindow = (0,0,sc.sw//matrix.cellSizeW,sc.sh//matrix.cellSizeH)
        self.font = pygame.font.SysFont('Segoe UI Emoji', min(sc.currentMatrix.cellSizeW,sc.currentMatrix.cellSizeH)) # emoji capable font


        # common emoji
        self.brickWall="🧱"
        self.tree="🌲"
        self.wood="🪵"
        self.plant="🌱"
        self.grass="🟩"
        self.sick="🤢"
        self.bubbles="🫧"
        self.windows="🪟"

    def switchMatrix(self, sc, name):
        sc.currentMatrix=sc.matrices[name]
        self.adjustDrawWindow(self.sc, 0, 0, 0)

    def isInDrawWindow(self,x,y):
        if x>=self.matrixDrawWindow[0] and x<self.matrixDrawWindow[2] and y>=self.matrixDrawWindow[1] and y<self.matrixDrawWindow[3]:
            return True
        return False
    
    # This adjusts all of the sizing parameters to deal with the fact that the screen has changed
    # size and/or position
    def adjustDrawWindow(self, sc, x, y, matrixSF):

        # Set the new scale factor - TODO - think about if we want to put any boundary checks on the size of this
        csw=sc.currentMatrix.cellSizeW+matrixSF
        csh=sc.currentMatrix.cellSizeH+matrixSF

        sc.currentMatrix.cellSizeW=1 if csw<1 else csw
        sc.currentMatrix.cellSizeH=1 if csh<1 else csh



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
        matrixMaxXCells=self.width//sc.currentMatrix.cellSizeW
        matrixMaxYCells=self.height//sc.currentMatrix.cellSizeH
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
        self.font = pygame.font.SysFont('Segoe UI Emoji', min(sc.currentMatrix.cellSizeW,sc.currentMatrix.cellSizeH)) # emoji capable font

    def drawSprites(self, sc, sprites):
        for sprite in sprites:
            sx1=(sprite.x-self.matrixDrawWindow[0])*sc.currentMatrix.cellSizeW
            sy1=(sprite.y-self.matrixDrawWindow[1])*sc.currentMatrix.cellSizeH
            if sc.fillRects:
                pygame.draw.rect(self.screen, sprite.colour, pygame.Rect(sprite.x*sc.currentMatrix.cellSizeW, sprite.y*sc.currentMatrix.cellSizeH, sprite.w, sprite.h))
            if sc.drawRects:
                pygame.draw.rect(self.screen, sprite.colour, pygame.Rect(sprite.x*sc.currentMatrix.cellSizeW, sprite.y*sc.currentMatrix.cellSizeH, sprite.w, sprite.h),1)
            if sc.drawEmoji:
                self.screen.blit(self.font.render(sprite.emoji, True, sprite.colour), (sx1, sy1))

    def drawPathToScreen(self, sc, path,lColor=(255,0,0)):
        for p in range(0, len(path)-1):
            # for each box in turn, lets draw a line from the centre of that box to the centre of the next box
            # in the pathSofar
            if self.isInDrawWindow(path[p][0], path[p][1])==False:
                continue
 
            px1=(path[p][0]-self.matrixDrawWindow[0])*sc.currentMatrix.cellSizeW
            py1=(path[p][1]-self.matrixDrawWindow[1])*sc.currentMatrix.cellSizeH
            px2=(path[p+1][0]-self.matrixDrawWindow[0])*sc.currentMatrix.cellSizeW
            py2=(path[p+1][1]-self.matrixDrawWindow[1])*sc.currentMatrix.cellSizeH  

            pygame.draw.line(self.screen, lColor, (px1+sc.currentMatrix.cellSizeW/2, py1+sc.currentMatrix.cellSizeH/2), (px2+sc.currentMatrix.cellSizeW/2, py2+sc.currentMatrix.cellSizeH/2), 2 )

    def drawMatrixToScreen(self, sc):
        for matrixY in range(self.matrixDrawWindow[1], self.matrixDrawWindow[3]):
            for matrixX in range(self.matrixDrawWindow[0], self.matrixDrawWindow[2]):
                screenX = (matrixX - self.matrixDrawWindow[0]) * sc.currentMatrix.cellSizeW
                screenY = (matrixY - self.matrixDrawWindow[1]) * sc.currentMatrix.cellSizeH
                cell = sc.currentMatrix.getCell(matrixX, matrixY)
                if cell is not None:
                    # draw a border around the cell  - e.g. for highlighting
                    #pygame.draw.rect(self.screen, cell.color, (screenX, screenY, sf, sf))

                    if sc.fillRects:
                        if isinstance(cell.value, int):
                            c = int(lerp(cell.value, sc.currentMatrix.minCellValue, sc.currentMatrix.maxCellValue, 0, 255))
                            # if cell.value!=0:
                            #     print("lerp:",c,cell.value, sc.currentMatrix.minCellValue, sc.currentMatrix.maxCellValue)
                            pygame.draw.rect(self.screen, (c,c,c), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH))

                    match cell.value:
                        case 0:
                            pass
                        case 1:
                            if sc.drawEmoji:
                                text_surface = self.font.render(self.brickWall, True, (0, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case 2:
                            if sc.drawEmoji:
                                text_surface = self.font.render("🟨", True, (0, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case 3:
                            if sc.drawEmoji:
                                text_surface = self.font.render("🏓", True, (0, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case 4:
                            if sc.drawEmoji:
                                text_surface = self.font.render("⚽", True, (0, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case " ":
                            if sc.drawEmoji:
                                text_surface = self.font.render(self.grass, True, (0, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case "#":
                            if sc.drawEmoji:
                                text_surface = self.font.render(self.windows, True, (255, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case "@":
                            if sc.drawEmoji:
                                text_surface = self.font.render(self.bubbles, True, (255, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case ".":
                            if sc.drawEmoji:
                                text_surface = self.font.render(self.bubbles, True, (0, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))
                        case "o":
                            if sc.drawEmoji:
                                text_surface = self.font.render(self.wood, True, (255, 255, 0))
                                self.screen.blit(text_surface, (screenX, screenY))

                        case _:

                            # # Check for "special" values that we use to "draw" map/matrix elements
                            # if cell.value=="#":
                            #     if sc.drawRects:
                            #         pygame.draw.rect(self.screen, (255,255,0), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH),1)
                            #         #pygame.draw.rect(self.screen, (255, 255, 255), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH), 1)
                            #     if sc.drawEmoji:
                            #         #text_surface = font.render(self.brickWall, True, (255, 255, 0))
                            #         text_surface = font.render(self.sick, True, (255, 255, 0))
                            #         self.screen.blit(text_surface, (screenX, screenY))
                            # elif cell.value=="o":
                            #     if sc.drawRects:
                            #         pygame.draw.rect(self.screen, (125, 125, 125), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH),1)
                            #         #pygame.draw.rect(self.screen, (255, 255, 255), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH), 1)
                            # elif cell.value=="@":
                            #     if sc.drawRects:
                            #         pygame.draw.rect(self.screen, (125, 0, 0), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH),1)
                            #         #pygame.draw.rect(self.screen, (255, 255, 255), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH), 1)
                            #     if sc.drawEmoji:
                            #         text_surface = font.render(self.tree, True, (255, 255, 0))
                            #         self.screen.blit(text_surface, (screenX, screenY))
                            # elif cell.value==".":
                            #     # if sc.drawEmoji:
                            #     #     text_surface = font.render(self.grass, True, (0, 255, 0))
                            #     #     self.screen.blit(text_surface, (screenX, screenY))
                            #     pass

                            # in the event that this cell contains an int value - we can optionally map that to a colour to fill the cell
                            if type(cell.value)==int or type(cell.value)==float:
                                if sc.drawRects:
                                    c = int(lerp(cell.value, sc.currentMatrix.minCellValue, sc.currentMatrix.maxCellValue, 0, 255))
                                    pygame.draw.rect(self.screen, (c, c, c), (screenX, screenY, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH),1)
                                # if sc.drawEmoji:
                                #     c = int(lerp(cell.value, sc.currentMatrix.minCellValue, sc.currentMatrix.maxCellValue, 0, 255))
                                #     text_surface = font.render(self.tree, True, (c, c, c))
                                #     self.screen.blit(text_surface, (screenX, screenY))

                    # This case is for where we just want to display the value of the cell contents
                    if sc.drawCellValues:
                        #if cell.value!=".":
                        v=cell.value
                        # because we maybe storing ints in the matrix, we need to check if we need to map them to a str first
                        v = v if type(cell.value) == str else str(cell.value)

                        # Lets check to see if we have a payload to append to the string
                        if cell.payload is not None:
                            p = cell.payload if type(cell.payload) == str else str(cell.payload)
                            v=v+":"+p
                        text_surface = self.font.render(v, True, (0, 0, 255))
                        self.screen.blit(text_surface, (screenX, screenY))

    def drawGridOnMatrix(self, sc):
        for y in range(0, sc.currentMatrix.height):
            for x in range(0, sc.currentMatrix.width):
                pygame.draw.rect(self.screen, (255, 255, 255), (x*sc.currentMatrix.cellSizeW, y*sc.currentMatrix.cellSizeH, sc.currentMatrix.cellSizeW, sc.currentMatrix.cellSizeH), 1)

    def processEvents(self, sc, event):
        if event.type == pygame.KEYDOWN:
            if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                # Switch to the corresponding matrix
                matrix_index = event.key - pygame.K_0
                if matrix_index<len(sc.matrices):
                    self.switchMatrix(sc, list(sc.matrices.keys())[matrix_index])
            elif event.key == pygame.K_LEFT:
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
            elif event.key == pygame.K_l:
                sc.updateConfigFromMatrix()
            elif event.key == pygame.K_p:
                sc.simpleMatrixSave()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # now check for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Left mouse button clicked
                # Get the mouse position
                mouse_pos = pygame.mouse.get_pos()
                # Calculate the matrix coordinates based on the mouse position
                matrix_x = (mouse_pos[0] // sc.currentMatrix.cellSizeW) + self.matrixDrawWindow[0]
                matrix_y = (mouse_pos[1] // sc.currentMatrix.cellSizeH) + self.matrixDrawWindow[1]

                # Check if the matrix coordinates are within the matrix bounds
                if matrix_x >= 0 and matrix_x < sc.currentMatrix.width and matrix_y >= 0 and matrix_y < sc.currentMatrix.height:
                    # Perform actions based on the clicked cell
                    print(f"Clicked on cell ({matrix_x}, {matrix_y})")
                    # For example, you can access the cell value and perform actions based on it
                    cell_value = sc.currentMatrix.getCell(matrix_x, matrix_y).value
                    print(f"Cell value: {cell_value}")
                    # Add your logic here to handle the click event on the cell
                    # For example, you can update the cell value or trigger some action
                else:
                    # print that we tried to click outside the matrix
                    print(f"Clicked outside matrix: {mouse_pos} v {self.matrixDrawWindow}")

            # call the mouse click handler for this matrix (if its been registered), passing it the cell location that has been clicked
            if sc.currentMatrix.mouseClickHandler is not None:
                sc.currentMatrix.mouseClickHandler(matrix_x, matrix_y)

    def updateDisplay(self, sc, bps=None, cps=None, runs=0, sprites=None):
        # Update the display
        self.screen.fill((0, 0, 0))  # Fill the screen with black (or any other color)


        # draw the screen
        self.drawMatrixToScreen(sc)

        if sc.drawGrid:
            self.drawGridOnMatrix(sc)

        if bps is not None:
            for p in bps:
                #draw path p
                self.drawPathToScreen(sc, p.path, (255, 0, 0))
        if cps is not None:
            for p in cps:
                #draw path p
                self.drawPathToScreen(sc, p.path, (0, 255, 0))

        if sprites is not None:
            self.drawSprites(sc, sprites)

        if runs>0:
            text_surface = self.font.render("Runs: "+str(runs), True, (255, 255, 255))
            self.screen.blit(text_surface, (0, 0))

        pygame.display.flip()  # Refresh the display



