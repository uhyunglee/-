var nodeCount = 1;
window.onload = function() {
    getNodeCount();
    generateProgressBars(nodeCount);
    updateAllProgressBars(nodeCount);
}
setInterval(repeat, 5000, nodeCount);


function repeat(nodeCount){
    updateAllProgressBars(nodeCount);
    checkConversionStatus();
}

function getNodeCount(){
     $.ajax({
          url: '/nodecount',
          async:false,
          success: function (data) {
            nodeCount = data;
          }
        })

}

function generateProgressBars(nodeCount) {
    var progressNode = document.getElementById("progress-bars-container");


    for (var i = 1; i <= nodeCount; i++) {
        var progressString = document.createElement("div");
        var nodeName = document.createElement("p");
        var persentString = document.createElement("p");
        var progressBar = document.createElement("progress");

        progressString.setAttribute('class', 'progressString');
        nodeName.setAttribute('class', 'nodeName');
        persentString.setAttribute('class', 'persentString');
        persentString.setAttribute('id', 'persentString-'+i);
        progressBar.setAttribute('class', 'progressBar');
        progressBar.setAttribute('id', 'progressBar-'+i);
        progressBar.setAttribute('min', 0);
        progressBar.setAttribute('max', 100);
        progressBar.setAttribute('value', 0);


        nodeName.innerHTML = "Node " + i ;
        persentString.innerHTML = "0%";

        progressString.appendChild(nodeName);
        progressString.appendChild(persentString);

       progressNode.appendChild(progressString);
       progressNode.appendChild(progressBar);
      }
}

function checkConversionStatus() {
    $.ajax({
      url: '/status/conversion',
      success: function (data) {
        if (data === "completed") {
          // 변환이 완료되면 다운로드 페이지로 이동
          window.location.href = "download";
        }
      },
    })
}


function updateProgressBar(progressBarId, progress) {
    var progressBar = document.getElementById("progressBar-"+progressBarId);
    progressBar.setAttribute('value',progress);

    var progressString = document.getElementById("persentString-"+progressBarId);
    progressString.innerHTML=progress+"%";
}

function updateProgressBars(updateUrl) {
    var data;
    $.ajax({
        url: updateUrl, // Replace with the actual endpoint URL and parameters
        type: 'GET',
        async:false,
        data : JSON.stringify(data),
        dataType : "json",
        success: function(data) {
          var progressBarId = data.progressBarId;
          var progress = data.progress;
          console.log(progressBarId, progress);

          // Update the specified progress bar
          updateProgressBar(progressBarId, progress);
        },
        error: function(xhr, status, error) {
          // Handle error case
        }
    });
}

function updateAllProgressBars(){
    for (var i = 1; i <= nodeCount; i++) {
        var updateUrl = "progress/"+i;
        updateProgressBars(updateUrl);
    }

}