document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const uploadSection = document.getElementById('uploadSection');
    const progressSection = document.getElementById('progressSection');
    const messageSection = document.getElementById('messageSection');
    const message = document.getElementById('message');
    const progressText = document.getElementById('progressText');
    const downloadBtn = document.getElementById('downloadBtn');
    const convertAnotherBtn = document.getElementById('convertAnotherBtn');

    let downloadUrl = '';
    let downloadFilename = '';

    browseBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        fileInput.click();
    });

    dropZone.addEventListener('click', function() {
        fileInput.click();
    });

    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    convertAnotherBtn.addEventListener('click', function() {
        resetUI();
    });

    downloadBtn.addEventListener('click', function() {
        if (downloadUrl) {
            window.location.href = downloadUrl;
        }
    });

    function handleFile(file) {
        const maxSizeMB = parseInt(document.querySelector('.file-info').textContent.match(/\d+/)[0]);
        const maxSizeBytes = maxSizeMB * 1024 * 1024;

        if (!file.name.toLowerCase().endsWith('.xlsx')) {
            showError('Please upload a .xlsx file');
            return;
        }

        if (file.size > maxSizeBytes) {
            showError(`File exceeds ${maxSizeMB}MB limit`);
            return;
        }

        uploadFile(file);
    }

    function uploadFile(file) {
        showProgress('Uploading file...');

        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                if (percentComplete < 100) {
                    progressText.textContent = `Uploading... ${percentComplete}%`;
                } else {
                    progressText.textContent = 'Converting file...';
                }
            }
        });

        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        downloadUrl = response.download_url;
                        downloadFilename = response.filename;
                        showSuccess(`Conversion successful! File: ${downloadFilename}`);
                    } else {
                        showError(response.error || 'Conversion failed');
                    }
                } catch (e) {
                    showError('Invalid response from server');
                }
            } else {
                try {
                    const response = JSON.parse(xhr.responseText);
                    showError(response.error || 'Upload failed');
                } catch (e) {
                    showError(`Upload failed with status ${xhr.status}`);
                }
            }
        });

        xhr.addEventListener('error', function() {
            showError('Network error. Please check your connection.');
        });

        xhr.addEventListener('timeout', function() {
            showError('Request timeout. Please try again.');
        });

        xhr.open('POST', '/upload', true);
        xhr.timeout = 120000;
        xhr.send(formData);
    }

    function showProgress(text) {
        progressText.textContent = text;
        dropZone.parentElement.classList.add('hidden');
        progressSection.classList.remove('hidden');
        messageSection.classList.add('hidden');
    }

    function showSuccess(text) {
        message.textContent = text;
        message.className = 'message success';
        downloadBtn.classList.remove('hidden');
        dropZone.parentElement.classList.add('hidden');
        progressSection.classList.add('hidden');
        messageSection.classList.remove('hidden');

        // Trigger automatic download
        if (downloadUrl) {
            setTimeout(function() {
                window.location.href = downloadUrl;
            }, 500);
        }
    }

    function showError(text) {
        message.textContent = text;
        message.className = 'message error';
        downloadBtn.classList.add('hidden');
        dropZone.parentElement.classList.add('hidden');
        progressSection.classList.add('hidden');
        messageSection.classList.remove('hidden');
    }

    function resetUI() {
        fileInput.value = '';
        downloadUrl = '';
        downloadFilename = '';
        dropZone.parentElement.classList.remove('hidden');
        progressSection.classList.add('hidden');
        messageSection.classList.add('hidden');
        message.className = 'message';
        message.textContent = '';
        downloadBtn.classList.add('hidden');
    }
});
