
class Direction:
    NORTH = 'n'
    SOUTH = 's'
    WEST = 'w'
    EAST = 'e'

    def inverse_dir(self, direction):
        if direction == self.NORTH:
            return self.SOUTH
        elif direction == self.SOUTH:
            return self.NORTH
        elif direction == self.WEST:
            return self.EAST
        elif direction == self.EAST:
            return self.WEST
