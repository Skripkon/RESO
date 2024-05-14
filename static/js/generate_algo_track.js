var algoRefreshIntervalId = NaN;
var algoProgressBarTextRefreshIntervalId = NaN;
const ALGO_PROGRESS_BAR_REFRESH_RATE = 150; // ms
const ALGO_PROGRESS_BAR_TEXT_REFRESH_RATE = 300; // ms
var algoGenerationState = 'initial';

function countDotsAtEnd(text) {
    const regex = /\.+$/;
    const match = text.match(regex);
    return match ? match[0].length : 0;
}

// function that shows a little text animation while the track is generating 
async function algoCycleThroughDots() {
    var element = document.getElementById('algoProgressBarText');
    var text = element.innerText;
    var count = countDotsAtEnd(text);
    element.innerText = text.substring(0, text.length - count) + '.'.repeat(count == 3 ? 0 : count + 1);
}

// function that is called once every PROGRESS_BAR_REFRESH_RATE ms. It updates the progress bar length and
// starts the algoFinish() function if the progress is at 100%
async function algoUpdateProgress(filename) {
    $.ajax({
        type: 'POST',
        url: '/progress',
        contentType: 'application/json',
        data: JSON.stringify({ 'filename': filename }),
        success: function (data) {
            var algoProgressBar = document.getElementById('algoProgressBar');
            var algoProgressBarText = document.getElementById('algoProgressBarText');
            if (data.progress > 0 && algoGenerationState == 'initial') {
                algoProgressBar.style.width = `${data.progress}%`;
                algoProgressBarText.innerText = "Generating";
                algoGenerationState = 'generating';
            }
            if (data.progress < 100 && algoGenerationState == 'generating') {
                algoProgressBar.style.width = `${data.progress}%`;
            }
            if (data.progress == 100 && algoGenerationState == 'generating') {
                algoProgressBar.style.width = `${data.progress}%`;
                algoGenerationState = 'saving';
                algoProgressBarText.innerText = "Saving";
            }
            // special value that indicates that the midi has been saved
            if (data.progress == 200) {
                algoProgressBar.style.width = "100%";
                algoGenerationState = 'rendering';
                algoProgressBarText.innerText = "Rendering";
                clearInterval(algoRefreshIntervalId);
                algoFinish(filename);
            }
        },
        error: function(xhr, status, error) {
            var errorMessage = xhr.responseJSON.error;
            alert(errorMessage);
            window.location.reload();
        }
    });
}

function generateAlgoTrack() {
    var AlgoGenerator = $('#AlgoGenerator').val();
    var DurationOfTheTrack = $('#DurationOfTheTrack').val();
    var TempoOfTheTrack = $('#TempoOfTheTrack').val();
    var ScaleOfTheTrack = $('#ScaleOfTheTrack').val();

    
    $.ajax({
        type: 'POST',
        url: '/generate/process_algorithmic_start',
        contentType: 'application/json',
        data: JSON.stringify({ 'generator': AlgoGenerator, 'duration': DurationOfTheTrack, 'tempo': TempoOfTheTrack, 'scale': ScaleOfTheTrack }),
        success: function (data) {
            document.getElementById('algoProgressBarText').innerText = "Initializing";
            document.getElementById('algoProgressBar').setAttribute("style","width: 0%");
            $('#algoProgressBarContainer').show();
            algoProgressBarTextRefreshIntervalId = setInterval(algoCycleThroughDots, ALGO_PROGRESS_BAR_TEXT_REFRESH_RATE);
            document.getElementById('GenerateAlgorithmicMusic').disabled = true;
            algoRefreshIntervalId = setInterval(algoUpdateProgress, ALGO_PROGRESS_BAR_REFRESH_RATE, data.filename);
        },
        error: function(xhr, status, error) {
            var errorMessage = xhr.responseJSON.error;
            alert(errorMessage);
            window.location.reload();
        }
    });
}

function algoFinish(filename) {
    $.ajax({
        type: 'POST',
        url: '/generate/process_track_finish',
        contentType: 'application/json',
        data: JSON.stringify({ 'filename': filename }),
        success: function () {
            // Update the MP3 player content with the returned filename
            var filenameMP3 = filename + '.mp3';
            var filenameMID = filename + '.mid';
            var filenameMusicXML = filename + '.musicxml';
            var filenamePDF = filename + '.pdf';

            var mp3Url = '/generated_data/' + encodeURIComponent(filenameMP3);
            $('#mp3PlayerContainerForAlgorithmicMusic').html('<audio-player src="' + mp3Url + '" bar-width="5" bar-gap="2" preload loop> </audio-player>');

            var pdfUrl = '/generated_data/' + encodeURIComponent(filenamePDF);
            $('#pdf-iframe').attr('src', pdfUrl);

            // Display download MID button
            $('#downloadMIDButton').html('<a class="hyperlink-text" id="DownloadGeneratedMIDFile" href="/downloadMID/' + encodeURIComponent(filenameMID) + '" download>Download MIDI</a>');

            // Display download MP3 button
            $('#downloadMP3Button').html('<a class="hyperlink-text" id="DownloadGeneratedMP3File" href="/downloadMP3/' + encodeURIComponent(filenameMP3) + '" download>Download MP3</a>');

            // Display download MusicXML button
            $('#downloadMusicXMLButton').html('<a class="hyperlink-text" id="DownloadGeneratedMusicXMLFile" href="/downloadMusicXML/' + encodeURIComponent(filenameMusicXML) + '" download>Download MusicXML</a>');

            // Display download PDF button
            $('#downloadPDFButton').html('<a class="hyperlink-text" id="DownloadGeneratedPDFFile" href="/downloadPDF/' + encodeURIComponent(filenamePDF) + '" download>Download PDF</a>');

            // Hide loading spinner
            // $('#loadingContainer').hide();
            clearInterval(algoProgressBarTextRefreshIntervalId);
            $('#algoProgressBarContainer').hide();
            algoGenerationState = 'initial';

            $('#EditAlgoTrackButtonContainer').show();
            $('#ViewSheetMusicButtonContainer').show();

            // Store track's name in an invisible <div> for easier access later for editing 
            var currentTrackName = document.getElementById('currentTrackName');
            currentTrackName.textContent = 'generated_data/' + encodeURIComponent(filenameMP3);

            // Reset editing player in case we are regenereating track
            $('#mp3PlayerContainerForAlgorithmicMusicEdited').html('');
            $('#downloadEditedMP3ButtonContainer').html('');
            var renderButton = document.getElementById('EditAlgoRenderButton');
            renderButton.innerText = "Render";
            document.getElementById('GenerateAlgorithmicMusic').disabled = false;
        },
        error: function(xhr, status, error) {
            var errorMessage = xhr.responseJSON.error;
            alert(errorMessage);
            window.location.reload();
        }
    });   
}