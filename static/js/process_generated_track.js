$(document).ready(function () {
    $('#GenerateAlgorithmicMusic').click(function () {
        var AlgoGenerator = $('#AlgoGenerator').val();
        var DurationOfTheTrack = $('#DurationOfTheTrack').val();
        var TempoOfTheTrack = $('#TempoOfTheTrack').val();
        var ScaleOfTheTrack = $('#ScaleOfTheTrack').val();

        // Show loading spinner
        $('#loadingContainer').show();

        $.ajax({
            type: 'POST',
            url: '/generate/process_algorithmic',
            data: { 'generator': AlgoGenerator, 'duration': DurationOfTheTrack, 'tempo': TempoOfTheTrack, 'scale': ScaleOfTheTrack },
            success: function (data) {
                // Update the MP3 player content with the returned filename
                var filenameMP3 = data.filename + '.mp3';
                var filenameMID = data.filename + '.mid';
                var filenameMusicXML = data.filename + '.musicxml';
                var filenamePDF = data.filename + '.pdf';

                var mp3Url = '/generated_data/' + encodeURIComponent(filenameMP3);
                $('#mp3PlayerContainerForAlgorithmicMusic').html('<audio-player src="' + mp3Url + '" bar-width="5" bar-gap="2" preload loop> </audio-player>')
                // Display download MID button
                $('#downloadMIDButtonContainer').html('<a class="hyperlink-text" id="DownloadGeneratedMIDFile" href="/downloadMID/' + encodeURIComponent(filenameMID) + '" download>Download MIDI</a>');

                // Display download MP3 button
                $('#downloadMP3ButtonContainer').html('<a class="hyperlink-text" id="DownloadGeneratedMP3File" href="/downloadMP3/' + encodeURIComponent(filenameMP3) + '" download>Download MP3</a>');

                // Display download MusicXML button
                $('#downloadMusicXMLButtonContainer').html('<a class="hyperlink-text" id="DownloadGeneratedMusicXMLFile" href="/downloadMusicXML/' + encodeURIComponent(filenameMusicXML) + '" download>Download MusicXML</a>');

                // Display download PDF button
                $('#downloadPDFButtonContainer').html('<a class="hyperlink-text" id="DownloadGeneratedPDFFile" href="/downloadPDF/' + encodeURIComponent(filenamePDF) + '" download>Download PDF</a>');

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