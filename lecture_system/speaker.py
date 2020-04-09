@dataclass
class Speaker():
    """
    Virtual representation of an audio Speaker.
    The Speaker outputs the current loudness of its input source.
    """
    position: Position

    gain: float = 0
    _audio_source: str = 'silent'
    _audio_input: AudioInput = None

    def playCalibrationTone(self):
        # Sets the audio source to a calibration tone
        self._audio_source = 'calibration'

    def playAudio(self, audio_input):
        # Sets the audio source to an input array
        self._audio_input = audio_input
        self._audio_source = 'input'

    def stop(self):
        # Silences the audio input
        self._audio_source = 'silent'

    def getLoudness(self) -> float:
        # Returns the loudness of the audio source in dB
        if self._audio_source == 'silent':
            return 0
        elif self._audio_source == 'calibration':
            return CALIBRATION_DB + self.gain
        elif self._audio_source == 'input':
            return self._audio_input.loudness + self.gain
