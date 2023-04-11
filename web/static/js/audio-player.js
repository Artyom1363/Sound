var playBtn = document.getElementById('play')
// var zoomSlider = document.getElementById('slider')

let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#26f0df',
    progressColor: '#224ab1',
    barWidth: 3,
    barHeight: 1, // the height of the wave
    backend: 'MediaElement',
    plugins: [
        WaveSurfer.regions.create({})
    ]
});

playBtn.onclick = function (){
    wavesurfer.playPause();
}

var playBtn2 = document.getElementById('play-2')
// var zoomSlider = document.getElementById('slider')

let wavesurfer2 = WaveSurfer.create({
    container: '#waveform-2',
    waveColor: '#26f0df',
    progressColor: '#224ab1',
    barWidth: 3,
    barHeight: 1, // the height of the wave
    backend: 'MediaElement',
    plugins: [
        WaveSurfer.regions.create({})
    ]
});

playBtn2.onclick = function (){
    wavesurfer2.playPause();
}




// pleerBlock1.style.display = "block"
// wavesurfer.load(fileServerAPI + "/static/media/example.mp3");

var pleerBlock = document.getElementById('pleer-1')

function initPlayer(audio) {
    // zoomSlider.oninput = function (){
    //     wavesurfer.zoom(Number(this.value));
    // };
    // wavesurfer.

    pleerBlock.style.display = "block"
    wavesurfer.load(fileServerAPI + audio);
}

var pleerProcessedBlock = document.getElementById('pleer-2')

function initPlayerProcessed(cutAudio) {
    // zoomSlider.oninput = function (){
    //     wavesurfer.zoom(Number(this.value));
    // };
    // wavesurfer.

    pleerProcessedBlock.style.display = "block"
    wavesurfer2.load(fileServerAPI + cutAudio);
}

// let regs = [{
//     start: 2.68,
//     end: 3.44
// },
//     {
//         start: 5.68,
//         end: 7.44
//     }]
//
// initRegions(regs);

function initRegions(filePath) {
    fetch(fileServerAPI + filePath).then(async response => {
        var regs = JSON.parse(await response.text())

        for (r of regs) {
            wavesurfer.addRegion({
                start: r.start,
                end: r.end,
                loop: false,
                color: 'hsla(0,2%,32%,0.5)'
            });
        }
    }).catch(err => {
        alert(err)
    })
}