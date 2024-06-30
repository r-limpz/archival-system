let cropper;

$('#imageModalContainer').on('shown.bs.modal', function () {
    let width = document.getElementById('crop-image-container').offsetWidth - 20;
    let height = width * 1.2; // Set the height to be 50% of the width
    $('#crop-image-container').height(height + 'px');
    cropper = $('#crop-image-container').croppie({
        viewport: {
            width: width,
            height: height // Set the height to be 50% of the width
        },
    });
    $('.cr-slider-wrap').remove();
    $('.modal-body1').height(document.getElementById('crop-image-container').offsetHeight + 5 + 'px');
    cropper.croppie('bind', {
        url: window.src,
    }).then(function () {
        cropper.croppie('setZoom', 0);
    });
});

//destroy the rendered image in the modal croppie 
$('#imageModalContainer').on('hidden.bs.modal', function () {
    cropper.croppie('destroy');
});