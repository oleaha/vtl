

class Location(object):
    location_table = {}

    map = [[0 for j in range(61)] for i in range(40)]
    intersections = []

    _my_pos = (None, None)

    def get_my_pos(self):
        return self._my_pos

    def set_my_pos(self, pos):
        self._my_pos = pos
    my_pos = property(get_my_pos, set_my_pos)

    def __init__(self, x, y, scenario):
        self.init_map(scenario)
        self.set_init_pos(x, y)
        self.init_intersections(scenario)

    def init_map(self, scenario):
        if scenario == 1:
            self.map[19] = [1 for j in range(61)]
            self.map[20] = [1 for j in range(61)]

            for i in range(40):
                self.map[i][19] = 1
                self.map[i][20] = 1
                self.map[i][40] = 1
                self.map[i][41] = 1
            return self.map

    def init_intersections(self, scenario):
        if scenario == 1:
            self.intersections.append((19, 19, 1, 1))
            self.intersections.append((19, 20, 1, 2))
            self.intersections.append((20, 19, 1, 3))
            self.intersections.append((20, 20, 1, 4))

            self.intersections.append((19, 40, 2, 1))
            self.intersections.append((19, 41, 2, 2))
            self.intersections.append((20, 40, 2, 3))
            self.intersections.append((20, 41, 2, 4))
        return

    def set_init_pos(self, x, y):
        self.my_pos = (x, y)
        return

    def draw_map(self):
        tmp = self.init_map(1)
        self.add_intersections(tmp)
        self.add_location_table(tmp)
        self.add_my_pos(tmp)
        tmp[0][0] += 1

        for r in tmp:
            print r
        print "\n"

    def add_my_pos(self, map):
        map[self.my_pos[1]][self.my_pos[0]] = 8
        return map

    def my_pos_x(self):
        return self.my_pos[0]

    def my_pos_y(self):
        return self.my_pos[1]

    def add_intersections(self, map):
        for intersection in self.intersections:
            inter_x = intersection[0]
            inter_y = intersection[1]
            map[inter_x][inter_y] = 3
        return map

    def add_location_table(self, map):
        for car, pos in self.location_table.iteritems():
            car_x = pos[0][0]
            car_y = pos[0][1]
            map[car_x][car_y] = 4
        return map

    def update_location_table(self, car_id, pos, dist, intersection_id, direction, approaching):
        self.location_table[car_id] = [pos, dist, intersection_id, direction, approaching]

    def delete_car(self, car_id):
        del self.location_table[car_id]

    def update_pos(self, direction):
        if direction == 'u':
            self.my_pos = (self.my_pos[0], self.my_pos[1] - 1)
            return
        elif direction == 'd':
            self.my_pos = (self.my_pos[0], self.my_pos[1] + 1)
            return
        elif direction == 'l':
            self.my_pos = (self.my_pos[0] - 1, self.my_pos[1])
            return
        elif direction == 'r':
            self.my_pos = (self.my_pos[0] + 1, self.my_pos[1])
            return
        return

    def distance_to_intersection(self):
        min_dist = 120
        for intersection in self.intersections:
            inter_x = intersection[1]
            inter_y = intersection[0]

            dist = abs(self.my_pos_x() - inter_x) + abs(self.my_pos_y() - inter_y)

            if dist < min_dist:
                min_dist = dist
                inter_id = intersection[2]
                inter_dir = intersection[3]
        return [min_dist, inter_id, inter_dir, 0]

