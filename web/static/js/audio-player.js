var playBtn = document.getElementById('play')
var pleerBlock = document.getElementById('pleer-1')
var pleerProcessedBlock = document.getElementById('pleer-2')
var zoomSlider = document.getElementById('zoom-1')
var zoomSlider2 = document.getElementById('zoom-2')
var playBtn2 = document.getElementById('play-2')
var playBtnActive = document.getElementById('play-active-1')
var playBtn2Active = document.getElementById('play-active-2')
var playBtnStop = document.getElementById('play-stop-1')
var playBtn2Stop = document.getElementById('play-stop-2')



let wavesurfer = WaveSurfer.create({
    // height: 80,
    // waveColor: '#26f0df',
    // progressColor: '#224ab1',
    // barWidth: 1,
    // barHeight: 1, // the height of the wave


    waveColor: '#afb4ff',
    progressColor: '#4353FF',
    cursorColor: '#4353FF',
    barWidth: 2,
    barRadius: 2,
    cursorWidth: 2,
    height: 80,
    barGap: 3,

    container: '#waveform',
    backend: 'MediaElement',
    plugins: [
        WaveSurfer.regions.create({})
    ]
});

playBtn.onclick = function (){
    wavesurfer.playPause();
}


// var zoomSlider = document.getElementById('slider')

let wavesurfer2 = WaveSurfer.create({
    // height: 80,
    // waveColor: '#26f0df',
    // progressColor: '#224ab1',
    // barWidth: 1,
    // barHeight: 1, // the height of the wave

    waveColor: '#afb4ff',
    progressColor: '#4353FF',
    cursorColor: '#4353FF',
    barWidth: 2,
    barRadius: 2,
    cursorWidth: 2,
    height: 80,
    barGap: 3,

    container: '#waveform-2',
    backend: 'MediaElement',
    plugins: [
        WaveSurfer.regions.create({})
    ]
});



function initPlayer(audio) {
    zoomSlider.oninput = function (){
        wavesurfer.zoom(Number(this.value));
    };

    pleerBlock.style.display = "block"
    wavesurfer.load(fileServerAPI + audio);
}



function initPlayerProcessed(cutAudio) {
    zoomSlider2.oninput = function (){
        wavesurfer2.zoom(Number(this.value));
    };

    pleerProcessedBlock.style.display = "block"
    wavesurfer2.load(fileServerAPI + cutAudio);
}

playBtn2.onclick = function (){
    wavesurfer2.playPause();
}

wavesurfer.on('play', function () {
    playBtnActive.style.display = 'block';
    playBtnStop.style.display = 'none';
});

wavesurfer.on('pause', function () {
    playBtnActive.style.display = 'none';
    playBtnStop.style.display = 'block';
});

wavesurfer2.on('play', function () {
    playBtn2Active.style.display = 'block';
    playBtn2Stop.style.display = 'none';
});

wavesurfer2.on('pause', function () {
    playBtn2Active.style.display = 'none';
    playBtn2Stop.style.display = 'block';
});


