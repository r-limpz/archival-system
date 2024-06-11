//preview
function preview(rowID) {
    console.log(rowID);

    fetch('/getDocImage/image/data/' + rowID)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(encodedImage => {
            let previewImageDisplay = document.getElementById('previewImageDisplay');
            previewImageDisplay.src = 'data:image/jpeg;base64,' + encodedImage;

            // Show the modal
            let modal = new bootstrap.Modal(document.getElementById('showPreviewModal'));
            modal.show();
        })
        .catch(error => {
            console.error('There has been a problem with your fetch operation:', error);
        });

}

// Clear the image source when the modal is hidden
$('#showPreviewModal').on('hidden.bs.modal', function (e) {
    document.getElementById('previewImageDisplay').src = '';
})

function downloadImage() {
    // Assuming 'image' is a global variable holding your image data
    var image = document.getElementById('previewImageDisplay').src;

    // Download the image
    var link = document.createElement('a');
    link.href = image;
    link.download = 'download.jpg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}