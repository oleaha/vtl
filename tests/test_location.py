from simulation.location.location import Location
from simulation.utils.direction import Direction
from unittest import TestCase

"""
MAP SETTINGS for test

MAP_SIZE_X = 61
MAP_SIZE_Y = 40
ROADS_X = [19, 20]
ROADS_Y = [19, 20, 40, 41]
INTERSECTIONS = [
    ((19, 19), (19, 20), (20, 19), (20, 20)),
    ((19, 40), (19, 41), (20, 40), (20, 41))
]
"""


class TestLocation(TestCase):

    # TODO: Add tests for quarter turns
    def test_oob_from_west_to_east(self):
        location = Location((19, 0))
        location.update_car_pos_turn(to_dir=Direction.WEST, new_to_dir=Direction.EAST)
        assert location.get_car_pos() == (20, 0)

    def test_oob_from_east_to_west(self):
        location = Location((20, 60))
        location.update_car_pos_turn(to_dir=Direction.EAST, new_to_dir=Direction.WEST)
        assert location.get_car_pos() == (19, 60)

    def test_oob_from_north_to_south(self):
        location = Location((0, 20))
        location.update_car_pos_turn(to_dir=Direction.NORTH, new_to_dir=Direction.SOUTH)
        assert location.get_car_pos() == (0, 19)

    def test_oob_from_south_to_north(self):
        location = Location((40, 19))
        location.update_car_pos_turn(to_dir=Direction.SOUTH, new_to_dir=Direction.NORTH)
        assert location.get_car_pos() == (40, 20)

    def test_oob_move_should_return_old_pos(self):
        location = Location((0, 20))
        location.update_car_pos(dir=Direction.NORTH)
        assert location.get_car_pos() == (0, 20)

    def test_oob_move_out_of_road(self):
        location = Location((0, 20))
        location.update_car_pos(dir=Direction.EAST)
        assert location.get_car_pos() == (0, 20)

    def test_in_intersection(self):
        location = Location((19, 19))
        assert location.in_intersection((19, 19))

    def test_is_next_pos_in_intersection(self):
        location = Location((19, 21))
        assert location.is_next_pos_in_intersection((19, 20))

    def test_turn_north_to_west(self):
        pass

    def test_turn_north_to_east(self):
        pass

    def test_turn_north_to_south(self):
        pass

    def test_turn_south_to_west(self):
        pass

    def test_turn_south_to_east(self):
        pass

    def test_turn_south_to_north(self):
        pass

    def test_turn_west_to_north(self):
        pass

    def test_turn_west_to_south(self):
        pass

    def test_turn_west_to_east(self):
        pass

    def test_turn_east_to_north(self):
        pass

    def test_turn_east_to_south(self):
        pass

    def test_turn_east_to_west(self):
        pass
