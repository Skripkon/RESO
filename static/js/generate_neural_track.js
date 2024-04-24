var neuroRefreshIntervalId = NaN;

async function updateProgressNeuro(filename) {
    const response = await fetch('/progress');
    const data = await response.json();
    document.querySelector('#progressBar div').style.width = `${data.progress}%`;
    if (data.progress == 100) {
        clearInterval(neuroRefreshIntervalId);
        finish(filename);
    }
}

function generateNeuralTrack() {
    var NeuralGenerator = $('#NeuralGenerator').val();
    var DurationOfTheTrack = $('#DurationOfTheTrack').val();
    var TempoOfTheTrack = $('#TempoOfTheTrack').val();
    
    // Show loading spinner
    $('#loadingContainer').show();
   
    $.ajax({
        type: 'POST',
        url: '/generate/process_neural_start',
        data: { 'generator': NeuralGenerator, 'duration': DurationOfTheTrack, 'tempo': TempoOfTheTrack },
        success: function (data) {
            neuroRefreshIntervalId = setInterval(updateProgressNeuro, 500, data.filename);
        }
    });
}

function finish(filename) {
    $.ajax({
        type: 'POST',
        url: '/generate/process_neural_finish',
        data: { 'filename': filename },
        success: function (data) {
            var filenameMP3 = filename + '.mp3';
            var filenameMID = filename + '.mid';
        
            var mp3Url = '/generated_data/' + encodeURIComponent(filenameMP3);
            $('#mp3PlayerContainerForNeuralMusic').html('<audio-player src="' + mp3Url + '" bar-width="5" bar-gap="2" preload loop> </audio-player>');

            // Display download MID button
            $('#downloadMIDButton').html('<a class="hyperlink-text" id="DownloadGeneratedMIDFile" href="/downloadMID/' + encodeURIComponent(filenameMID) + '" download>Download MIDI</a>');

            // Display download MP3 button
            $('#downloadMP3Button').html('<a class="hyperlink-text" id="DownloadGeneratedMP3File" href="/downloadMP3/' + encodeURIComponent(filenameMP3) + '" download>Download MP3</a>');

            // Hide loading spinner
            $('#loadingContainer').hide();
            $('#EditNeuroTrackButtonContainer').show();

            // Store track's name in an invisible <div> for easier access later for editing 
            var currentTrackName = document.getElementById('currentTrackName');
            currentTrackName.textContent = 'generated_data/' + encodeURIComponent(filenameMP3);

            // Reset editing player in case we are regenereating track
            $('#mp3PlayerContainerForNeuralMusicEdited').html('');
            $('#downloadEditedMP3ButtonContainer').html('');
            var renderButton = document.getElementById('EditNeuroRenderButton');
            renderButton.innerText = "Render";
        }
    });   
}