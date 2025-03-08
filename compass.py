from enum import Enum, auto

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
        