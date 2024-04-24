var neuroRefreshIntervalId = NaN;
var neuroProgressBarTextRefreshIntervalId = NaN;
const PROGRESS_BAR_REFRESH_RATE = 100; // ms
const PROGRESS_BAR_TEXT_REFRESH_RATE = 300; // ms
var generationState = 'initial';

function countDotsAtEnd(text) {
    const regex = /\.+$/;
    const match = text.match(regex);
    return match ? match[0].length : 0;
}

async function cycleThroughDots() {
    var element = document.getElementById('neuroProgressBarText');
    var text = element.innerText;
    var count = countDotsAtEnd(text);
    element.innerText = text.substring(0, text.length - count) + '.'.repeat(count == 3 ? 0 : count + 1);
}

async function updateProgressNeuro(filename) {
    const response = await fetch('/progress');
    const data = await response.json();
    document.getElementById('neuroProgressBar').style.width = `${data.progress}%`;
    if (data.progress > 0 && generationState == 'initial') {
        generationState = 'generating';
        document.getElementById('neuroProgressBarText').innerText = "Generating";
    }
    if (data.progress == 100 && generationState == 'generating') {
        generationState = 'rendering';
        document.getElementById('neuroProgressBarText').innerText = "Rendering";
        clearInterval(neuroRefreshIntervalId);
        finish(filename);
    }
}

function generateNeuralTrack() {
    var NeuralGenerator = $('#NeuralGenerator').val();
    var DurationOfTheTrack = $('#DurationOfTheTrack').val();
    var TempoOfTheTrack = $('#TempoOfTheTrack').val();
    
    // Show loading spinner
    // $('#loadingContainer').show();
    document.getElementById('neuroProgressBarText').innerText = "Initializing";
    document.getElementById('neuroProgressBar').setAttribute("style","width: 0%");
    $('#neuroProgressBarContainer').show();
    neuroProgressBarTextRefreshIntervalId = setInterval(cycleThroughDots, PROGRESS_BAR_TEXT_REFRESH_RATE);
   
    $.ajax({
        type: 'POST',
        url: '/generate/process_neural_start',
        data: { 'generator': NeuralGenerator, 'duration': DurationOfTheTrack, 'tempo': TempoOfTheTrack },
        success: function (data) {
            neuroRefreshIntervalId = setInterval(updateProgressNeuro, PROGRESS_BAR_REFRESH_RATE, data.filename);
        }
    });
}

function finish(filename) {
    $.ajax({
        type: 'POST',
        url: '/generate/process_neural_finish',
        data: { 'filename': filename },
        success: function () {
            var filenameMP3 = filename + '.mp3';
            var filenameMID = filename + '.mid';
        
            var mp3Url = '/generated_data/' + encodeURIComponent(filenameMP3);
            $('#mp3PlayerContainerForNeuralMusic').html('<audio-player src="' + mp3Url + '" bar-width="5" bar-gap="2" preload loop> </audio-player>');

            // Display download MID button
            $('#downloadMIDButton').html('<a class="hyperlink-text" id="DownloadGeneratedMIDFile" href="/downloadMID/' + encodeURIComponent(filenameMID) + '" download>Download MIDI</a>');

            // Display download MP3 button
            $('#downloadMP3Button').html('<a class="hyperlink-text" id="DownloadGeneratedMP3File" href="/downloadMP3/' + encodeURIComponent(filenameMP3) + '" download>Download MP3</a>');

            // Hide loading spinner
            // $('#loadingContainer').hide();
            clearInterval(neuroProgressBarTextRefreshIntervalId);
            $('#neuroProgressBarContainer').hide();
            generationState = 'initial';

            $('#EditNeuroTrackButtonContainer').show();

            // Store track's name in an invisible <div> for easier access later for editing 
            var currentTrackName = document.getElementById('currentTrackName');
            currentTrackName.textContent = 'generated_data/' + encodeURIComponent(filenameMP3);

            // Reset editing player in case we are regenereating track
            $('#mp3PlayerContainerForNeuralMusicEdited').html('');
            $('#downloadEditedMP3ButtonContainer').html('');
            document.getElementById('EditNeuroRenderButton').innerText = "Render";
        }
    });   
}