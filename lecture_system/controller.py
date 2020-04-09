class Controller():
    speakers: List[Speaker]
    sensors: List[Sensor]

    target_dB: float = 35
    # Represents the relative distance between speaker, sensor pairs
    _weights: List[List[float]]

    def __init__(self, speakers, sensors):
        self.speakers = speakers
        self.sensors = sensors
        # Calibrate the system on system initialization
        self._calibrateSystem()

    def _calibrateSystem(self):
        # Generate the internal weights of the system, by playing a test tone
        # on one speaker at a time, and measure the relative loudness on each sensor
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
        # Get new loudness readings on each sensor
        for sensor in self.sensors:
            sensor.update()

    def adjustGains(self):
        # Adjust the gains of each audio output track/speaker.
        # Each sensor measurement is adjusted by the controller's internal weights
        sensed_values = [sensor.getSensorValue() for sensor in self.sensors]
        for speaker, weights in zip(self.speakers, self._weights):
            differential = sum([wi * (self.target_dB - si) for si, wi in zip(sensed_values, weights)])/len(self.sensors)
            if abs(differential) < 0.01:
                differential = 0
            speaker.gain += ADJ_RATE * differential

    def streamAudio(self, audio):
        for speaker in self.speakers:
            speaker.playAudio(audio)
