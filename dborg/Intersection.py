

class Intersection(object):
    POS = []
    STATISTICS = {'num_cars': 0,
                  'avg_wait': 0}

    def __init__(self, placement):
        self.POS = placement

    def get_pos(self):
        return self.POS

    def __str__(self):
        return "3"
