var processActiveSpin = document.getElementById('process-active')
// var processBtn = document.getElementById('process')

function showProcessStart() {
    processActiveSpin.style.display = "block";
}
function showProcessStop() {
    processActiveSpin.style.display = "none";
}

function process(audioLink) {
    showProcessStart()

    fetch(processAPI + new URLSearchParams({
        audio: audioLink,
    })).then(response => {
        // alert("ok")
    }).catch(err => {
        alert(err)
    })
}

function processFinish(mess) {
    showProcessStop()
    initPlayer(mess.audio)
    initPlayerProcessed(mess.cutAudio)
    initEditor(mess.text)
    initRegions(mess.audioMarkers)
    initDownload(mess.cutAudio)
}

processFinish({
    audio: "fileserver/oJBfrc9SoT_cut.mp3",
    cutAudio: "fileserver/oJBfrc9SoT_cut.mp3",
    text: "fileserver/koCRssEDnV.txt",
    audioMarkers: "fileserver/3eDh5rOdih.txt",
});

// processBtn.onclick = function () {
//     mysocket.showMessage()
// }


