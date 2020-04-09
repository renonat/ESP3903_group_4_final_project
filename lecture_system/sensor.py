@dataclass
class Sensor():
    """
    Virtual representation of a sound pressure sensor (microphone).
    """
    position: Position
    speakers: List[Speaker]

    def __post_init__(self):
        self.speaker_weights = [0.0 for i in self.speakers]
        self._history = deque()

    def _senseSpeaker(self, speaker: Speaker) -> float:
        # Returns sensed loudness of a speaker, based on their relative distance.
        # Actual positions are used to simulate the acoustics of a room.
        distance = self.position.distanceTo(speaker.position)
        loudness = speaker.getLoudness()
        return max(0, loudness - 20 * (log10(distance) - log10(REFERENCE_DISTANCE)))

    def _addDb(self, a, b):
        return 10 * log10(10**(a/10) + 10**(b/10))

    def update(self):
        # Add the measured loudness of all speakers to the sensor's internal history
        loudnesses = [self._senseSpeaker(speaker) for speaker in self.speakers]
        total_loudness = reduce(self._addDb, loudnesses)

        self._history.append(total_loudness)
        if len(self._history) > SENSOR_SAMPLE_LENGTH:
            self._history.popleft()

    def flushHistory(self):
        self._history = deque()

    def getSensorValue(self):
        # Returns the loudness of the sensor in dB, based on a weighted
        # average of the past ten sensor measurements.
        return np.average(self._history, weights=range(1, len(self._history) + 1))
