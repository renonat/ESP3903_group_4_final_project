from typing import List, Tuple, NamedTuple, NewType
from dataclasses import dataclass

from lecture_system.types import Speaker, Sensor
from lecture_system.constants import *
from lecture_system.room_layout import *

class Controller():
    speakers: List[Speaker]
    sensors: List[Sensor]

    target_dB: float = 40
    _weights: List[List[float]]

    def __init__(self, speakers, sensors):
        self.speakers = speakers
        self.sensors = sensors

    def calibrateSystem(self):
        self._weights = []
        for speaker in self.speakers:
            speaker.playCalibrationTone()
            speaker_weights = []
            for sensor in self.sensors:
                sensor.update()
                speaker_weights.append(sensor.getSensorValue())
                sensor.flushHistory()
            speaker.stop()

            self._weights.append([w/sum(speaker_weights) for w in speaker_weights])

    def update(self):
        for sensor in self.sensors:
            sensor.update()

    def adjustGains(self):
        sensed_values = [sensor.getSensorValue() for sensor in self.sensors]
        for speaker, weights in zip(self.speakers, self._weights):
            differential = sum([wi * (self.target_dB - si) for si, wi in zip(sensed_values, weights)])/len(self.sensors)
            speaker.gain += ADJ_RATE * differential

    def testMode(self):
        for speaker in self.speakers:
            speaker.playTestTone()

