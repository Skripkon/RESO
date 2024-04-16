$(document).ready(function () {
    $('#GenerateNeuralMusic').click(function () {
        var NeuralGenerator = $('#NeuralGenerator').val();
        var DurationOfTheTrack = $('#DurationOfTheTrack').val();
        var TempoOfTheTrack = $('#TempoOfTheTrack').val();

        // Show loading spinner
        $('#loadingContainer').show();

        $.ajax({
            type: 'POST',
            url: '/generate/process_neural',
            data: { 'generator': NeuralGenerator, 'duration': DurationOfTheTrack, 'tempo': TempoOfTheTrack },
            success: function (data) {
                // Update the MP3 player content with the returned filename
                var filenameMP3 = data.filename + '.mp3';
                var filenameMID = data.filename + '.mid';

                var mp3Url = '/generated_data/' + encodeURIComponent(filenameMP3);
                $('#mp3PlayerContainerForNeuralMusic').html('<audio-player src="' + mp3Url + '" bar-width="5" bar-gap="2" preload loop> </audio-player>');


                // Display download MID button
                $('#downloadMIDButton').html('<a class="hyperlink-text" id="DownloadGeneratedMIDFile" href="/downloadMID/' + encodeURIComponent(filenameMID) + '" download>Download MIDI</a>');

                // Display download MP3 button
                $('#downloadMP3Button').html('<a class="hyperlink-text" id="DownloadGeneratedMP3File" href="/downloadMP3/' + encodeURIComponent(filenameMP3) + '" download>Download MP3</a>');

                // Hide loading spinner
                $('#loadingContainer').hide();
                $('#EditAlgoTrackButtonContainer').show();

                // Store track's name in an invisible <div> for easier access later for editing 
                var currentTrackName = document.getElementById('currentTrackName');
                currentTrackName.textContent = 'generated_data/' + encodeURIComponent(filenameMP3);

                // Reset editing player in case we are regenereating track
                $('#mp3PlayerContainerForAlgorithmicMusicEdited').html('');
                $('#downloadEditedMP3ButtonContainer').html('');
                var renderButton = document.getElementById('EditAlgoRenderButton');
                renderButton.innerText = "Render";
            }
        });
    });
});