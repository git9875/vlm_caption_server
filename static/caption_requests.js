/*
This JavaScript file handles the form submission for a directory caption request.
The form has a text box for the directory path.
The form has dropdown lists for selecting the model and prompt.
When the form is submitted, a fetch request is sent to the server with the form data.
The server starts a caption job process.
The JavaScript will poll periodically poll the server for the job status and update the UI accordingly.
*/
document.addEventListener('DOMContentLoaded', function() {
    const loadModelBtn = document.getElementById('load-model');
    const stopModelBtn = document.getElementById('stop-model');
    const modelMessage = document.getElementById('model-message');
    const form = document.getElementById('caption-request-form');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressExtra = document.getElementById('progress-extra');
    const resultsTable = document.getElementById('results-table');
    const resultsTableBody = document.getElementById('results-table-body');
    let timerId = null;

    loadModelBtn.addEventListener('click', async function() {
        const selectedModel = document.querySelector('input[name="model"]:checked');
        if (!selectedModel) {
            alert('Please select a model to load');
            return;
        }

        modelMessage.textContent = "Loading model...";
        let response = null;

        try {
            response = await fetch('/load_model_service', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ service_model: selectedModel.value })
            });

            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    const errorText = await response.text();
                    modelMessage.textContent = `Error: ${errorText}`;
                    return;
                }

                const errorData = await response.json();
                
                if ('detail' in errorData) {
                    modelMessage.textContent = `Error: ${errorData.detail}`;
                    return;
                }

                modelMessage.textContent = `Error: ${errorData.message}`;
                return;
            }
        }
        catch (error) {
            modelMessage.textContent = `Error: ${error.message}`;
            return;
        }

        // const data = await response.json();
        modelMessage.textContent = '';
        form.style.display = 'block';
        progressContainer.style.display = 'block';
        resultsTable.style.display = 'table';
    });

    stopModelBtn.addEventListener('click', async function() {
        const response = await fetch('/stop_model_service', {
            method: 'POST'
        });

        const data = await response.json();
        modelMessage.textContent = data.message;
    });


    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const formObject = Object.fromEntries(formData.entries());
        const response = await fetch('/caption_directory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formObject)
        });

        const data = await response.json();
        progressBar.style.width = `0%`;
        progressText.textContent = `0 of 0 files processed`;
        progressExtra.textContent = `0 captioned, 0 errors; ` + data.message;
        resultsTableBody.innerHTML = '';

        for (const fileName of data.files) {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${fileName}</td><td></td><td></td>`;
            resultsTableBody.appendChild(row);
        }

        timerId = setInterval(pollJobStatus, 10000);
    });

    async function pollJobStatus() {
        const response = await fetch(`/caption_directory_status`);
        if (!response.ok) {
            clearInterval(timerId);
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch job status');
        }

        const data = await response.json();

        if (data.processed_files >= data.total_files) {
            clearInterval(timerId);
        }

        const progress = (data.processed_files / data.total_files) * 100;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${data.processed_files} of ${data.total_files} files processed`;
        progressExtra.textContent = `${data.captioned_files} captioned, ${data.error_count} errors`;

        // Update results
        resultsTableBody.innerHTML = '';
        for (const [file, status] of Object.entries(data.file_statuses)) {
            const row = document.createElement('tr');

            if (!('status' in status)) {
                row.innerHTML = `<td>${file}</td><td>Queued</td><td></td>`;
            }
            else if (!('message' in status)) {
                row.innerHTML = `<td>${file}</td><td>${status.status}</td><td></td>`;
            }
            else {
                row.innerHTML = `<td>${file}</td><td>${status.status}</td><td>${status.message}</td>`;
            }

            resultsTableBody.appendChild(row);
        }
    }
});
