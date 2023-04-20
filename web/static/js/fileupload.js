let srcFileName;

window.addEventListener( "load", function () {
    function sendData() {
        const XHR = new XMLHttpRequest();

        // Bind the FormData object and the form element
        const FD = new FormData( form );

        // Define what happens on successful data submission
        XHR.addEventListener( "load", function(event) {
            showLoadStop();
            process(event.target.responseText);
            // alert( event.target.responseText );
            // initPlayer(event.target.responseText);
        } );

        // Define what happens in case of error
        XHR.addEventListener( "error", function( event ) {
            showLoadStop();
            showUploadError();
        } );

        // Set up our request
        XHR.open( "POST",  uploadAPI);

        // The data sent is what the user provided in the form
        XHR.send( FD );
    }

    // Access the form element...
    const form = document.getElementById("myForm");

    // ...and take over its submit event.
    form.addEventListener( "submit", function ( event ) {
        event.preventDefault();
        // getAudioDuration(form.uploadfile.value);
        showLoadStart();
        hideUploadError();
        srcFileName = form.uploadfile.value.split(/(\\|\/)/g).pop()

        sendData();
    } );
} );

var loadBtn = document.getElementById('load')
var loadActiveBtn = document.getElementById('load-active')
var loadFileField = document.getElementById('upfile')
var uploadError = document.getElementById('upload-error')

function showLoadStart () {
    loadBtn.style.display = "none";
    loadActiveBtn.style.display = "block";
}

function showLoadStop () {
    loadBtn.style.display = "block";
    loadActiveBtn.style.display = "none";
}

function showUploadError() {
    uploadError.style.display = "block";
}

function hideUploadError() {
    uploadError.style.display = "none";
}


// Create a non-dom allocated Audio element
var audio = document.createElement('audio');

// Add a change event listener to the file input
function getAudioDuration(file) {
    var reader = new FileReader();

    console.log("Start" + file);
    if (file) {
        var reader = new FileReader();

        reader.onload = function (e) {
            audio.src = file;
            audio.addEventListener('loadedmetadata', function(){
                // Obtain the duration in seconds of the audio file (with milliseconds as well, a float value)
                var duration = audio.duration;

                // example 12.3234 seconds
                console.log("The duration of the song is of: " + duration + " seconds");
                // Alternatively, just display the integer value with
                // parseInt(duration)
                // 12 seconds
            },false);
        };
        reader.readAsDataURL(file);
    }
}