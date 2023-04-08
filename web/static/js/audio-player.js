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



var pleerBlock1 = document.getElementById('pleer-1')

// pleerBlock1.style.display = "block"
// wavesurfer.load(fileServerAPI + "/static/media/example.mp3");


function initPlayer(audio) {
    // zoomSlider.oninput = function (){
    //     wavesurfer.zoom(Number(this.value));
    // };
    // wavesurfer.

    pleerBlock1.style.display = "block"
// Load audio from URL
    wavesurfer.load(fileServerAPI + audio);
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