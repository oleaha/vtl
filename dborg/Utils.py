

class Direction:
    NORTH = 'n'
    SOUTH = 's'
    WEST = 'w'
    EAST = 'e'

    def inverse_dir(self, dir):
        if dir == self.NORTH:
            return self.SOUTH
        elif dir == self.SOUTH:
            return self.NORTH
        elif dir == self.WEST:
            return self.EAST
        elif dir == self.EAST:
            return self.WEST
