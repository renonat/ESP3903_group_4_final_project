from flask import Flask
from prettytable import PrettyTable

from lecture_system import constants
from lecture_system.types import Speaker
from lecture_system.sensor_processing import measure_with_sensors, update_speaker_gain

app = Flask(__name__)

PROCESSING = False
live_speaker_outputs = constants.SPEAKER_ARRAY

@app.route('/')  
def main():
    """
    The main dashboard.
    Demonstrates that we can access the values of vars on demand.
    TODO: Display these vars live
    """
    global live_speaker_outputs
    table = PrettyTable(['Speaker', 'Loudness', 'Gain', 'Position'])
    for i in range(len(live_speaker_outputs)):
        speaker = live_speaker_outputs[i]
        table.add_row([i, f"{speaker.loudness:0.2f}", f"{speaker.gain:0.2f}", speaker.position])
    return table.get_html_string()


@app.route('/start')
def start_processing_microphone_input():
    """
    The background thread that is reading the audio file.
    Theoretically should also be calling back into the output function to play the transformed audio...
    Demonstrates that we can modify the speaker loudness in the background in realtime.
    """
    global PROCESSING
    PROCESSING = True
    global live_speaker_outputs
    while PROCESSING:
        for i in range(len(live_speaker_outputs)):
            speaker = live_speaker_outputs[i]
            live_speaker_outputs[i] = Speaker(speaker.loudness + 0.001, speaker.gain, speaker.position)
        sensors = measure_with_sensors(live_speaker_outputs)
        live_speaker_outputs = update_speaker_gain(live_speaker_outputs, sensors)
    return ""


@app.route('/stop')
def stop_processing_microphone_input():
    """Just handy to have to reset things, kills the processing thread"""
    global PROCESSING
    PROCESSING = False
    global live_speaker_outputs
    live_speaker_outputs = constants.SPEAKER_ARRAY
    return ""


if __name__ == '__main__': 
    app.run(threaded=True)