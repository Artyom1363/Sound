$(document).ready(function () {
    $('#summernote').summernote({
        toolbar: [
            // ['color', ['color']],
            ['view', ['codeview']],
            ['mybutton', ['bad']]
        ],
        height: 120,
        styleTags: [
            'p',
        ],
        buttons: {
            bad: BadButton
        }
    });
});

var BadButton = function (context) {
    var ui = $.summernote.ui;

    // create button
    var button = ui.button({
        contents: '<svg xmlns="http://www.w3.org/2000/svg" id="marker-add-bad" width="24" height="24" style="color:red;" fill="currentColor" class="bi bi-align-middle" viewBox="0 0 16 16">\n' +
            '         <path d="M6 13a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V3a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1v10zM1 8a.5.5 0 0 0 .5.5H6v-1H1.5A.5.5 0 0 0 1 8zm14 0a.5.5 0 0 1-.5.5H10v-1h4.5a.5.5 0 0 1 .5.5z"/>\n' +
            '      </svg> Запикать',
        tooltip: 'hello',
        click: function () {
            // invoke insertText method with 'hello' on editor module.

            var range = $('#summernote').summernote('createRange')

            // context.invoke('editor.insertHTML', '<span style="background-color: rgb(255, 0, 0);">hello</span>');
            $('#summernote').summernote('pasteHTML', '<span style="background-color: rgb(255, 0, 0);">' + range.toString() + '</span>');

        }
    });

    return button.render();   // return button as jquery object
}

textEditorBlock = document.getElementById('text-editor')

async function initEditor(filePath) {
    textEditorBlock.style.display = "block"
    await new Promise(r => setTimeout(r, 500));
    fetch(fileServerAPI + filePath).then(async response => {
        $('#summernote').summernote('reset');
        $('#summernote').summernote('pasteHTML', await response.text());
    }).catch(err => {
        alert(err)
    })
}


// var getTextBtn = document.getElementById('get-text')
//
// getTextBtn.onclick = function () {
//     fetch(getTextAPI + new URLSearchParams({
//         text: $($('#summernote').summernote('code')).text(),
//     })).then(async response => {
//         $('#summernote').summernote('reset');
//         $('#summernote').summernote('pasteHTML', await response.text());
//     }).catch(err => {
//         alert(err)
//     })
// }