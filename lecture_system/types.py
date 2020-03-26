from typing import List, Tuple, NamedTuple, NewType
from dataclasses import dataclass
from math import log10, exp, sqrt
from functools import reduce
from collections import deque

from lecture_system.constants import *

class Position(NamedTuple):
    x: int
    y: int

    def distanceTo(self, other):
        return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Speaker():
    position: Position
    gain: float = 0
    _audio_source: str = 'silent'

    def playCalibrationTone(self):
        self._audio_source = 'calibration'

    def playTestTone(self):
        self._audio_source = 'test'

    def stop(self):
        self._audio_source = 'silent'

    def getLoudness(self) -> float:
        if self._audio_source == 'silent':
            return 0
        elif self._audio_source == 'calibration':
            return CALIBRATION_DB + self.gain
        elif self._audio_source == 'test':
            return 90 + self.gain


@dataclass
class Sensor():
    position: Position
    speakers: List[Speaker]

    def __post_init__(self):
        self.speaker_weights = [0.0 for i in self.speakers]
        self._history = deque()

    def _senseSpeaker(self, speaker: Speaker) -> float:
        distance = self.position.distanceTo(speaker.position)
        loudness = speaker.getLoudness()
        return max(0, loudness - 20 * (log10(distance) - log10(REFERENCE_DISTANCE)))

    def _addDb(self, a, b):
        return 10 * log10(10**(a/10) + 10**(b/10))

    def update(self):
        loudnesses = [self._senseSpeaker(speaker) for speaker in self.speakers]
        self._history.append(reduce(self._addDb, loudnesses))
        if len(self._history) > SENSOR_SAMPLE_LENGTH:
            self._history.popleft()

    def flushHistory(self):
        self._history = deque()

    def getSensorValue(self):
        return sum(self._history)/len(self._history)
