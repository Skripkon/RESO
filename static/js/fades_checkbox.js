$(document).ready(function () {
    $('#AlgoAddFades').change(function () {
        var addFades = document.getElementById('AlgoAddFades');
        if (addFades.checked) {
            $('#EditAlgoTrackFadesContainer').show();
        } else {
            $('#EditAlgoTrackFadesContainer').hide();
        }
    });
});

$(document).ready(function () {
    $('#NeuroAddFades').change(function () {
        var addFades = document.getElementById('NeuroAddFades');
        if (addFades.checked) {
            $('#EditNeuroTrackFadesContainer').show();
        } else {
            $('#EditNeuroTrackFadesContainer').hide();
        }
    });
});