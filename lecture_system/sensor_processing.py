from typing import List
from random import random

from lecture_system.types import Speaker, Sensor
from lecture_system.constants import SENSOR_POSITIONS


def measure_with_sensors(speakers: List[Speaker]) -> List[Sensor]:
    """Do the math for the room acoustics, so that each sensor measures a loudness"""
    sensor_array: List[Sensor] = [Sensor(1.5, posn) for posn in SENSOR_POSITIONS]
    return sensor_array


def update_speaker_gain(speakers: List[Speaker], sensors: List[Sensor]) -> List[Speaker]:
    """Based on the sensor measurements update the speaker gain"""
    for i in range(len(speakers)):
        speakers[i] = Speaker(speakers[i].loudness, random(), speakers[i].position)
    return speakers
