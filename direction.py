from enum import Enum

class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    def __str__(self):
        match self:
            case Direction.NORTH: return "^"
            case Direction.EAST: return ">"
            case Direction.SOUTH: return "v"
            case Direction.WEST: return "<"
