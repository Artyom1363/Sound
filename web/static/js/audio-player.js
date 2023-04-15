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
let regionsCounts;

function initRegions(filePath) {
    fetch(fileServerAPI + filePath).then(async response => {
        var regs = JSON.parse(await response.text())
        regionsCounts = 0;
        for (region of regs) {
            wavesurfer.addRegion({
                id: `${regionsCounts}`,
                start: region.Start,
                end: region.End,
                loop: false,
                color: getRegionColorByType(region.Type)
            });
            regionsCounts++;
        }
        wavesurfer.region
    }).catch(err => {
        alert(err)
    })
}

function getRegionColorByType(type) {
    switch (type){
        case "bad":
            return 'hsla(0, 100%, 50%, 0.4)'
        case "parasite":
            return 'hsla(50, 100%, 50%, 0.4)'
        case "mezdo":
            return 'hsla(169, 0%, 50%, 0.4)'
    }
}

function getRegionTypeByColor(color) {
    switch (color){
        case "hsla(0, 100%, 50%, 0.4)":
            return "bad"
        case "hsla(50, 100%, 50%, 0.4)":
            return "parasite"
        case "hsla(169, 0%, 50%, 0.4)":
            return "mezdo"
    }
}