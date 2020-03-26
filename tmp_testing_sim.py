from lecture_system.room_layout import *
from lecture_system.types import *
from lecture_system.controller import Controller

speakers = SPEAKER_ARRAY
sensors = [Sensor(pos, speakers) for pos in SENSOR_POSITIONS]

controller = Controller(speakers, sensors)
controller.calibrateSystem()

controller.testMode()
for i in range(1000):
    controller.update()
    controller.adjustGains()
    print('Iteration', i)
    print('Sensed values', [sensor.getSensorValue() for sensor in sensors])
    print('Gains', [speaker.gain for speaker in speakers])
    print()
