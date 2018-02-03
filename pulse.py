from cube import *
from display import *
import functools

def fade(brightness, colour):
  return Colour((colour.r * brightness, colour.g * brightness, colour.b * brightness))

def pulse(cube):
  while True:
    for i in range(21):
      c = cube.copy()
      c.transform_colours(functools.partial(fade, i / 20))
      yield c
    for i in range(21):
      c = cube.copy()
      c.transform_colours(functools.partial(fade, (20 - i) / 20))
      yield c
    yield True

if __name__ == "__main__":
  with Display('/dev/ttyUSB0') as d:
    generators.generate(d, generators.sequence([
      pulse(Cube(colour = Colour((255, 0, 0)))),
      pulse(Cube(colour = Colour((0, 255, 0)))),
      pulse(Cube(colour = Colour((0, 0, 255)))),
      pulse(Cube(colour = Colour((255, 255, 255)))),
    ]))

