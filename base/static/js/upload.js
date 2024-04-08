document.addEventListener("DOMContentLoaded", function() {
    const dropzoneBox = document.querySelectorAll(".dropzone-box")[0];
    const inputFiles = document.querySelectorAll(".dropzone-area input[type='file']");
    const inputElement = inputFiles[0];
    const dropZoneElement = inputElement.closest(".dropzone-area");

    document.getElementById("uploadForm").addEventListener("submit", function(event) {
        var modelInputs = document.querySelectorAll(".radio-button-input");
        var modelSelected = false;
        
        modelInputs.forEach(function(input) {
            if (input.checked) {
                modelSelected = true;
            }
        });

        if (!modelSelected) {
            alert("Please select a model.");
            event.preventDefault();
            return;
        }

        if (!validateFileType(inputElement)) {
            alert("Please select a video or image file.");
            event.preventDefault();
        }

        showLoader();
    });

    function validateFileType(inputElement) {
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'video/mp4', 'video/mkv', 'video/avi', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska'];
        if (inputElement.files.length === 0) return false;
        const fileType = inputElement.files[0].type;
        return allowedTypes.includes(fileType);
    }

    inputElement.addEventListener("change", (e) => {
        if (inputElement.files.length) {
            if (!validateFileType(inputElement)) {
                alert("Please select a video or image file.");
                inputElement.value = ''; // Clear the input field
                resetDropzoneFileList(dropZoneElement);
                return;
            }
            updateDropzoneFileList(dropZoneElement, inputElement.files[0]);
        } else {
            resetDropzoneFileList(dropZoneElement);
        }
    });

    dropZoneElement.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZoneElement.classList.add("dropzone--over");
    });

    ["dragleave", "dragend"].forEach((type) => {
        dropZoneElement.addEventListener(type, (e) => {
            dropZoneElement.classList.remove("dropzone--over");
        });
    });

    dropZoneElement.addEventListener("drop", (e) => {
        e.preventDefault();
        if (e.dataTransfer.files.length) {
            if (!validateFileType(inputElement)) {
                alert("Please select a video or image file.");
                return;
            }
            inputElement.files = e.dataTransfer.files;
            updateDropzoneFileList(dropZoneElement, e.dataTransfer.files[0]);
        }
        dropZoneElement.classList.remove("dropzone--over");
    });

    const updateDropzoneFileList = (dropzoneElement, file) => {
        let dropzoneFileMessage = dropzoneElement.querySelector(".file-info");
        dropzoneFileMessage.innerHTML = `${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
    };

    const resetDropzoneFileList = (dropzoneElement) => {
        let dropzoneFileMessage = dropzoneElement.querySelector(".file-info");
        dropzoneFileMessage.innerHTML = `No File Selected`;
    };

    document.getElementById("uploadForm").addEventListener("reset", (e) => {
        resetDropzoneFileList(dropZoneElement);
    });

    dropzoneBox.addEventListener("submit", (e) => {
        e.preventDefault();
        const myFile = document.getElementById("upload-file");
        console.log(myFile.files[0]);
    });
});

function showLoader() {
    document.getElementById('loader').style.display = 'block';
    document.getElementById('loading-overlay').style.display = 'block';
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
    document.getElementById('loading-overlay').style.display = 'none';
}

window.addEventListener('load', function() {
    hideLoader();
});