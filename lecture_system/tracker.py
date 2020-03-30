import csv

class Tracker():
    def __init__(self, speakers, sensors):
        self.speakers = speakers
        self.sensors = sensors

        self.speaker_loudness = []
        self.speaker_gains = []
        self.sensor_values = []

    def update(self):
        self.speaker_loudness.append([s.getLoudness() for s in self.speakers])
        self.speaker_gains.append([s.gain for s in self.speakers])
        self.sensor_values.append([s.getSensorValue() for s in self.sensors])

    def write_csv(self):
        with open('data/output.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['input_loudness'] +
                    ['speaker_{}_loudness'.format(i) for i in range(len(self.speakers))] +
                    ['speaker_{}_gain'.format(i) for i in range(len(self.speakers))] +
                    ['sensor_{}_loudness'.format(i) for i in range(len(self.sensors))])
            for l, g, v in zip(self.speaker_loudness, self.speaker_gains, self.sensor_values):
                writer.writerow([l[0] - g[0]] + l + g + v)

        
