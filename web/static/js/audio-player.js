var playBtn = document.getElementById('play')
// var zoomSlider = document.getElementById('slider')

let wavesurfer = WaveSurfer.create({
    height: 80,
    container: '#waveform',
    waveColor: '#26f0df',
    progressColor: '#224ab1',
    barWidth: 1,
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
    height: 80,
    container: '#waveform-2',
    waveColor: '#26f0df',
    progressColor: '#224ab1',
    barWidth: 1,
    barHeight: 1, // the height of the wave
    backend: 'MediaElement',
    plugins: [
        WaveSurfer.regions.create({})
    ]
});

playBtn2.onclick = function (){
    wavesurfer2.playPause();
}

var pleerBlock = document.getElementById('pleer-1')
var zoomSlider = document.getElementById('zoom-1')
var zoomSlider2 = document.getElementById('zoom-2')

function initPlayer(audio) {
    zoomSlider.oninput = function (){
        wavesurfer.zoom(Number(this.value));
    };

    pleerBlock.style.display = "block"
    wavesurfer.load(fileServerAPI + audio);
}

var pleerProcessedBlock = document.getElementById('pleer-2')

function initPlayerProcessed(cutAudio) {
    zoomSlider2.oninput = function (){
        wavesurfer2.zoom(Number(this.value));
    };

    pleerProcessedBlock.style.display = "block"
    wavesurfer2.load(fileServerAPI + cutAudio);
}
