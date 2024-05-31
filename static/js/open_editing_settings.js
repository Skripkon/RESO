$(document).ready(function () {
    $('#EditAlgoTrackButton').click(function () {
        var editButton = document.getElementById('EditAlgoTrackButton');
        var editContainer = document.getElementById('EditAlgoTrackContainer');
        if (editButton.innerText === "Edit track") {
            $('#EditAlgoTrackContainer').show();
            editButton.innerText = "Hide editing settings";
        } else {
            $('#EditAlgoTrackContainer').hide();
            editButton.innerText = "Edit track";
        }
    });

    $('#EditNeuroTrackButton').click(function () {
        var editButton = document.getElementById('EditNeuroTrackButton');
        var editContainer = document.getElementById('EditNeuroTrackContainer');
        if (editButton.innerText === "Edit track") {
            $('#EditNeuroTrackContainer').show();
            editButton.innerText = "Hide editing settings";
        } else {
            $('#EditNeuroTrackContainer').hide();
            editButton.innerText = "Edit track";
        }
    });
});