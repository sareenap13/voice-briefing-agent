# Voice Briefing Agent

A lightweight AI-powered web app that turns written articles or notes into concise spoken briefings.

The user pastes text into the app, and the application uses OpenAI to generate a short summary and ElevenLabs to convert that summary into speech. The resulting audio can then be played directly in the browser.

## Demo

**Pipeline:**

`Article / Notes → OpenAI → Concise Briefing → ElevenLabs → Audio`

## Features

* Paste an article or notes into a simple web interface
* Generate a concise AI briefing
* Convert the briefing into speech using ElevenLabs
* Play the generated audio directly in the browser
* Input validation for empty and oversized articles
* Loading and error states
* Prevents outdated audio from being played after new input
* Handles text-to-speech failures without crashing the application

## Tech Stack

* **Python**
* **FastAPI** — backend API
* **OpenAI API** — generates the briefing
* **ElevenLabs API** — converts the briefing to speech
* **HTML / CSS / JavaScript** — frontend
* **Uvicorn** — local development server
* **python-dotenv** — environment variable management

## How It Works

### 1. User submits an article

The frontend sends the article to the FastAPI backend as JSON:

```json
{
  "article": "Article text goes here..."
}
```

### 2. FastAPI validates the request

The backend checks that:

* The article isn't empty
* The article is no longer than 10,000 characters

### 3. OpenAI generates the briefing

The article is sent to OpenAI, which produces a concise spoken briefing.

The application asks the model to target approximately 60–80 words while only using information contained in the original article.

A 500-character safety limit is also applied to the generated summary before it is sent to the text-to-speech service.

### 4. ElevenLabs generates the audio

The generated briefing is sent to ElevenLabs using text-to-speech.

The resulting MP3 is saved locally and served through the FastAPI application.

### 5. The browser plays the briefing

The frontend receives the generated response and loads the audio into an HTML audio player.

A cache-busting query parameter is used when loading new audio so the browser does not accidentally reuse an older briefing.

## Project Structure

```text
voice-briefing-agent/
│
├── static/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── briefing.mp3
│
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

> `.env` and generated audio files should not be committed to GitHub.

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd voice-briefing-agent
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API keys

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

Do not commit this file to GitHub.

### 5. Start the application

```bash
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## Example

Paste an article such as:

> The New York City marathon will take place Sunday. More than 50,000 runners are expected to participate. The race will begin in Staten Island and finish in Central Park.

The application generates a concise briefing and, when ElevenLabs audio generation is available, produces an audio version that can be played in the browser.

## Error Handling

The application handles several common failure cases:

* Empty article submission
* Articles exceeding the 10,000-character limit
* Failed API requests
* ElevenLabs text-to-speech failures
* Missing generated audio

For example, if ElevenLabs cannot generate audio, the application still displays the generated briefing and informs the user that audio is unavailable rather than returning an unhandled server error.

## What I Built

This project was built to practice integrating AI APIs into a complete web application rather than using an LLM or text-to-speech API in isolation.

The main engineering pieces include:

* Designing a FastAPI endpoint for AI processing
* Connecting multiple external APIs into a single workflow
* Validating user input before making API calls
* Handling asynchronous frontend requests with JavaScript
* Managing loading, success, and error states
* Preventing stale browser audio from being reused
* Managing API credentials with environment variables
* Building a simple end-to-end AI product from frontend to backend to external services

## Future Improvements

Potential next steps include:

* URL input so users can submit an article link directly
* More control over briefing length
* Multiple voice options
* A progress indicator during generation
* Better audio file management
* Deployment to a cloud platform
* Automated tests for API and validation behavior
* More sophisticated article extraction and cleaning