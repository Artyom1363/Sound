$(document).ready(function () {
    $('#summernote').summernote({
        toolbar: [
            // ['color', ['color']],
            //['view', ['codeview']],
            ['mybutton', ['bad', 'parasite', 'trash']]
        ],
        height: 120,
        styleTags: [
            'p',
        ],
        buttons: {
            trash: TrashButton,
            bad: BadButton,
            parasite: ParasiteButton,
        }
    });
});

textEditorBlock = document.getElementById('text-editor')
let transcription;

async function initEditor(textPath, transcriptionPath) {
    textEditorBlock.style.display = "block"
    await new Promise(r => setTimeout(r, 500));
    fetch(fileServerAPI + textPath).then(async response => {
        $('#summernote').summernote('reset');
        $('#summernote').summernote('pasteHTML', await response.text());
    }).catch(err => {
        alert(err)
    })

    fetch(fileServerAPI + transcriptionPath).then(async response => {
        transcription = JSON.parse(await response.text())
    }).catch(err => {
        alert(err)
    })
}

function parseHTML(html) {
    var t = document.createElement('template');
    t.innerHTML = html;
    return t.content;
}

var ParasiteButton = function (context) {
    var ui = $.summernote.ui;
    // create button
    var button = ui.button({
            contents: '<svg xmlns="http://www.w3.org/2000/svg" id="marker-add-bad" width="24" height="24" style="color:#ffd900;" fill="currentColor" class="bi bi-align-middle" viewBox="0 0 16 16">\n' +
                '         <path d="M6 13a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V3a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1v10zM1 8a.5.5 0 0 0 .5.5H6v-1H1.5A.5.5 0 0 0 1 8zm14 0a.5.5 0 0 1-.5.5H10v-1h4.5a.5.5 0 0 1 .5.5z"/>\n' +
                '      </svg> Вырезать',
            tooltip: 'parasite',
            click: function (){
                createTextRegion('parasite', "hsla(50, 100%, 50%, 0.5)");
            }
        }
    );

    return button.render();   // return button as jquery object
}

var BadButton = function (context) {
    var ui = $.summernote.ui;
    // create button
    var button = ui.button({
            contents: '<svg xmlns="http://www.w3.org/2000/svg" id="marker-add-bad" width="24" height="24" style="color:red;" fill="currentColor" class="bi bi-align-middle" viewBox="0 0 16 16">\n' +
                '         <path d="M6 13a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V3a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1v10zM1 8a.5.5 0 0 0 .5.5H6v-1H1.5A.5.5 0 0 0 1 8zm14 0a.5.5 0 0 1-.5.5H10v-1h4.5a.5.5 0 0 1 .5.5z"/>\n' +
                '      </svg> Запикать',
            tooltip: 'bad',
            click: function (){
                createTextRegion('bad', "hsla(0, 100%, 50%, 0.5)");
            }
        }
    );

    return button.render();   // return button as jquery object
}

function createTextRegion(regionType, color) {
        var range = $('#summernote').summernote('createRange')
        if (range.sc.data !== range.ec.data) {
            alert("Текст должен быть выделен в одном цветовом блоке")
        }

        let startBlock = transcription.text.indexOf(range.sc.data)
        console.log(transcription.text)
        console.log(range.sc.data)
        if (startBlock === -1) {
            alert("Данные блока не найдены")
            return
        }
        let startPos = startBlock + range.so;
        let endPos = startBlock + range.eo;

        let startWordInd = transcription.text.slice(0,startPos).split(" ").length - 1;
        let endWordInd = transcription.text.slice(0,endPos).split(" ").length - 1;

        let start = transcription.words[startWordInd].start;
        let end = transcription.words[endWordInd].end;
        let regionId = addRegion(start, end, regionType);

        let data = range.sc.data;
        let startTextRegion = data.slice(0, range.so).lastIndexOf(" ") + 1;
        let endTextRegion = data.indexOf(" ", range.eo);
        let startFragment = data.slice(0, startTextRegion);
        let centerFragment = data.slice(startTextRegion, endTextRegion);
        let endFragment = data.slice(endTextRegion);

        let newData = `${startFragment}<span style="background-color: ${color};" id="marker-${regionId}">${centerFragment}</span>${endFragment}`;
        range.sc.replaceWith(parseHTML(newData));
        console.log(newData)
        // $('#summernote').summernote('pasteHTML', newData);
        // $('#summernote').summernote('pasteHTML', '<span style="background-color: rgb(255, 0, 0);">' + range.toString() + '</span>');
        // <span style="background-color: rgb(255, 255, 0);">Hehehe</span>
}

var TrashButton = function (context) {
    var ui = $.summernote.ui;
    // create button
    var button = ui.button({
        contents: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16">\n' +
            '  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5Zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6Z"/>\n' +
            '  <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1ZM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118ZM2.5 3h11V2h-11v1Z"/>\n' +
            '</svg> Удалить маркер',
        tooltip: 'trash',
        click: function () {
            var range = $('#summernote').summernote('createRange')
            if (range.sc.data !== range.ec.data) {
                alert("Текст должен быть выделен в одном цветовом блоке")
            }

            let regionId = range.sc.parentNode.id.slice(7);
            removeRegion(regionId);
            removeTextRegion(regionId);
        }
    });

    return button.render();
}

function removeTextRegion(regionId) {
    let element = document.getElementById(`marker-${regionId}`);
    if (element) {
        let newData = element.firstChild.data;
        element.replaceWith(parseHTML(newData));
    }
}