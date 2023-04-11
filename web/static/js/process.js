var processActiveSpin = document.getElementById('process-active')
var processBtn = document.getElementById('process')

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
    initPlayer(mess.audio);
    initPlayerProcessed(mess.cutAudio);
    initEditor(mess.text);
    initRegions(mess.audioMarkers)
}

processBtn.onclick = function () {
    mysocket.showMessage()
}


