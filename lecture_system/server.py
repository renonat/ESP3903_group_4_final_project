from flask import Flask, render_template
from flask_socketio import SocketIO  # type: ignore
from threading import Thread, Event
from typing import Optional

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

    # Until audio inputs are added, we can use testMode to output a fake loudness level
    controller.testMode()

    eventcounter = 0
    while not thread_stop_event.isSet():
        controller.update()

        if eventcounter % 100 == 0:
            controller.adjustGains()
            # This could be out of the if statment for the adjustment to happen faster
            # In here right now so it is more visible

            # Every time this event is emitted, the webpage content is updated
            socketio.emit('system_update', {'data': {
                "table" : formatted_speaker_data(speakers),
                "readings" : dataToDict(speakers, sensors),
                "eventcounter": eventcounter,
                "roomlayout": generate_html_room_display(speakers, sensors)
            }})

            
            socketio.emit('update_graphs', {'data': {
                "readings": dataToDict(speakers, sensors),
                "eventcounter": eventcounter
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
    socketio.run(app, debug=False)
