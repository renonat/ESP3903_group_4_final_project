from flask import Flask, render_template
from flask_socketio import SocketIO  # type: ignore
from threading import Thread
from typing import List
from threading import Thread, Event
from prettytable import PrettyTable  # type: ignore

import plotly
import plotly.graph_objs as go
import plotly.express as px
import json

from lecture_system.types import Speaker, Sensor
from lecture_system.sensor_processing import measure_with_sensors, update_speaker_gain
from lecture_system import constants

app = Flask(__name__)
app.config['SECRET_KEY'] = 'esp3903!'
socketio = SocketIO(app, async_mode=None)
thread = Thread()
thread_stop_event = Event()


@app.route('/')  
def main():
    """
    The main dashboard.
    Demonstrates that we can live update the values using sockets
    """
    return render_template('index.html')


def formatted_speaker_data(speakers: List[Speaker]) -> str:
    """Used to display pretty speaker data on the webpage"""
    table = PrettyTable(['Speaker', 'Loudness', 'Gain', 'Position'])
    for i in range(len(speakers)):
        speaker = speakers[i]
        table.add_row([i, f"{speaker.loudness:0.2f}", f"{speaker.gain:0.2f}", speaker.position])
    return table.get_html_string()


def microphoneInputReader():
    """
    Read our audio input stream, emit to a socketio instance (broadcast)
    Ideally to be run in a separate thread?
    """
    print("Reading the microphone")
    speakers = constants.SPEAKER_ARRAY
    eventcounter = 0

    while not thread_stop_event.isSet():
        for i in range(len(speakers)):
            speaker = speakers[i]
            speakers[i] = Speaker(speaker.loudness + 0.001, speaker.gain, speaker.position)
        sensors = measure_with_sensors(speakers)
        speakers = update_speaker_gain(speakers, sensors)

        if eventcounter % 100 == 0:
            # Every time this event is emitted, the webpage content is updated
            socketio.emit('speaker_update', {'data': {
                "table" : formatted_speaker_data(speakers),
                "readings" : dataToDict(speakers, sensors),
                "eventcounter": eventcounter
            }})
        socketio.sleep(0.01)
        eventcounter += 1

def dataToDict(speakers: List[Speaker], sensors: List[Sensor]) -> dict:
    return {
        "speakers": [{
            "loudness": speaker.loudness,
            "gain": speaker.gain,
            "position": speaker.position
        } for speaker in speakers],
        "sensors": [{
            "loudness": sensor.loudness,
            "position": sensor.position
        } for sensor in sensors]
    }


@socketio.on('connect')
def connect():
    # need visibility of the global thread object
    global thread
    print('Client connected')
    #Start the microphone reading thread only if the thread has not been started before.
    if not thread.isAlive():
        print("Starting Thread")
        thread = socketio.start_background_task(microphoneInputReader)


if __name__ == '__main__':
    socketio.run(app)
