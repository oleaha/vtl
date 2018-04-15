from simulation.apps.traffic_light.regular_traffic_light import TrafficLight


class Intersection:

    POSITION = []

    def __init__(self, pos, use_traffic_light=False):
        self.POSITION = pos
        if use_traffic_light:
            self.traffic_light = TrafficLight(intersection=self.POSITION)

    def get_pos(self):
        return self.POSITION

    def __str__(self):
        return "3"
