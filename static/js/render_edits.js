$(document).ready(function () {
    $('#EditAlgoRenderButton').click(function () {
        var file = document.getElementById('currentTrackName').textContent;
        var start = document.getElementById('AlgoStartTime').value;
        var end = document.getElementById('AlgoEndTime').value;
        var add_fades = document.getElementById('AlgoAddFades').checked;
        var fade_in = 0, fade_out = 0;
        if (add_fades) {
            fade_in = document.getElementById('AlgoFadeInTime').value;
            fade_out = document.getElementById('AlgoFadeOutTime').value;
        }
        var renderButton = document.getElementById('EditAlgoRenderButton');
        renderButton.disabled = true;
        $.ajax({
            type: 'POST',
            url: '/generate/edit',
            data: {'file': file, 'start': start, 'end': end, 'fade_in': fade_in, 'fade_out': fade_out},
            success: function (data) {
                renderButton.innerText = "Rerender";
                renderButton.disabled = false;
                var mp3Url = '/generated_data/' + data.file;
                $('#mp3PlayerContainerForAlgorithmicMusicEdited').html('<audio-player src="' + mp3Url + '" bar-width="5" bar-gap="2" preload loop> </audio-player>')
                $('#downloadEditedMP3ButtonContainer').html('<a class="hyperlink-text" id="DownloadEditedMP3File" href="/downloadEditedMP3/' + data.file + '" download>Download MP3</a>');
            }, 
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON.error;
                alert(errorMessage);
                window.location.reload();
            }
        });
    });

    $('#EditNeuroRenderButton').click(function () {
        var file = document.getElementById('currentTrackName').textContent;
        var start = document.getElementById('NeuroStartTime').value;
        var end = document.getElementById('NeuroEndTime').value;
        var add_fades = document.getElementById('NeuroAddFades').checked;
        var fade_in = 0, fade_out = 0;
        if (add_fades) {
            fade_in = document.getElementById('NeuroFadeInTime').value;
            fade_out = document.getElementById('NeuroFadeOutTime').value;
        }
        var renderButton = document.getElementById('EditNeuroRenderButton');
        renderButton.disabled = true;
        $.ajax({
            type: 'POST',
            url: '/generate/edit',
            data: {'file': file, 'start': start, 'end': end, 'fade_in': fade_in, 'fade_out': fade_out},
            success: function (data) {
                renderButton.innerText = "Rerender";
                renderButton.disabled = false;
                var mp3Url = '/generated_data/' + data.file;
                $('#mp3PlayerContainerForNeuralMusicEdited').html('<audio-player src="' + mp3Url + '" bar-width="5" bar-gap="2" preload loop> </audio-player>')
                $('#downloadEditedMP3ButtonContainer').html('<a class="hyperlink-text" id="DownloadEditedMP3File" href="/downloadEditedMP3/' + data.file + '" download>Download MP3</a>');
            }, 
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseJSON.error;
                alert(errorMessage);
                window.location.reload();
            }
        });
    });
});