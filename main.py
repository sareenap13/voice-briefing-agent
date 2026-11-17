from dotenv import dotenv_values
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import time
import re
from request_cost_tracking import calculate_openai_cost_dollars, calculate_elevenlabs_cost_dollars, append_request_metrics_to_log

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

MAX_SPOKEN_SUMMARY_CHARACTERS = 500


def trim_summary_to_last_full_sentence(summary_text, max_characters=MAX_SPOKEN_SUMMARY_CHARACTERS):
    summary_text = summary_text.strip()
    if len(summary_text) <= max_characters:
        return summary_text

    sentence_end_positions = [
        sentence_end_match.end()
        for sentence_end_match in re.finditer(r"[.!?](?=\s|$)", summary_text)
        if sentence_end_match.end() <= max_characters
    ]
    if sentence_end_positions:
        return summary_text[:sentence_end_positions[-1]]

    text_within_limit = summary_text[:max_characters]
    last_space_position = text_within_limit.rfind(" ")
    return text_within_limit[:last_space_position].rstrip(",;:") + "."

@app.post("/brief")
def create_brief(request: BriefRequest):
    if not request.article.strip():
        return {
            "summary": "",
            "audio_file": None,
            "error": "Please enter an article first."
        }

    summary_start_time = time.perf_counter()

    response = openai_client.responses.create(
        model = "gpt-5-mini",
        reasoning={"effort": "minimal"},
        input = f"""
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

    summary_latency_seconds = time.perf_counter() - summary_start_time
    summary = response.output_text
    summary = trim_summary_to_last_full_sentence(summary)
    print("\nSUMMARY:")
    print(summary)
    print("CHARACTERS:", len(summary))

    speech_start_time = time.perf_counter()
    audio_generation_succeeded = False

    try:
        audio = elevenlabs_client.text_to_speech.convert(
            text=summary,
            voice_id = "JBFqnCBsd6RMkjVDRZzb",
            model_id = "eleven_v3",
            output_format = "mp3_44100_128",
        )

        with open("static/briefing.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)

        audio_generation_succeeded = True

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

    finally:
        append_request_metrics_to_log({
            "summary_latency_seconds": round(summary_latency_seconds, 3),
            "speech_latency_seconds": round(time.perf_counter() - speech_start_time, 3),
            "summary_input_tokens": response.usage.input_tokens,
            "summary_output_tokens": response.usage.output_tokens,
            "summary_cost_dollars": calculate_openai_cost_dollars(
                response.usage.input_tokens, response.usage.output_tokens
            ),
            "speech_cost_dollars": calculate_elevenlabs_cost_dollars(summary),
            "audio_generation_succeeded": audio_generation_succeeded,
        })
