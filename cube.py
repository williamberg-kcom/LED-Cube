# TODO: visualizations
# matrix: green dots falling, with trails
# snow: snowflakes falling onto a white base
# snake: an AI playing 3D snake
# sphere: a spinning ball made from a colour wheel
# waves: a multicoloured 3D sine waveform, rotating around the axes
#
import generators
from display import *
from enum import Enum

SIZE = 4

class Pos:
  def __init__(self, x, y, z):
    self.x = x
    self.y = y
    self.z = z

  def is_in_bounds(self, size):
    return self.x >= 0 and self.x < size and self.y >= 0 and self.y < size and self.z >= 0 and self.z < size

  def __add__(self, other):
    return Pos(self.x + other.x, self.y + other.y, self.z + other.z)

  def __sub__(self, other):
    return Pos(self.x - other.x, self.y - other.y, self.z - other.z)

  def __mul__(self, other):
    if type(other) is int:
      return Pos(self.x * other, self.y * other, self.z * other)
    return Pos(self.x * other.x, self.y * other.y, self.z * other.z)

  def __neg__(self):
    return Pos(-self.x, -self.y, -self.z)

  def __eq__(self, other):
    return self.x == other.x and self.y == other.y and self.z == other.z

  def __ne__(self, other):
    return not self.__eq__(other)

class Direction(Enum):
  UP = Pos(0, -1, 0)
  DOWN = Pos(0, 1, 0)
  LEFT = Pos(-1, 0, 0)
  RIGHT = Pos(1, 0, 0)
  FRONT = Pos(0, 0, 1)
  BACK = Pos(0, 0, -1)

def get_perpendicular_direction(dir1, dir2):
  if (dir1 == Direction.UP or dir1 == Direction.DOWN) and (dir2 == Direction.LEFT or dir2 == Direction.RIGHT):
    return Direction.FRONT
  if (dir1 == Direction.LEFT or dir1 == Direction.RIGHT) and (dir2 == Direction.UP or dir2 == Direction.DOWN):
    return Direction.FRONT
  if (dir1 == Direction.UP or dir1 == Direction.DOWN) and (dir2 == Direction.FRONT or dir2 == Direction.BACK):
    return Direction.RIGHT
  if (dir1 == Direction.FRONT or dir1 == Direction.BACK) and (dir2 == Direction.UP or dir2 == Direction.DOWN):
    return Direction.RIGHT
  if (dir1 == Direction.LEFT or dir1 == Direction.RIGHT) and (dir2 == Direction.FRONT or dir2 == Direction.BACK):
    return Direction.DOWN
  if (dir1 == Direction.FRONT or dir1 == Direction.BACK) and (dir2 == Direction.LEFT or dir2 == Direction.RIGHT):
    return Direction.DOWN
  raise ValueError(str(dir1) + " and " + str(dir2) + " are not perpendicular")

def is_direction_positive(direction):
  return (direction == Direction.DOWN or direction == Direction.RIGHT or direction == Direction.FRONT)

class Cube:

  def __init__(self, size = SIZE, colour = Colour.BLACK):
    self.grid = [[[colour for z in range(size)] for y in range(size)] for x in range(size)]
    self.size = size

  def __repr__(self):
    return repr(self.get_colours())

  def __str__(self):
    s = ""
    for x in range(SIZE):
      face = ""
      for y in range(SIZE):
        line = ""
        for z in range(SIZE):
          line += str(self.grid[x][y][z]) + ", "
        face += line + "\n"
      s += "x=" + str(x) + "\n" + face.replace("^", "  ")
    return s

  def get_colours(self):
    """Maps the cube to the 1D colour list that can be displayed on the cube

    This mapping is done based on the order in which each LED exists in sequence in the real cube.
    The first layer is ordered:
    16 15 14 13
     9 10 11 12
     8  7  6  5
     1  2  3  4
    The second layer reverses this ordering
    """
    result = []
    for layer_index, layer in enumerate(self.grid):
      layer_result = []
      for line_index, line in enumerate(layer):
        line_result = line[:]
        if (line_index % 2) == 0:
          line_result.reverse()
        layer_result += line_result
      if (layer_index % 2) == 0:
        layer_result.reverse()
      result += layer_result
    return result

  def set(self, pos, colour):
    self.grid[pos.x][pos.y][pos.z] = colour

  def get(self, pos):
    return self.grid[pos.x][pos.y][pos.z]

  def fill(self, startpos, endpos, colour):
    for x in range(startpos.x, endpos.x + 1):
      for y in range(startpos.y, endpos.y + 1):
        for z in range(startpos.z, endpos.z + 1):
          self.grid[x][y][z] = colour

  def clear(self):
    self.fill(Pos(0, 0, 0), Pos(SIZE - 1, SIZE - 1, SIZE - 1), Colour.BLACK)

  def fill_layer(self, direction, layer, colour):
    """Fills the given layer in the given direction with the given colour.

    As the layer number increases [0-3], the filled layer moves towards the given direction."""
    direction_value = direction.value.x if direction.value.x != 0 else (direction.value.y if direction.value.y != 0 else direction.value.z)
    fixed_coord = layer if direction_value > 0 else (SIZE - 1 - layer)
    for i in range(SIZE):
      for j in range(SIZE):
        x = i if direction.value.x == 0 else fixed_coord
        y = i if direction.value.x != 0 else (j if direction.value.y == 0 else fixed_coord)
        z = j if direction.value.z == 0 else fixed_coord
        self.grid[x][y][z] = colour

  def fill_line(self, line_direction, other_coords, colours):
    """Fills the given line with the given colours.

    The direction represents the direction that the line is pointing in.
    other_coords is a Pos that represents the other two coordinates, the component in line_direction is ignored."""
    cs = colours[:]
    line_direction_value = line_direction.value.x if line_direction.value.x != 0 else (line_direction.value.y if line_direction.value.y != 0 else line_direction.value.z)
    if line_direction_value < 0:
      cs.reverse()
    for i in range(SIZE):
      x = i if line_direction.value.x != 0 else other_coords.x
      y = i if line_direction.value.y != 0 else other_coords.y
      z = i if line_direction.value.z != 0 else other_coords.z
      self.grid[x][y][z] = colours[i]


def scroll_in(cube, direction):
  result = Cube(cube.size)
  startpos = direction.value * -cube.size
  while True:
    for i in range(cube.size):
      for x in range(cube.size):
        for y in range(cube.size):
          for z in range(cube.size):
            newpos = startpos + (direction.value * i) + Pos(x, y, z)
            if newpos.is_in_bounds(cube.size):
              result.set(newpos, cube.get(Pos(x, y, z)))
      yield result
    result = Cube(cube.size)
    yield True

def scroll_out(cube, direction):
  while True:
    for i in range(cube.size):
      result = Cube(cube.size)
      for x in range(cube.size):
        for y in range(cube.size):
          for z in range(cube.size):
            newpos = (direction.value * (i+1)) + Pos(x, y, z)
            if newpos.is_in_bounds(cube.size):
              result.set(newpos, cube.get(Pos(x, y, z)))
      yield result
    yield True

def single_frame(cube):
  while True:
    yield cube
    yield True

def scroll_past(cube, direction):
  return generators.sequence([scroll_in(cube, direction), single_frame(cube), scroll_out(cube, direction)])

if __name__ == "__main__":
  with Display('/dev/ttyUSB0') as d:
    generators.generate(d, generators.sequence([
      scroll_past(Cube(SIZE, Colour.RED), Direction.UP),
      scroll_past(Cube(SIZE, Colour.GREEN), Direction.RIGHT),
      scroll_past(Cube(SIZE, Colour.BLUE), Direction.FRONT),
    ]), delay = 0.5)
