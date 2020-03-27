from flask import Flask, render_template
from flask_socketio import SocketIO  # type: ignore
from threading import Thread, Event
from typing import Optional

import soundfile as sf
import numpy as np
from timeit import default_timer as timer
import time
from math import sqrt, log10

import plotly
import plotly.graph_objs as go
import plotly.express as px
import json

from lecture_system.types import Speaker, Sensor
from lecture_system.room_layout import SPEAKER_ARRAY, SENSOR_POSITIONS
from lecture_system.frontend_helpers import formatted_speaker_data, generate_html_room_display, dataToDict
from lecture_system.controller import Controller

app = Flask(__name__)
app.config['SECRET_KEY'] = 'esp3903!'
socketio = SocketIO(app, async_mode=None)
thread: Optional[Thread] = None
thread_stop_event = Event()


@app.route('/')  
def main():
    """
    The main dashboard.
    Demonstrates that we can live update the values using sockets
    """
    return render_template('index.html')

@app.route('/debug')
def debug():
    """
    A debug screen.
    Displays unformatted data
    """
    return render_template('debug.html')


def microphoneInputReader():
    """
    Read our audio input stream, emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    print("Reading the microphone")
    speakers = SPEAKER_ARRAY
    sensors = [Sensor(pos, speakers) for pos in SENSOR_POSITIONS]
    controller = Controller(speakers, sensors)

    @socketio.on('set target')
    def handle_set_target(value):
        controller.target_dB = float(value)

    # data is an array of [L,R] float values, with (samplerate) samples per second
    data, samplerate = sf.read('data/thats-how-you-get-ants.wav', dtype='float32')
    # Chunk the data into blocks of (BLOCKSIZE) samples
    BLOCKSIZE = 1024
    # Each block is therefore (BLOCK_LEN_S) seconds long
    BLOCK_LEN_S = BLOCKSIZE / samplerate
    audioQ = np.split(data, len(data)/BLOCKSIZE)
    output_data = []

    block_counter = 0
    while not thread_stop_event.isSet() and len(audioQ) > 0:
        _start = timer()
        block = audioQ.pop(0)
        controller.streamInput(block)
        controller.update()
        controller.adjustGains()

        # Choose speaker[0] as the output track source
        # Get gain as a value of 1.xx, and transform the block
        gain = 10**(controller.speakers[0].gain/20)
        transformed_block = block * gain
        # Add the transformed block to output array, to be saved to a file
        output_data.extend([list(m) for m in transformed_block])

        if block_counter % 10 == 0:
            # Every time this event is emitted, the webpage content is updated
            socketio.emit('system_update', {'data': {
                "table" : formatted_speaker_data(speakers),
                "readings" : dataToDict(speakers, sensors),
                "eventcounter": block_counter,
                "roomlayout": generate_html_room_display(speakers, sensors)
            }})

        _end = timer()
        # sleep such that each cycle is the same length of time as a block should be
        sleep_time = max(0, BLOCK_LEN_S - (_end - _start))
        socketio.sleep(sleep_time)
        block_counter += 1

    # Processing of the audio file has finished, write transform to output file
    sf.write('data/output-file.wav', np.array(output_data), samplerate)
    print('Completed processing the audio file')


@socketio.on('connect')
def connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')
    #Start the microphone reading thread only if the thread has not been started before.
    if thread is None:
        print("Starting Thread")
        thread = socketio.start_background_task(microphoneInputReader)


if __name__ == '__main__':
    socketio.run(app, debug=False)
