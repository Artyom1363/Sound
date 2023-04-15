$(document).ready(function () {
    $('#summernote').summernote({
        toolbar: [
            // ['color', ['color']],
            // ['view', ['codeview']],
        ],
        height: 120,
        styleTags: [
            'p',
        ],
    });
});

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