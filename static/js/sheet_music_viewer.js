$(document).ready(function() {
  $('#ViewSheetMusicButton').click(function() {
        openPdf();
  });

  var overlay = $("#overlay");
  var pdf_container = $("#pdf-container");

  function openPdf() {
    overlay.css('display', 'block');
    pdf_container.css('display', 'block');
  }

  overlay.on("click", function(event) {
    if (event.target === overlay[0]) {
      overlay.css("display", "none");
      pdf_container.css("display", "none");
    }
  });
});