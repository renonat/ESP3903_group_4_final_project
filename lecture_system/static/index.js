function initializeChart(DOMelement) {
    const ms = 40; // margin size
    const layout_template = {
        title: formatName(DOMelement.id),
        margin: { l: ms, r: ms, t: ms, b: ms+20 },
        padding: 40,
        legend: { orientation: 'h' },
        xaxis: { title: "Time" },
        yaxis: { title: "Loudness (dB)" },
        yaxis2: { title: "Gain (db) ", side: "right", overlaying: "y"},
        autosize: true,
        height: 320,
        font: { family: "arial" }
    };
    const config = {
        displayModeBar: false,
        responsive: true
    };
    let traces = [{
        name: "Loudness",
        y: [0],
        mode: 'lines+markers', 
        marker: {color: '#6b46c1'}, 
    }];
    let isSpeaker = DOMelement.id.includes('speaker');
    
    if (isSpeaker) {
        traces.push({
            name: "Gain",
            y: [0],
            type: 'line',
            yaxis: 'y2',
            mode: 'lines+markers', 
            marker: {color: '#3182ce'},
        });
    }


    Plotly.newPlot(DOMelement, traces, layout_template, config)
}

function formatName(id) {
    const number = id.slice(-1);
    const type = id.charAt(0).toUpperCase() + id.slice(1, id.length - 1);
    return `${type} ${number}`;
}

function drawRoom(readings, ctx) {

    let grid = getGrid(readings);

    // draw grid points
    for (let i = 1; i < grid.dimensions.x; i++) {
        for (let j = 1; j < grid.dimensions.y; j++) {
        drawPoint(i, j, ctx, grid);
      }
    }

    // plot reading for each speaker and sensor
    readings.speakers.forEach((speaker, i) => {
        drawText(
            speaker.position[0], // x value
            speaker.position[1], // y value
            "🔊", `Speaker ${i+1}`, speaker.loudness.toFixed(2),
            ctx, grid
            );
    });

    readings.sensors.forEach((sensor, i) => {
        drawText(
            sensor.position[0],
            sensor.position[1],
            "🎤", `Sensor ${i+1}`, sensor.loudness.toFixed(2),
            ctx, grid
            );
    });

}

function getGrid(readings) {
    let room_width = 0; 
    let room_height = 0;

    // update max by iterating through each sensor
    readings.speakers.forEach(speaker => {
        if (speaker.position[0] > room_width)
            room_width = speaker.position[0];
        if (speaker.position[1] > room_height)
            room_height = speaker.position[1];
    });

    readings.sensors.forEach(sensor => {
        if (sensor.position[0] > room_width)
            room_width = sensor.position[0];
        if (sensor.position[1] > room_height)
            room_height = sensor.position[1];
    });

    // add two to width and height for padding
    let grid = {
        dimensions: { x: room_width + 2, y: room_height + 2}    
    };

    grid.steps = {
        x: Math.floor(canvas.width / grid.dimensions.x),
        y: Math.floor(canvas.height / grid.dimensions.y)
    };

    return grid;
}


function drawPoint(x, y, ctx, grid) {
    const size = 2;
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.fillRect(x * grid.steps.x - size / 2,
        y * grid.steps.y - size / 2,
        size, size);
}

// draw sensor stuff
function drawText(x, y, icon, name, reading, ctx, grid) {
    const fontSize = 16;
    const lineHeight = fontSize * 1.2;
    ctx.font = `${fontSize}px Arial`;
    ctx.fillStyle = 'black';
    ctx.textAlign = "center";

    x_coord = (x + 1) * grid.steps.x;
    y_coord = canvas.height - ((y + 1) * grid.steps.y);
  
    ctx.fillText(icon, x_coord, y_coord - lineHeight);
    ctx.fillText(name, x_coord, y_coord);
    ctx.fillText(reading, x_coord, y_coord + lineHeight);
}