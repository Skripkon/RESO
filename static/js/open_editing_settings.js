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

    $('#EditNeuroTrackButton').click(function () {
        var editButton = document.getElementById('EditNeuroTrackButton');
        var editContainer = document.getElementById('EditNeuroTrackContainer');
        if (editButton.innerText === "Edit track") {
            // editContainer.style.display = 'flex';
            $('#EditNeuroTrackContainer').show();
            editButton.innerText = "Hide editing settings";
        } else {
            // editContainer.style.display = 'none';
            $('#EditNeuroTrackContainer').hide();
            editButton.innerText = "Edit track";
        }
    });
});