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
            alert( 'Oops! Something went wrong.' );
        } );

        // Set up our request
        XHR.open( "POST",  uploadAPI);

        // The data sent is what the user provided in the form
        XHR.send( FD );
    }

    // Access the form element...
    const form = document.getElementById( "myForm" );

    // ...and take over its submit event.
    form.addEventListener( "submit", function ( event ) {
        event.preventDefault();
        showLoadStart();

        sendData();
    } );
} );

var loadBtn = document.getElementById('load')
var loadActiveBtn = document.getElementById('load-active')

function showLoadStart () {
    loadBtn.style.display = "none";
    loadActiveBtn.style.display = "block";
}

function showLoadStop () {
    loadBtn.style.display = "block";
    loadActiveBtn.style.display = "none";
}