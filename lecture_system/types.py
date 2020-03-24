from typing import List, Tuple, NamedTuple, NewType

class Position(NamedTuple):
    x: int
    y: int

class Speaker(NamedTuple):
    loudness: float
    gain: float
    position: Position

class Sensor(NamedTuple):
    loudness: float
    position: Position
