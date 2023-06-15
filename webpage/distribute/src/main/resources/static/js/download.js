let videoUrl
window.onload = function() {

}

function getVideoUrl(){
fetch("/api/videoUrl", {method: "POST"})
    .then((response) =>{
        return response.json();
    })
    .then((response) =>{
        videoUrl = response;
        let videoObject = document.getElementById("videoPlayer");
        let video = '<video src=${videoUrl.url} width ="500" height="500" controls />';
        videoObject.innerHTML = video;
    });

}
