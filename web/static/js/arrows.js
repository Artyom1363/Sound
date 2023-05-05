var lineNoteHealth = new LeaderLine(
    document.getElementById('note-health'),
    document.getElementById('foot'),
    {
        color: 'grey',
        size: 2,
        dash: true
    }
);

var lineNoteUpload = new LeaderLine(
    document.getElementById('note-upload'),
    document.getElementById('upload-form'),
    {
        color: 'grey',
        size: 2,
        dash: true,
        startSocket: 'left'
    }
);