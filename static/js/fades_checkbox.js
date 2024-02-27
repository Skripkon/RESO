$(document).ready(function () {
    $('#AlgoAddFades').change(function () {
        var addFades = document.getElementById('AlgoAddFades');
        var fadesContainer = document.getElementById('EditAlgoTrackFadesContainer');
        if (addFades.checked) {
            $('#EditAlgoTrackFadesContainer').show();
        } else {
            $('#EditAlgoTrackFadesContainer').hide();
        }
    });
});