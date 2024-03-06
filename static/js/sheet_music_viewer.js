$(document).ready(function() {
    $('#ViewSheetMusicButton').click(function() {
        openPdf();
    });

    $('#close-button').click(function() {
        var overlay = $('#overlay');
        var pdfContainer = $('#pdf-container');

        overlay.css('display', 'none');
        pdfContainer.css('display', 'none');
    });

    function openPdf() {
        var overlay = $('#overlay');
        var pdfContainer = $('#pdf-container');

        overlay.css('display', 'block');
        pdfContainer.css('display', 'block');
    }
});

