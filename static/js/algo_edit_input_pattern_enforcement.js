function convertToSeconds(time) {
    const parts = time.split(':');
    return parseInt(parts[0],  10) * 60 + parseInt(parts[1],  10);
}

var startOldValue = "0:00";
document.getElementById('AlgoStartTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-9]:[0-5][0-9]$');
    if (!pattern.test(value)) {
        alert('Invalid time format. Please enter time in the format of m:ss.');
        e.target.value = startOldValue;
    } else {
        startOldValue = value;
    }
});

var endOldValue = "0:30";
document.getElementById('AlgoEndTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-9]:[0-5][0-9]$');
    if (!pattern.test(value)) {
        alert('Invalid time format. Please enter time in the format of m:ss.');
        e.target.value = endOldValue;
    } else {
        endOldValue = value;
        // TODO: protection from incorrect inputs (i.e. start time > end time)

        // var startInput = document.getElementById('AlgoStartTime');
        // var numStartValue = convertToSeconds(startInput.value);
        // var numEndValue = convertToSeconds(value);
        // if (numEndValue < numStartValue) {
        //     e.target.value = startInput.value; 
        //     alert('End time should be greater than start time.')
        // }
    }
});

// TODO: protection from incorrect inputs (i.e. '01' -> '1')
document.getElementById('AlgoFadeInTime').addEventListener('change', function(e) {
  var value = e.target.value;
  var pattern = new RegExp('^[0-5]?[0-9]$');
  if (!pattern.test(value)) {
    alert('Invalid time format. Please enter time in the format of ss.');
    e.target.value = '0';
  }
});

document.getElementById('AlgoFadeOutTime').addEventListener('change', function(e) {
  var value = e.target.value;
  var pattern = new RegExp('^[0-5]?[0-9]$');
  if (!pattern.test(value)) {
    alert('Invalid time format. Please enter time in the format of ss.');
    e.target.value = '0';
  } else {

  }
});