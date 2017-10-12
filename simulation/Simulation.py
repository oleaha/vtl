import dborg.Car


class Simulation(object):
    CAR_IPS = ['192.168.1.6', '192.168.1.7', '192.168.1.12']
    CAR_INITIAL_POSITIONS = [(16, 19), (19, 0), (40, 0)]

    CARS = []

    def __init__(self):
        for i in range(0, len(self.CAR_IPS)):
            self.CARS.append(dborg.Car.Car(self.CAR_IPS[i], self.CAR_INITIAL_POSITIONS[i]))