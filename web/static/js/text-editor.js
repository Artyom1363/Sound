$(document).ready(function() {
    $('#summernote').summernote({
        toolbar: [
            // [groupName, [list of button]]
            // ['style', ['bold', 'italic', 'underline', 'clear', 'mark1']],
            ['color', ['color']],
            ['view', ['codeview']],
        ],
        height: 200,
        styleTags: [
            'p',
            {
                tag : 'm1',
                title : 'hehehe',
                style : 'background-color: rgb(255, 255, 0);',
                className : 'applyed element class name and dropdown item className',
                value : 'Value to apply when clicked'
            },
            'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        ],
    });
});

textEditorBlock = document.getElementById('text-editor')

function initEditor(filePath) {
    textEditorBlock.style.display = "block"
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