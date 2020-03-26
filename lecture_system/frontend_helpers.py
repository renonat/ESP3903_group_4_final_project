from prettytable import PrettyTable, NONE, FRAME  # type: ignore
from typing import List

from lecture_system.types import Speaker, Sensor


def formatted_speaker_data(speakers: List[Speaker]) -> str:
    """Used to display pretty speaker data on the webpage"""
    table = PrettyTable(['Speaker', 'Loudness', 'Gain', 'Position'])
    for i in range(len(speakers)):
        speaker = speakers[i]
        table.add_row([i, f"{speaker.loudness:0.2f}", f"{speaker.gain:0.2f}", speaker.position])
    return table.get_html_string()


def generate_html_room_display(speakers: List[Speaker], sensors: List[Sensor]) -> str:
    # Add extra 2 units on each side of the room for padding
    x_min = min([s.position.x for s in speakers] + [s.position.x for s in sensors]) - 2
    x_max = max([s.position.x for s in speakers] + [s.position.x for s in sensors]) + 3
    y_min = min([s.position.y for s in speakers] + [s.position.y for s in sensors]) - 2
    y_max = max([s.position.y for s in speakers] + [s.position.y for s in sensors]) + 3
    
    table = PrettyTable(header=False, vrules=NONE, hrules=NONE)

    # Generate the room array
    room_arr = [["." for i in range(x_min, x_max)] for j in range(y_min, y_max)]
    # Place the speaker and sensor emoji, as well as live readout data below
    for speaker in speakers:
        room_arr[speaker.position.y + 2][speaker.position.x + 2] = "🔊"
        room_arr[speaker.position.y + 3][speaker.position.x + 2] = f"{speaker.loudness:0.2f}dB"
    for sensor in sensors:
        room_arr[sensor.position.y + 2][sensor.position.x + 2] = "🎙️"
        room_arr[sensor.position.y + 3][sensor.position.x + 2] = f"{sensor.loudness:0.2f}dB"

    for row in room_arr:
        table.add_row(row)
    return table.get_html_string(format=True)

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