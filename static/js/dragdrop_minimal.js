"use strict";

async function loadImage(canvas, src) {
  const ctx = canvas.getContext("2d");

  const img = new Image();
  return new Promise((resolve,reject)=>{
  img.onload = function () {
    const displaySize = { width: img.width, height: img.height };
    faceapi.matchDimensions(canvas, displaySize);
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    resolve()
  };
  img.onerror=(error)=> reject(error);
  img.src = src; // Replace with your image URL
});
}

function getImgParams($comboBox, areaNumber) {
  const faceNum = parseInt($comboBox.val());
  const fileName = current_images[areaNumber - 1];
  return { faceNum, fileName };
}
async function getFacePath($comboBox, areaNumber) {
  let $params = getImgParams($comboBox, areaNumber);
  let path = "";
  let face_num = $params.faceNum;
  path = SERVER_URL + `/pool/${$params.fileName}`;
  const exists = await checkFileExists(path);
  return { path, exists, face_num };
}
function setupDropArea($dropArea, areaNumber) {
  const $img = $dropArea.find("canvas");
  const $content = $dropArea.find(`#dragarea${areaNumber}-content`);
  const $dragText = $content.find("header");
  const $button = $content.find("button");
  const $input = $dropArea.find("input");
  const $comboBox = $(`#combo-box${areaNumber}`);
  $button.on("click", function () {
    $input.click();
  });

  $input.on("change", function () {
    const file = this.files[0];
    $dropArea.addClass("active");
    showFile($dropArea, file);
    $("form").submit(function (eventObj) {
      $("<input />")
        .attr("type", "hidden")
        .attr("name", "action")
        .attr("value", "Upload")
        .appendTo(this);
      return true;
    });
    $("form").submit();
    $("button").prop("disabled", true);
    $("input[type='button'], input[type='submit']").prop("disabled", true);
  });
  $dropArea.on("dragover", function (event) {
    event.preventDefault();
    $dropArea.addClass("active");
    $dragText.text("Release to Upload File");
  });
  $dropArea.on("dragleave", function () {
    $dropArea.removeClass("active");
    $dragText.text("Drag & Drop to Upload File");
  });

  $dropArea.on("drop", function (event) {
    event.preventDefault();
    const file = event.originalEvent.dataTransfer.files[0];
    $input[0].files = event.originalEvent.dataTransfer.files;
    showFile($dropArea, file);
    $("form").submit(function (eventObj) {
      $("<input />")
        .attr("type", "hidden")
        .attr("name", "action")
        .attr("value", "Upload")
        .appendTo(this);
      return true;
    });
    $("form").submit();
    $("button").prop("disabled", true);
    $("input[type='button'], input[type='submit']").prop("disabled", true);
  });
  $comboBox.on("change", async function () {
    let result = await getFacePath($(this), areaNumber);
    if (result.exists) {
      //display
      $(`#face_num_input${areaNumber}`).val(result.face_num);
      await loadImage($img[0], result.path);

      $img.removeClass("d-none");
      $dropArea.removeClass("p-5");
    } else {
      // align and then display
    }
  });
  return { $img, $content, $dragText, $button, $input, $comboBox };
}
const dropArea1Elements = setupDropArea($("#dragarea1"), 1);
const dropArea2Elements = setupDropArea($("#dragarea2"), 2);
let file;

$(document).ready(function () {

  let $imgs = [dropArea1Elements.$img, dropArea2Elements.$img];
  for (let index = 0; index < current_images.length; index++) {
    if (current_images[index] != undefined && current_images[index] !== "") {
      let path;
      path = SERVER_URL + `/pool/${current_images[index]}`;
      loadImage($imgs[index][0], path);
      $imgs[index].removeClass("d-none");
      $imgs[index].removeClass("p-5");
    }
  }
});

function deleteImage(button) {
  var $dragArea = $(button).parent();
  const $input = $dragArea.find("input");
  $input.val("");

  unshowFile($dragArea);
  $(button).remove();
}
function unshowFile($dragArea) {
  let $img = $dragArea.find("canvas");
  const ctx = $img.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  $img.addClass("d-none");
  $dragArea.addClass("p-5");
  $dragArea.removeClass("active");
}
function dataURLtoFile(dataurl, filename) {
  var arr = dataurl.split(","),
    mime = arr[0].match(/:(.*?);/)[1],
    bstr = atob(arr[arr.length - 1]),
    n = bstr.length,
    u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new File([u8arr], filename, { type: mime });
}

function showFile(dragArea, file) {
  let fileType = file.type;
  let validExtensions = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
  if (validExtensions.includes(fileType)) {
    let fileReader = new FileReader();
    fileReader.onload = () => {
      let fileURL = fileReader.result;
      let $imgElement = dragArea.find("canvas");
      loadImage($imgElement[0], fileURL);
      $imgElement.removeClass("d-none");
      dragArea.addClass("active");
      dragArea.removeClass("p-5");
    };
    fileReader.readAsDataURL(file);
  } else {
    alert("This is not an Image File!");
    dragArea.removeClass("active");
    dragArea.find("header").text("Drag & Drop to Upload File");
  }
}
async function checkFileExists(filePath) {
  try {
    await $.ajax({
      url: filePath,
      type: "HEAD",
    });
    return true;
  } catch (error) {
    return false;
  }
}
