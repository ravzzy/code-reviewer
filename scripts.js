document.addEventListener('DOMContentLoaded', function () {
    const maxLengthSelect = document.getElementById('max-length');
    for (let i = 30; i <= 500; i += 30) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i;
        if (i === 150) {
            option.selected = true; // 👈 This makes 150 show as default in the GUI
        }
        maxLengthSelect.appendChild(option);
    }
    
    // Set default server URL if empty
    const serverUrlInput = document.getElementById('server-url');
    if (!serverUrlInput.value) {
        serverUrlInput.value = 'http://localhost:8000';
    }

    // Analyze button handler
    const analyzeBtn = document.getElementById('analyze-btn');
    analyzeBtn.addEventListener('click', async function () {
        const serverUrl = serverUrlInput.value;
        const language = document.getElementById('language').value;
        const maxLength = document.getElementById('max-length').value;
        const code = document.getElementById('code-input').value;
        const resultContainer = document.getElementById('result-container');
        const resultElement = document.getElementById('result');

        // Validate inputs
        if (!serverUrl || !code) {
            alert('Please provide both the server URL and your code.');
            return;
        }

        // Set loading state
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = 'Analyzing...';
        resultContainer.style.display = 'none';

        try {
            console.log('Sending request to:', serverUrl);
            console.log('Code length:', code.length, 'chars');
            console.log('Selected max tokens:', maxLength);

            // First check server health
            const healthResponse = await fetch(`${serverUrl}/health`, {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });

            if (!healthResponse.ok) {
                throw new Error('Server is not healthy');
            }

            const healthData = await healthResponse.json();
            console.log('Server health:', healthData);

            if (!healthData.model_loaded) {
                throw new Error('Model not loaded on server');
            }

            // Send analysis request
            const startTime = performance.now();
            console.log('Sending request to model hosted server:', startTime);

            const response = await fetch(`${serverUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    language,
                    max_length: Math.min(parseInt(maxLength, 10), 500),
                    code
                })
            });

            const endTime = performance.now();
            console.log(`Request took ${(endTime - startTime).toFixed(2)}ms`);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Server error:', errorData);
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const data = await response.json();
            console.log('Analysis successful:', data);

            // Display results
            resultElement.textContent = data.analysis;
            resultContainer.style.display = 'block';

        } catch (error) {
            console.error('Error:', error);
            resultElement.textContent = `Error: ${error.message}`;
            resultContainer.style.display = 'block';

            // Show detailed error for debugging
            if (confirm(`Analysis failed: ${error.message}\n\nShow detailed error in console?`)) {
                console.error('Full error details:', error);
            }
        } finally {
            // Reset button state
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze';
        }
    });

    // Copy button handler
    const copyBtn = document.getElementById('copy-btn');
    copyBtn.addEventListener('click', function () {
        const resultElement = document.getElementById('result');
        navigator.clipboard.writeText(resultElement.textContent)
            .then(() => alert('Result copied to clipboard!'))
            .catch(err => console.error('Copy failed:', err));
    });

    // Toggle instructions handler
    const toggleInstructionsBtn = document.getElementById('toggle-instructions');
    const instructionsContent = document.getElementById('instructions-content');
    instructionsContent.style.display = 'none'; // Start collapsed

    toggleInstructionsBtn.addEventListener('click', function () {
        if (instructionsContent.style.display === 'none') {
            instructionsContent.style.display = 'block';
        } else {
            instructionsContent.style.display = 'none';
        }
    });

    // Populate instructions content
    instructionsContent.innerHTML = `
        <h2>An AI-powered code review assistant running Phi-2 locally on your machine for private, anonymous, no-ads and secure code analysis without sharing your code online.</h2>
      <h3>Serving the Phi-2 Model Locally with FastAPI</h3>
      <ol>
          <li>Ensure Python: Version 3.8 or higher (recommended: 3.10) is installed on your machine</li>
          <li>Required Python packages: fastapi, uvicorn, transformers, torch and safetensors (ignore the packages that have been installed already)
              <pre>brew install python@3.10</pre>
              <pre>python3.10 --version</pre>
              <pre>python3.10 -m pip install --upgrade pip</pre>
              <pre>python3.10 -m pip install fastapi uvicorn transformers torch safetensors</pre>
              <pre>python3.10 -m pip install --upgrade git+https://github.com/huggingface/transformers.git</pre>
          </li>
          <li>Download the below model files from the <a href="https://huggingface.co/microsoft/phi-2/tree/main" target="_blank">Official Hugging Face Page</a> and place it in the correct directory</li>
            <pre>model-00001-of-00002.safetensors</pre>
            <pre>model-00002-of-00002.safetensors</pre>
            <pre>generation_config.json</pre>
            <pre>tokenizer.json</pre>
            <pre>tokenizer_config.json</pre>
            <pre>config.json</pre>
            <pre>special_tokens_map.json</pre>
            <pre>vocab.json</pre>
            <pre>merges.txt</pre>
            <li>Download and update the server.py file to load the Phi-2 model using the correct local model path where you kept the above files.</li>
          <li>Run the server (either of the below commands):
              <pre>uvicorn server:app --host 0.0.0.0 --port 8000</pre>
              <pre>python3.10 -m uvicorn server:app --host 0.0.0.0 --port 8000</pre>
          </li>
          <li>The API will be available at <a href="http://localhost:8000" target="_blank">http://localhost:8000</a>, if you have changed the port update Local Server URL below</li>
      </ol>
      <br>
      <h3>Troubleshooting</h3>
      <ul>
          <li>To view the server logs in real-time:
            <pre>tail -f code_analysis.log</pre>
            </li>
            <li>If running with CUDA-enabled PyTorch, verify GPU status (Optional):
            <pre>curl http://localhost:8000/gpu-info | jq</pre>

          <li>Try smaller code snippets first</li>
          <li>Reduce max tokens if getting memory errors, recommended is 150 for optimum information.</li>
      </ul>
  `;
});