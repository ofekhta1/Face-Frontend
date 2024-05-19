$('.editButton').click(function () {
    var button = $(this);
    var textElement = button.prev('.editableText');
    var currentText = textElement.text();
    var inputElement = $('<input>').attr('type', 'text').val(currentText);
    textElement.replaceWith(inputElement);
    var confirmButton = $('<button>').text('Confirm');
    inputElement.after(confirmButton);

    confirmButton.click(async function(){
        model_name=$("#modelNameSelect").val()
        var updatedText = inputElement.val();
        var newTextElement = $('<div>').addClass('editableText').text(updatedText);
        inputElement.replaceWith(newTextElement);
        jsonData = JSON.stringify({ old: currentText, new: updatedText,model_name:model_name });
        let response = await postData("change_group_name", jsonData);
        console.log(response);
        confirmButton.remove();
    });

});


$("#clusterBtn").on("click", async function () {
    await get_clusters(true);
});
$("#groupsBtn").on("click", async function () {
    await get_clusters(false);
});
async function get_clusters(retrain){
    let cluster_family = $('input[name="ClusterFamily"]:checked').val();
    model_name=$("#modelNameSelect").val()
    let max_distance=1-$("#SimilarityThreshold").val()
    let min_group_size=$("#MinGroupSize").val()
    let data = JSON.stringify({
        max_distance: max_distance,
        min_samples: min_group_size,
        retrain: retrain,
        model_name: model_name,
        cluster_family: cluster_family // 
    });
    let response = await postData("cluster",data);
    const filteredData = {};
    filteredData["groups"]={}
    for (const key in response) {
        if (Array.isArray(response[key]) && response[key].length <= 400) {
            filteredData["groups"][key] = response[key];
        }
    }
  
    filteredData["similarity_thresh"]=1-max_distance
    filteredData["min_group_size"]=min_group_size
    filteredData["cluster_family"]=cluster_family

    sendJsonFormPost("clustering", filteredData);
}

async function handleFaceClick(src) {
    let result = getOriginalImagePath(src)
    let originalImagePath = decodeURI(result[0])
    let face_num = result[1];
    let startIndex = originalImagePath.indexOf("/pool/") + "/pool/".length;
    let imageName = ""
    if (startIndex !== -1) {
        imageName = originalImagePath.substring(startIndex);

    } else {

        console.log("'/pool/' not found in the string.");
        return;
    }
    let canvas = await makeCanvas(originalImagePath);
    let faces = await findFace(imageName, face_num);
    for (let i = 0; i < faces.length; i++) {
        let face = faces[i];
        let box = { x: face[0], y: face[1], width: face[2] - face[0], height: face[3] - face[1] }
        let num = (face_num === -2) ? i : parseInt(face_num);
        let drawOptions = {
            label: `face ${num + 1}`,
            lineWidth: 5
        }
        let drawBox = new faceapi.draw.DrawBox(box, drawOptions)
        drawBox.draw(canvas)
    }
    let newWindow = window.open('', '_blank');
    $(newWindow.document.body).append(canvas);
}