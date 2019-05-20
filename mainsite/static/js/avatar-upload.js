$(function () {

    /* SCRIPT TO OPEN THE MODAL WITH THE PREVIEW */
    $("#id_avatar").change(function () {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $("#image").attr("src", e.target.result);
                $("#upload-modal").modal('hide');
                $('#bootstrap-modal').modal('show');
            }
            reader.readAsDataURL(this.files[0]);
        }
    });

    /* SCRIPTS TO HANDLE THE CROPPER BOX */
    var $image = $("#image");
    var cropBoxData;
    var canvasData;
    $("#bootstrap-modal").on("shown.bs.modal", function () {
        $image.cropper({
            viewMode: 1,
            aspectRatio: 1 / 1,
            minCropBoxWidth: 200,
            minCropBoxHeight: 200,
            ready: function () {
                $image.cropper("setCanvasData", canvasData);
                $image.cropper("setCropBoxData", cropBoxData);
            }
        });
    }).on("hidden.bs.modal", function () {
        cropBoxData = $image.cropper("getCropBoxData");
        canvasData = $image.cropper("getCanvasData");
        $image.cropper("destroy");
    });

    $(".js-zoom-in").click(function () {
        // alert("zoom in")
        $image.cropper("zoom", 0.1);
    });

    $(".js-zoom-out").click(function () {
        // alert("zoom out")
        $image.cropper("zoom", -0.1);
    });

    /* SCRIPT TO COLLECT THE DATA AND POST TO THE SERVER */
    $(".js-crop-and-upload").click(function () {
        var cropData = $image.cropper("getData");
        $("#id_x").val(cropData["x"]);
        $("#id_y").val(cropData["y"]);
        $("#id_height").val(cropData["height"]);
        $("#id_width").val(cropData["width"]);
        $("#formUpload").submit();
    });

    /* 1. OPEN THE FILE EXPLORER WINDOW */
    $(".js-upload-avatar").click(function () {
        $("#id_avatar").click();
    });
    $('.open-upload-modal').on('click', function () {
        $('#bootstrap-modal').modal('hide');
        $('#upload-modal').modal({
            keyboard: false
        })
    });
    /* SCRIPT TO COLLECT THE DATA AND POST TO THE SERVER */
    $(".js-crop-and-upload").click(function () {
        var cropData = $image.cropper("getData");
        $("#id_x").val(cropData["x"]);
        $("#id_y").val(cropData["y"]);
        $("#id_height").val(cropData["height"]);
        $("#id_width").val(cropData["width"]);
        $("#formUpload").submit();
    });
    // /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
    // $("#fileupload").fileupload({
    //   dataType: 'json',
    //   done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
    //     console.log('success', e, data)
    //     if (data.result.is_valid) {
    //       $("#gallery tbody").prepend(
    //         "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
    //       )
    //     }
    //   },
    //
    //   start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
    //     $(".upload-progress").removeClass('hidden');
    //   },
    //   stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINALIZE, HIDE THE MODAL */
    //     $(".upload-progress").addClass('hidden');
    //     $('#bootstrap-modal').modal('hide');
    //     location.reload();
    //   },
    //   progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
    //     var progress = parseInt(data.loaded / data.total * 100, 10);
    //     var strProgress = progress + "%";
    //     $("upload-progress.progress-bar").css({"width": strProgress});
    //     $(".progress-bar").text(strProgress);
    //   },
    //
    //   error: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
    //     console.log('error', e, data);
    //     // if (data.result.is_valid) {
    //     //   $("#gallery tbody").prepend(
    //     //     "<tr><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td></tr>"
    //     //   )
    //     // }
    //   }
    // });

});