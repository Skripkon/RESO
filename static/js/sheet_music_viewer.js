$(document).ready(function () {

  $('#ViewSheetMusicButton').click(function () {
    openPdf();
  });

  var overlay = $("#overlay");
  var pdf_container = $("#pdf-container");

  function openPdf() {
    overlay.css('display', 'block');
    pdf_container.css('display', 'block');
  }

  function closePdf() {
    overlay.css('display', 'none');
    pdf_container.css('display', 'none');
  }

  // If the click event's target is the overlay itself, the PDF viewer is closed
  overlay.on("click", function (event) {
    if (event.target === overlay[0]) {
      closePdf();
    }
  });

  // If the 'Escape' key is pressed, the PDF viewer is closed if it is visible
  $(document).on('keydown', function (event) {
    if (event.key === "Escape") {
      if (overlay.css('display') === 'block' || pdf_container.css('display') === 'block') {
        closePdf();
      }
    }
  });
});
