$(document).ready(function() {
    $('#ViewSheetMusicButton').click(function() {
        openPdf();
    });

    function openPdf() {
        var overlay = $('#overlay');
        var pdfContainer = $('#pdf-container');

        overlay.css('display', 'block');
        pdfContainer.css('display', 'block');
    }

    var overlay = $("#overlay");
    var pdf_container = $("#pdf-container");

    overlay.on("click", function(event) {
      if (event.target === overlay[0]) {
        overlay.css("display", "none");
        pdf_container.css("display", "none");
      }
    });
});