$(document).ready(function() {
    $('#summernote').summernote({
        toolbar: [
            // [groupName, [list of button]]
            // ['style', ['bold', 'italic', 'underline', 'clear', 'mark1']],
            ['color', ['color']],
        ],
        height: 200,
        styleTags: [
            'p',
            { title: 'Blockquote', tag: 'blockquote', className: 'blockquote', value: 'blockquote' },
            'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        ],
            // {
            //     tag : 'mark1',
            //     title : 'dropdown item title',
            //     style : 'dropdown item style',
            //     className : 'applyed element class name and dropdown item className',
            //     value : 'Value to apply when clicked'
            // }
        // ],
    });
});