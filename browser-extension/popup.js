// popup.js - Handle URL submission from popup

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('submit-form');
  const urlInput = document.getElementById('article-url');
  const submitBtn = document.getElementById('submit-btn');
  const statusDiv = document.getElementById('status');

  // Pre-fill with current tab URL
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    if (tabs[0] && tabs[0].url) {
      urlInput.value = tabs[0].url;
    }
  });

  form.addEventListener('submit', async function(e) {
    e.preventDefault();

    const url = urlInput.value.trim();
    if (!url) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    statusDiv.textContent = '';

    try {
      // Submit to backend API
      const response = await fetch('http://localhost:8000/api/v1/articles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url,
          user_id: 'browser_extension'
        })
      });

      if (response.ok) {
        const data = await response.json();
        statusDiv.textContent = 'Article submitted successfully!';
        statusDiv.className = 'status success';

        // Store job ID for polling
        chrome.storage.local.set({ jobId: data.job_id });

        // Start polling in background
        chrome.runtime.sendMessage({
          type: "TRACK_JOB",
          jobId: data.id
        });

        // Close popup after success
        setTimeout(() => window.close(), 2000);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Submission error:', error);
      statusDiv.textContent = 'Failed to submit article. Please try again.';
      statusDiv.className = 'status error';
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Submit Article';
    }
  });
});