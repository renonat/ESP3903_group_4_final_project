from flask import Flask, render_template
from flask_socketio import SocketIO  # type: ignore
from threading import Thread, Event
from typing import Optional

import plotly
import plotly.graph_objs as go
import plotly.express as px
import json

from lecture_system.types import Speaker, Sensor
from lecture_system.sensor_processing import measure_with_sensors, update_speaker_gain
from lecture_system import constants
from lecture_system.frontend_helpers import formatted_speaker_data, generate_html_room_display, dataToDict

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
            socketio.emit('system_update', {'data': {
                "table" : formatted_speaker_data(speakers),
                "readings" : dataToDict(speakers, sensors),
                "eventcounter": eventcounter,
                "roomlayout": generate_html_room_display(speakers, sensors)
            }})

        socketio.sleep(0.001)
        eventcounter += 1



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
    socketio.run(app, debug=True)
