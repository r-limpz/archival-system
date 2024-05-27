const dropzone = document.getElementById('dropzone');
const documentImageInput = document.getElementById('document_image');
const previewContainer = document.getElementById('previewContainer');
const preview = document.getElementById('preview');
const dragText = document.getElementById('dragText');
const ocr_button = document.getElementById('submitOCR');
const save_button = document.getElementById('continueButton');
let isContinueClicked = false;

dropzone.addEventListener('click', () => {
    if (!isContinueClicked) {
        documentImageInput.click();
    }
});

documentImageInput.addEventListener('change', handleFiles);

dropzone.addEventListener('dragover', (e) => {
    if (!isContinueClicked) {
        e.preventDefault();
        dropzone.classList.add('dragging');
    }
});

dropzone.addEventListener('dragleave', () => {
    if (!isContinueClicked) {
        dropzone.classList.remove('dragging');
    }
});

dropzone.addEventListener('drop', (e) => {
    if (!isContinueClicked) {
        e.preventDefault();
        dropzone.classList.remove('dragging');
        const files = e.dataTransfer.files;
        if (files.length) {
            handleFiles({ target: { files } });
        }
    }
});

function handleFiles(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            previewContainer.classList.remove('d-none');
            save_button.classList.remove('d-none');
            dragText.classList.add('d-none');
        };
        reader.readAsDataURL(file);
    }
}

cancel_selectedDocument.addEventListener('click', function (event) {
    event.stopPropagation();
    preview.src = '';
    ocr_button.classList.add('d-none');
    save_button.classList.add('d-none');
    previewContainer.classList.add('d-none');
    dragText.classList.remove('d-none');
    documentImageInput.value = '';
    isContinueClicked = false;
});

cancel_image.addEventListener('click', function (event) {
    event.stopPropagation();
    preview.src = '';
    ocr_button.classList.add('d-none');
    save_button.classList.add('d-none');
    previewContainer.classList.add('d-none');
    dragText.classList.remove('d-none');
    documentImageInput.value = '';
    isContinueClicked = false;
});

function saveImage() {
    isContinueClicked = true;
    ocr_button.classList.remove('d-none');
    save_button.classList.add('d-none');
}

continueButton.addEventListener('click', function (event) {
    event.stopPropagation();
    saveImage();
});

document.addEventListener('DOMContentLoaded', () => {
    const preview = document.getElementById('preview');

    let scale = 1;
    const scaleStep = 0.1;
    const maxScale = 3;
    const minScale = 0.5;

    document.getElementById('previewContainer').addEventListener('wheel', (event) => {
        event.preventDefault(); // Prevent default scrolling behavior

        if (event.deltaY < 0) {
            // Scrolling up, zoom in
            if (scale < maxScale) {
                scale += scaleStep;
                updateScale();
            }
        } else {
            // Scrolling down, zoom out
            if (scale > minScale) {
                scale -= scaleStep;
                updateScale();
            }
        }
    });

    function updateScale() {
        preview.style.transform = `scale(${scale})`;
    }
});
