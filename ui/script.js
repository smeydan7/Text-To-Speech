const synthesizeBtn = document.getElementById('synthesize-btn');
const textInput = document.getElementById('text-input');
const voicePresetSelect = document.getElementById('voice-preset-select');
const audioContainer = document.getElementById('audio-container');
const audioPlayer = document.getElementById('audio-player');
const loader = document.getElementById('loader');
const errorMessage = document.getElementById('error-message');

synthesizeBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    const voicePreset = voicePresetSelect.value;
    
    if (!text) {
        showError("Please enter some text to synthesize.");
        return;
    }

    // Reset UI state
    synthesizeBtn.disabled = true;
    synthesizeBtn.textContent = 'Generating...';
    loader.classList.remove('hidden');
    audioContainer.classList.add('hidden');
    errorMessage.classList.add('hidden');

    try {
        const response = await fetch('/synthesize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: text,
                voice_preset: voicePreset || null
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        audioPlayer.src = audioUrl;
        audioContainer.classList.remove('hidden');

    } catch (error) {
        console.error('Synthesis failed:', error);
        showError(`Failed to generate audio. Please check the console or try again. Error: ${error.message}`);
    } finally {
        synthesizeBtn.disabled = false;
        synthesizeBtn.textContent = 'Synthesize Speech';
        loader.classList.add('hidden');
    }
});

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}
