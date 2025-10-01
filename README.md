## Text-to-Speech Application 🎤

This project is a simple web application that converts text into speech using a locally-run Hugging Face model. It uses a FastAPI backend to handle the speech synthesis and serves a simple HTML frontend for user interaction.

# Features
* Backend: Built with Python and FastAPI.
* AI Model: Utilizes the suno/bark-small model from Hugging Face for high-quality, realistic speech generation.
* Local Inference: The model runs entirely on your local machine. No external API calls are needed for the speech synthesis.

# Setup and Installation

Ensure you have python 3.8 or newer.

After cloning the repository:

1. Create a virtual environment `python -m venv venv`
2. Activate the environment `source venv/bin/activate`
3. Install necessary python libraries using `pip`: `pip install "fastapi[all]" uvicorn "transformers[torch]" torch soundfile`
4. Run the app from the root directory `uvicorn main:app --reload` (NOTE: the first time you start the server, the model will be downloaded from Hugging Face thus it may take some time and requires a stable internet connection)
5. Once the server is running go to `http://127.0.0.1:8000` to access the UI and use the app
