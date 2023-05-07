var processActiveBlock = document.getElementById('process-active')
var processActiveSpin = document.getElementById('process-active-spin')
var processActiveInfo = document.getElementById('process-active-info')
var welcomeBlock = document.getElementById('welcome-block')

function showProcessStart() {
    processActiveBlock.style.display = "block";
    processActiveSpin.style.display = "block";
    loadBtn.disabled = true;
    loadFileField.disabled = true;

    welcomeBlock.style.display = "none";
    lineNoteUpload.hide();
    lineNoteHealth.hide();

    textEditorBlock.style.display = "none";
    pleerBlock.style.display = "none";
    pleerProcessedBlock.style.display = "none";
    downloadBlock.style.display = "none";

    wavesurfer.clearRegions();
}

function showProcessStop() {
    processActiveBlock.style.display = "none";
    processActiveInfo.innerHTML = '';
    loadBtn.disabled = false;
    loadFileField.disabled = false;
}

function showProcessPause() {
    processActiveSpin.style.display = "none";
    loadBtn.disabled = false;
    loadFileField.disabled = false;
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

let lastProcess;

async function processFinish(mess) {
    await new Promise(r => setTimeout(r, 3000));
    lastProcess = mess;

    showProcessStop()
    initPlayer(mess.audio)
    initPlayerProcessed(mess.cutAudio)
    initEditor(mess.text)
    initRegions(mess.audioMarkers)
    initDownload(mess.cutAudio)
}

function processInfo(mess) {
    var infoDiv = document.createElement('div');
    // div.setAttribute('class', 'post block bc2');

    let title;
    switch (mess.module) {
        case "transpile":
            title = "Распознование текста, поиск матов"
            break;
        case "parasite":
            title = "Поиск слов паразитов"
            break;
        case "mezdo":
            title = "Поиск междометий"
            break;
        case "textmarkers":
            title = "Обогащение текста маркерами"
            break;
        case "audiomarkers":
            title = "Обогащение аудио маркерами"
            break;
        case "cutter":
            title = "Обработка аудио"
            break;
    }


    switch (mess.status) {
        case "info":
            infoDiv.innerHTML = `
                ${title}
                <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" style="color:green;" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16">
                    <path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"/>
                </svg>
            `
            break;
        case "error":
            infoDiv.innerHTML = `
                ${title}
                <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" style="color:red;" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16">
                  <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
                </svg>
                <p style="color:red;">Ошибка: ${mess.error}</p>
            `
            break;
    }

    processActiveInfo.append(infoDiv)
}