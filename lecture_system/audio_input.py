import soundfile as sf
import numpy as np
from math import sqrt, log10

from lecture_system.constants import BLOCK_SIZE, RMS_MIN

class AudioInput():
    def __init__(self, path):
        # data is an array of [L,R] float values, with (samplerate) samples per second
        data, self.samplerate = sf.read(path, dtype='float32')

        # Chunk the data into blocks of (BLOCKSIZE) samples
        self.audioQ = np.split(data, len(data)/BLOCK_SIZE)

        # Each block is therefore (BLOCK_LEN_S) seconds long
        self.block_len_s = BLOCK_SIZE / self.samplerate

        self.loudnessQ = [self._blockLoudness(b) for b in self.audioQ]

    def nextBlock(self):
        self.block = self.audioQ.pop(0)
        self.loudness = self.loudnessQ.pop(0)

    def _blockLoudness(self, block):
        block_loudness = sqrt(np.mean(block**2))
        if block_loudness < RMS_MIN:
            return 0
        return 20*log10(block_loudness/RMS_MIN)

    def isFinished(self):
        return len(self.audioQ) == 0
