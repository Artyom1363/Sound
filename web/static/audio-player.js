var playBtn = document.getElementById('play')
var zoomSlider = document.getElementById('slider')

let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#A8DBA8',
    progressColor: '#3B8686',
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

zoomSlider.oninput = function (){
    wavesurfer.zoom(Number(this.value));
};


// Load audio from URL
wavesurfer.load('media/audio.mp3');

