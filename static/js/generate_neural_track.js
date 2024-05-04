var neuroRefreshIntervalId = NaN;
var neuroProgressBarTextRefreshIntervalId = NaN;
const NEURO_PROGRESS_BAR_REFRESH_RATE = 100; // ms
const NEURO_PROGRESS_BAR_TEXT_REFRESH_RATE = 300; // ms
var neuroGenerationState = 'initial';

function countDotsAtEnd(text) {
    const regex = /\.+$/;
    const match = text.match(regex);
    return match ? match[0].length : 0;
}

// function that shows a little text animation while the track is generating 
async function neuroCycleThroughDots() {
    var element = document.getElementById('neuroProgressBarText');
    var text = element.innerText;
    var count = countDotsAtEnd(text);
    element.innerText = text.substring(0, text.length - count) + '.'.repeat(count == 3 ? 0 : count + 1);
}

// function that is called once every PROGRESS_BAR_REFRESH_RATE ms. It updates the progress bar length and
// starts the neuroFinish() function if the progress is at 100%
async function neuroUpdateProgress(filename) {
    $.ajax({
        type: 'POST',
        url: '/progress',
        data: { 'filename': filename },
        success: function (data) {
            document.getElementById('neuroProgressBar').style.width = `${data.progress}%`;
            if (data.progress > 0 && neuroGenerationState == 'initial') {
                neuroGenerationState = 'generating';
                document.getElementById('neuroProgressBarText').innerText = "Generating";
            }
            if (data.progress == 100 && neuroGenerationState == 'generating') {
                neuroGenerationState = 'rendering';
                document.getElementById('neuroProgressBarText').innerText = "Rendering";
                clearInterval(neuroRefreshIntervalId);
                neuroFinish(filename);
            }
        }, 
        error: function(xhr, status, error) {
            var errorMessage = xhr.responseJSON.error;
            alert(errorMessage);
            window.location.reload();
        }
    });
}

// main function that initializes the track generation
function generateNeuralTrack() {
    var NeuralGenerator = $('#NeuralGenerator').val();
    var DurationOfTheTrack = $('#DurationOfTheTrack').val();
    var TempoOfTheTrack = $('#TempoOfTheTrack').val();
    var NeuroCorrectScale = $('#NeuroCorrectScale').val();
    
    document.getElementById('neuroProgressBarText').innerText = "Initializing";
    document.getElementById('neuroProgressBar').setAttribute("style","width: 0%");
    $('#neuroProgressBarContainer').show();
    neuroProgressBarTextRefreshIntervalId = setInterval(neuroCycleThroughDots, NEURO_PROGRESS_BAR_TEXT_REFRESH_RATE);
   
    $.ajax({
        type: 'POST',
        url: '/generate/process_neural_start',
        data: { 'generator': NeuralGenerator, 'duration': DurationOfTheTrack, 'tempo': TempoOfTheTrack, 'correct_scale': NeuroCorrectScale },
        success: function (data) {
            document.getElementById('GenerateNeuralMusic').disabled = true;
            neuroRefreshIntervalId = setInterval(neuroUpdateProgress, NEURO_PROGRESS_BAR_REFRESH_RATE, data.filename);
        },
        error: function(xhr, status, error) {
            var errorMessage = xhr.responseJSON.error;
            alert(errorMessage);
            window.location.reload();
        }
    });
}

// switch from 'generating' state to 'generated' state (render the track, show editing buttons)
function neuroFinish(filename) {
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
            neuroGenerationState = 'initial';

            $('#EditNeuroTrackButtonContainer').show();

            // Store track's name in an invisible <div> for easier access later for editing 
            var currentTrackName = document.getElementById('currentTrackName');
            currentTrackName.textContent = 'generated_data/' + encodeURIComponent(filenameMP3);

            // Reset editing player in case we are regenereating track
            $('#mp3PlayerContainerForNeuralMusicEdited').html('');
            $('#downloadEditedMP3ButtonContainer').html('');
            document.getElementById('EditNeuroRenderButton').innerText = "Render";
            document.getElementById('GenerateNeuralMusic').disabled = false;
            enableGenerateButton();
        },
        error: function(xhr, status, error) {
            var errorMessage = xhr.responseJSON.error;
            alert(errorMessage);
            window.location.reload();
        }
    });   
}
