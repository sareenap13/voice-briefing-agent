from dotenv import dotenv_values
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from elevenlabs.client import ElevenLabs

config = dotenv_values(".env")

app = FastAPI()
app.mount("/static", StaticFiles(directory = "static"), name = "static")

openai_client = OpenAI(api_key = config.get("OPENAI_API_KEY"))
elevenlabs_client = ElevenLabs(api_key = config.get("ELEVENLABS_API_KEY"))


@app.get("/")
def home():
    return FileResponse("static/index.html")

class BriefRequest(BaseModel):
    article: str = Field(max_length = 10000)
    
@app.post("/brief")
def create_brief(request: BriefRequest):
    if not request.article.strip():
        return {
            "summary": "",
            "audio_file": None,
            "error": "Please enter an article first."
        }
    
    response = openai_client.responses.create(
        model="gpt-5-mini",
        input=f"""
        Summarize the following article into a concise spoken briefing.

        Aim for 60 to 80 words when the article contains enough information.
        For very short articles, use fewer words rather than repeating or
        explaining missing information.

        Only include information that is actually present in the article.
        Do not add recommendations, speculation, background information,
        or information that is not stated in the article.
        Do not mention what the article does not contain.

        Article:
        {request.article}
        """
    )

    summary = response.output_text
    summary = summary[:500]
    print("\nSUMMARY:")
    print(summary)
    print("CHARACTERS:", len(summary))

    try:
        audio = elevenlabs_client.text_to_speech.convert(
            text=summary,
            voice_id="JBFqnCBsd6RMkjVDRZzb",
            model_id="eleven_v3",
            output_format="mp3_44100_128",
        )

        with open("static/briefing.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return {
            "summary": summary,
            "audio_file": "briefing.mp3"
        }

    except Exception as e:
        print("ElevenLabs error:", e)

        return {
            "summary": summary,
            "audio_file": None,
            "error": "Audio could not be generated."
        }
