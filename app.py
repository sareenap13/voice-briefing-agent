import os
from dotenv import dotenv_values
from openai import OpenAI
from elevenlabs.client import ElevenLabs

config = dotenv_values(".env")

openai_key = OpenAI(api_key=config.get("OPENAI_API_KEY"))
elevenlabs_key = ElevenLabs(api_key=config.get("ELEVENLABS_API_KEY"))

article = """
Artificial intelligence is changing how people consume information.
Instead of reading long articles, users can use AI tools to summarize
important developments into shorter, easier-to-understand briefings.
Voice technology can then turn those summaries into audio, allowing
people to listen while commuting, exercising, or doing other tasks.
"""

# summarize with openai
response = openai_key.responses.create(
    model="gpt-5-mini",
    input=f"""
Summarize the following article into a concise spoken briefing
that would take about 60 seconds to read aloud.

Article: {article}"""
)

summary = response.output_text

print("\n--- BRIEFING ---\n")
print(summary)

# turn the briefing into audio
audio = elevenlabs_key.text_to_speech.convert(
    text=summary,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_v3",
    output_format="mp3_44100_128",
)

with open("briefing.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)

print("\nAudio generated successfully!")
print("Saved as briefing.mp3")