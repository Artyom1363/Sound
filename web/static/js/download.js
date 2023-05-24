downloadBlock = document.getElementById('download-block')
downloadBtn = document.getElementById('download')
renderBtn = document.getElementById('render')
renderSpin = document.getElementById('render-active')

let resultAudio;

function initDownload(audio) {
    downloadBlock.style.display = "block";
    resultAudio = audio
}

downloadBtn.onclick = function() {
    const a = document.createElement('a')
    a.href = fileServerAPI + resultAudio
    a.download = "(sweetvoice)" + srcFileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
}

renderBtn.onclick = function() {
    showRenderStart();
    let data = {
        filepath: lastProcess.audio,
        markers: [],
    };

    for (let id = 0; id < regionsCounts; id++){
        if (!regionsDeleted.has(id)) {
            data.markers.push({
                Start: wavesurfer.regions.list[`${id}`].start,
                End: wavesurfer.regions.list[`${id}`].end,
                Type: getRegionTypeByColor(wavesurfer.regions.list[`${id}`].color)
            })
        }
    }

    fetch(renderAPI, {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        credentials: "same-origin", // include, *same-origin, omit
        headers: {
            "Content-Type": "application/json",
            // 'Content-Type': 'application/x-www-form-urlencoded',
        },
        redirect: "follow", // manual, *follow, error
        referrerPolicy: "no-referrer", // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        body: JSON.stringify(data), // body data type must match "Content-Type" header
    }).then(async response => {
        res = await response.text()
        initPlayerProcessed(res)
        initDownload(res)
        showRenderStop();
    }).catch(err => {
        alert(err)
        showRenderStop();
    })

}

function showRenderStart () {
    renderBtn.style.display = "none";
    renderSpin.style.display = "block";
}

function showRenderStop () {
    renderBtn.style.display = "block";
    renderSpin.style.display = "none";
}