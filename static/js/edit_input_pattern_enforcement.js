function convertToSeconds(time) {
    const parts = time.split(':');
    return parseInt(parts[0],  10) * 60 + parseInt(parts[1],  10);
}

var startOldValue = "0:00";
try {
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
} catch {
  // nothing 
}

try {
  document.getElementById('NeuroStartTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-9]:[0-5][0-9]$');
    if (!pattern.test(value)) {
        alert('Invalid time format. Please enter time in the format of m:ss.');
        e.target.value = startOldValue;
    } else {
        startOldValue = value;
    }
  });
} catch {
  // nothing
}

try {
  var endOldValue = "0:30";
  document.getElementById('AlgoEndTime').addEventListener('change', function(e) {
      var value = e.target.value;
      var pattern = new RegExp('^[0-9]:[0-5][0-9]$');
      if (!pattern.test(value)) {
          alert('Invalid time format. Please enter time in the format of m:ss.');
          e.target.value = endOldValue;
      } else {
          endOldValue = value;
      }
  });
} catch {
  // nothing
}

try {
  document.getElementById('NeuroEndTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-9]:[0-5][0-9]$');
    if (!pattern.test(value)) {
        alert('Invalid time format. Please enter time in the format of m:ss.');
        e.target.value = endOldValue;
    } else {
        endOldValue = value;
    }
  });
} catch {
  // nothing
}

try {
  document.getElementById('AlgoFadeInTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-5]?[0-9]$');
    if (!pattern.test(value)) {
      alert('Invalid time format. Please enter time in the format of ss.');
      e.target.value = '0';
    }
  });
} catch {
  // nothing
}

try {
  document.getElementById('NeuroFadeInTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-5]?[0-9]$');
    if (!pattern.test(value)) {
      alert('Invalid time format. Please enter time in the format of ss.');
      e.target.value = '0';
    }
  });
} catch {
  // nothing
}

try {
  document.getElementById('AlgoFadeOutTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-5]?[0-9]$');
    if (!pattern.test(value)) {
      alert('Invalid time format. Please enter time in the format of ss.');
      e.target.value = '0';
    } else {

    }
  });
} catch {
  // nothing
}

try {
  document.getElementById('NeuroFadeOutTime').addEventListener('change', function(e) {
    var value = e.target.value;
    var pattern = new RegExp('^[0-5]?[0-9]$');
    if (!pattern.test(value)) {
      alert('Invalid time format. Please enter time in the format of ss.');
      e.target.value = '0';
    } else {

    }
  });
} catch {
  // nothing
}