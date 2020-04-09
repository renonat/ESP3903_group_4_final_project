def microphoneInputReader():
    """
    Process the audio input stream, and broadcast updates to the frontend webpage
    """
    # Reading the microphone
    audio = AudioInput('data/ESP3903_lecture1.wav')

    # Initialize Data
    speakers = [Speaker(pos) for pos in SPEAKER_POSITIONS]
    sensors = [Sensor(pos, speakers) for pos in SENSOR_POSITIONS]
    controller = Controller(speakers, sensors)

    # Allow for lecturer to control the loudness setpoint
    @socketio.on('set target')
    def handle_set_target(value):
        controller.target_dB = float(value)

    controller.streamAudio(audio)

    output_data = []
    block_counter = 0
    while not thread_stop_event.isSet() and not audio.isFinished():
        _start = timer()

        # Process the current audio block with the system controller
        audio.nextBlock()
        controller.update()
        if audio.loudness > 20:
            controller.adjustGains()

        # Choose speaker[0] as the output track source
        # Modulate the input track amplitude by the speaker's gain
        # Write the modulated data to the output file
        output_block = audio.block * 10**(speakers[0].gain/20)
        output_data.extend([list(m) for m in output_block])

        if block_counter % 10 == 0:
            # Update the webpage every 10th block
            socketio.emit('system_update', {'data': {
                "readings" : dataToDict(speakers, sensors),
                "eventcounter": block_counter,
                "roomlayout": generate_html_room_display(speakers, sensors)
            }})

        _end = timer()

        # Sleep the thread, so that the audio processing occurs in real time
        sleep_time = max(0, audio.block_len_s - (_end - _start))
        socketio.sleep(sleep_time)
        block_counter += 1


@socketio.on('connect')
def connect():
    thread = socketio.start_background_task(microphoneInputReader)


if __name__ == '__main__':
    socketio.run(app, debug=False)
