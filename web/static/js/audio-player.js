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
        // WaveSurfer.playhead.create({
        //     returnOnPause: true,
        //     moveOnSeek: true,
        //     draw: true
        // })
    ]
});

playBtn.onclick = function (){
    wavesurfer.playPause();
}



var pleerBlock1 = document.getElementById('pleer-1')

function initPlayer(audio) {
    // zoomSlider.oninput = function (){
    //     wavesurfer.zoom(Number(this.value));
    // };

    pleerBlock1.style.display = "block"
// Load audio from URL
    wavesurfer.load(audio);
}