async function postData(endpoint, data) {
  try {
    const response = await fetch(`http://127.0.0.1:5057/api/${endpoint}`, {
      method: "POST", // or 'PUT'
      body: data,
    });

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Error:", error);
  }
}
function updateRangeOutput(element) {
  element.nextElementSibling.value = parseFloat(element.value).toFixed(2);
}
async function getData(endpoint) {
  try {
    const response = await fetch(`http://127.0.0.1:5057/api/${endpoint}`, {
      method: "GET", // or 'PUT'
    });

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Error:", error);
  }
}
function getOriginalImagePath(facePath) {
  let pattern = /\/static\/[a-zA-Z0-9_]+\/(aligned_(\d+)_)?/; //
  let match = pattern.exec(facePath); // Executing the regex pattern on the string

  if (match) {
    let face_num = match[2];
    let imagePath = facePath.replace(pattern, "/pool/");
    // imagePath = imagePath.replace("/static/", "/pool/")
    return [imagePath, face_num];
  }
  return ["", 0];
}
async function findLandmarks(image, face_num) {
  let data = new FormData();
  if (face_num !== undefined && face_num != -2) {
    data.append("images", [`aligned_${face_num}_${image}`]);
  } else {
    data.append("images", [image]);
  }
  let result = await postData("detect", data);
  let detected_image = result.images[0];
  return detected_image;
}
async function findFace(image, face_num) {
  let data = new FormData();
  data.append("image", image);
  let result = await postData("find", data);
  if (face_num == -2) {
    return result.boxes;
  }
  return [result.boxes[face_num]];
}
function makeCanvas(src) {
  // Create a canvas element
  let canvas = document.createElement("canvas");
  let ctx = canvas.getContext("2d");

  // Create an Image object
  let img = new Image();
  img.crossOrigin = "anonymous"; // This enables CORS
  return new Promise((resolve, reject) => {
    img.onload = function () {
      const displaySize = { width: img.width, height: img.height };
      faceapi.matchDimensions(canvas, displaySize);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      resolve(canvas);
    };
    img.onerror = (error) => reject(error);
    // Set the source of the image
    img.src = src;
  });
}

async function loadImage(canvas, src) {
  const ctx = canvas.getContext("2d");

  const img = new Image();
  return new Promise((resolve, reject) => {
    img.onload = function () {
      const displaySize = { width: img.width, height: img.height };
      faceapi.matchDimensions(canvas, displaySize);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      resolve();
    };
    img.onerror = (error) => reject(error);
    img.src = src; // Replace with your image URL
  });
}
function sendJsonPost(endpoint,data){
  fetch(`/${endpoint}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
})
.then(response => response.json())
.then(data => {
  return data
})
.catch(error => console.error('Error:', error));
}


function sendJsonFormPost(endpoint, data) {
  const form = document.createElement("form");
  form.action = `/${endpoint}`;
  form.method = "POST";

  const jsonData = document.createElement("input");
  jsonData.type = "hidden";
  jsonData.name = "jsonData"; // This will be the key on the server side
  jsonData.value = JSON.stringify(data);
  const detectorData = document.createElement("input");
  const embedderData = document.createElement("input");
  detectorData.type = "hidden";
  detectorData.name = "detector_name"; // This will be the key on the server side
  detectorData.value = detector_name;
  embedderData.type = "hidden";
  embedderData.name = "embedder_name"; // This will be the key on the server side
  embedderData.value = embedder_name;
  form.appendChild(detectorData);
  $("[id^=face_num_input]").appendTo(form);
  form.appendChild(embedderData);
  form.appendChild(jsonData);
  document.body.appendChild(form);
  form.submit();
}
function sendFormPost(endpoint, data) {
  const form = document.createElement("form");
  form.action = endpoint;
  form.method = "POST";
  for (let key in data) {
    const field = document.createElement("input");
    field.type = "hidden";
    field.name = key; // This will be the key on the server side
    field.value = data[key];
    form.appendChild(field);
  }
  document.body.appendChild(form);
  form.submit();
}
function display_faceActionMenu(e){
  e.preventDefault();
  faceActionsMenu.style.display = "block";
  faceActionsMenu.style.left = `${e.pageX}px`;
  faceActionsMenu.style.top = `${e.pageY}px`;
  current_selected_image=$(e.currentTarget).find('p').text() 
}
function setAsImage(idx){
  console.log(`${current_selected_image} set as ${idx}`)
  sendJsonPost("update_selection",{"index":idx,"image":current_selected_image,
    "embedder_name":embedder_name,"detector_name":detector_name})
}
$(document).ready(function () {
  let current_selected_image;
  const $faceActionsMenu = $("#faceActionsMenu");
  $(document).on("click", function () {
  $faceActionsMenu.hide();
});
});
