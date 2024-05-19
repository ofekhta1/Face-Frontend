$button=$("#zipBtn")
$input=$("#zipFileInput")
$button.on("click", function () {
    $input.click();
    
  });
$("form").on('submit',function(){
    $("button").prop("disabled", true);
    $("input[type='button'], input[type='submit']").prop("disabled", true);
})
$input.on("change",function(){
    $("form").submit(function (eventObj) {
      $("<input />")
        .attr("type", "hidden")
        .attr("name", "type")
        .attr("value", "zipfile")
        .appendTo(this);
      return true;
    });
    $("form").submit();
    $("button").prop("disabled", true);
    $("input[type='button'], input[type='submit']").prop("disabled", true);
})
