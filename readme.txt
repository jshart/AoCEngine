#       ┌─────────────────┐                                                   
#       │System Config    │                                                   
#       │                 │                                                   
#       │                 │                                                   
#       └──┬──────────────┘                                                   
#          │Tracks                                                            
#          │Multiple                                                          
#          │                                                                  
#          │                                                                  
#       ┌──▼──────────────┐Draws  ┌─────────────────┐     ┌──────────────────┐
#       │Matrix           ◄───────┼Display (PyGame) │     │Sprite Manager    │
# ┌─────►                 │       │                 │     │                  │
# │     │                 │       │                 │     │                  │
# │     └──┬──────────────┘       └────────────┬───┬┘     └───┬──────────────┘
# │        │                                   │   │          │Tracks         
# │        │ Contains                    Draws │   │Draws     │Multiple       
# │        │ Many                              │   │          │               
# │        │                                   │   │          │               
# │     ┌──▼──────────────┐                    │   │      ┌───▼──────────────┐
# │     │Cell             │                    │   └──────►Sprite            │
# ┼─────►                 │                    │          │                  │
# │     │                 │                    │          │                  │
# │     └──────────────▲──┘       ┌────────────▼────┐     └───┬─┬────────────┘
# │                    └──────────┼Path             │         │ │             
# │                       Tracks  │                 ◄─────────┘ │             
# │                               │                 │ Uses      │             
# │                               └─▲───────────────┘           │             
# │                                 │                           │             
# │                                 │Creates                    │             
# │                                 │                           │             
# │     ┌────────────────┐  Uses  ┌─┼───────────────┐           │             
# │     │NodeWeights     ◄────────┼SearchSpace      │           │             
# │     │                │        │                 ◄───────────┘             
# └─────┼                │        │                 │ Uses                    
#       └────────────────┘        └─────────────────┘                         
# https://asciiflow.com/#/local/AoC_Class_Model          

# DayTemplate Python Program

## Overview

This Python script implements a matrix-based system for visualizing, processing, and interacting with 2D grids. It leverages libraries like `pygame` for graphical display and provides tools for cellular automata, pathfinding, and sprite management. The script is modular, with clear components for configuration, matrix operations, and visual rendering.

## Features

- **Matrix Manipulation**: Create, modify, and query 2D matrices with various operations such as submatrix extraction, flood-fill, and rotation.
- **Pathfinding**: Tools for tracking paths and calculating costs using customizable heuristics.
- **Visualization**: Render grids and interactive elements using `pygame`.
- **Sprites**: Manage movable objects with collision detection and behavior scripting.
- **Utility Functions**: Extract numbers from strings, calculate Manhattan distance, and perform other helper operations.

## Key Classes and Functions

### 1. **SystemConfig**
Handles global settings for the application, including screen dimensions, drawing modes, and active matrices.

- `simpleMatrixLoad(filehandle)`: Load a matrix from a file with character-based data.
- `simpleCoordsLoad(filehandle)`: Load coordinate pairs from a file.
- `inspectConfig()`: Prints the current system configuration for debugging.

---

### 2. **Matrix**
Represents a 2D grid with extensive functionality.

- `getCell(x, y)`: Retrieve a cell at specific coordinates.
- `setCell(x, y, value)`: Update a cell's value.
- `randomiseMatrix(min, max)`: Populate the matrix with random numbers within a range.
- `findAllCharMatchesInString(value)`: Locate all occurrences of specific characters in the matrix.
- `subMatrix(x1, y1, x2, y2)`: Extract a subregion as a new matrix.
- `floodFill(map, start, p, visitedPoints, maxDist, stopChar=None)`: Performs flood-fill based on distance and optional stopping conditions.

---

### 3. **CompassDirection (Enum)**
Enumerates directions (NORTH, SOUTH, EAST, WEST) with utilities for rotation and movement deltas.

- `turnRight()`, `turnLeft()`, `turn180()`: Rotate the direction.
- `getMovementDelta()`: Get movement offsets for the current direction.

---

### 4. **Sprite and SpriteManager**
Defines and manages objects that move within the matrix.

- **Sprite**:
  - `checkNextValidMoves(matrix)`: Determines valid moves based on current location.
  - `updateLocation(destCell)`: Updates the sprite's position.

- **SpriteManager**:
  - `addSprite(sprite)`, `removeSprite(sprite)`: Add or remove sprites.
  - `checkForSpriteCollisions(sprite)`: Detect and handle collisions.

---

### 5. **Display**
Handles graphical rendering using `pygame`.

- `drawMatrixToScreen(sc)`: Renders the current matrix to the screen.
- `drawSprites(sc, sprites)`: Displays all sprites.
- `processCommands(sc, event)`: Processes keyboard and window events for interaction.

---

### 6. **SearchSpace**
Manages pathfinding using algorithms like A*.

- `initNodeWeights(path)`: Initializes weight tracking for nodes.
- `update()`: Advances the pathfinding process.

---

## Usage

### Requirements
- Python 3.x
- `pygame`, `networkx`, `numpy`

### Running the Program
1. Install dependencies using `pip install pygame networkx numpy`.
2. Run the script:
   ```bash
   python dayTemplate.py
