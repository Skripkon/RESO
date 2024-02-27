$(document).ready(function () {
    $('#EditAlgoTrackButton').click(function () {
        var editButton = document.getElementById('EditAlgoTrackButton');
        var editContainer = document.getElementById('EditAlgoTrackContainer');
        if (editButton.innerText === "Edit track") {
            // editContainer.style.display = 'flex';
            $('#EditAlgoTrackContainer').show();
            editButton.innerText = "Hide editing settings";
        } else {
            // editContainer.style.display = 'none';
            $('#EditAlgoTrackContainer').hide();
            editButton.innerText = "Edit track";
        }
    });
});