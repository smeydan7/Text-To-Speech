
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded');
    
    const synthesizeBtn = document.getElementById('synthesize-btn');
    const textInput = document.getElementById('text-input');
    const audioContainer = document.getElementById('audio-container');
    const audioPlayer = document.getElementById('audio-player');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('error-message');

    // Check if elements exist
    console.log('Elements found:', {
        synthesizeBtn: !!synthesizeBtn,
        textInput: !!textInput,
        audioContainer: !!audioContainer,
        audioPlayer: !!audioPlayer,
        loader: !!loader,
        errorMessage: !!errorMessage
    });

    if (!synthesizeBtn || !textInput) {
        console.error('Required elements not found!');
        return;
    }

    synthesizeBtn.addEventListener('click', async () => {
        console.log('Button clicked!');
        const text = textInput.value.trim();
        console.log('Text value:', text);
        
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
            console.log('Sending request to /synthesize');
            const response = await fetch('/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text
                }),
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            
            audioPlayer.src = audioUrl;
            audioContainer.classList.remove('hidden');
            console.log('Audio generated successfully!');

        } catch (error) {
            console.error('Synthesis failed:', error);
            showError(`Failed to generate audio: ${error.message}`);
        } finally {
            synthesizeBtn.disabled = false;
            synthesizeBtn.textContent = 'Synthesize Speech';
            loader.classList.add('hidden');
        }
    });

    textInput.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            synthesizeBtn.click();
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }
});