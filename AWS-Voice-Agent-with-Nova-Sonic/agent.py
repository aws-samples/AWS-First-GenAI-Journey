"""Voice AI Agent using Amazon Nova Sonic + Strands SDK."""
import json
import boto3
import numpy as np
import sounddevice as sd
from strands import Agent, tool

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
MODEL_ID = "amazon.nova-sonic-v1:0"
SAMPLE_RATE = 16000


@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return json.dumps({"location": location, "temp": "72°F", "condition": "Sunny"})


@tool
def search_knowledge(query: str) -> str:
    """Search knowledge base for relevant information."""
    return json.dumps({"query": query, "result": f"Found information about: {query}"})


@tool
def set_reminder(message: str, time: str) -> str:
    """Set a reminder with a message and time."""
    return json.dumps({"status": "set", "message": message, "time": time})


SYSTEM_PROMPT = (
    "You are a helpful voice assistant powered by Amazon Nova Sonic. "
    "You can check weather, search knowledge, and set reminders. "
    "Keep responses concise and natural for voice interaction."
)

agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    tools=[get_weather, search_knowledge, set_reminder],
)


def record_audio(duration: float = 5.0) -> np.ndarray:
    """Record audio from microphone."""
    print(f"Recording for {duration}s...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    print("Recording complete.")
    return audio.flatten()


def stream_to_nova_sonic(audio_data: np.ndarray) -> bytes:
    """Stream audio to Nova Sonic and get audio response."""
    audio_bytes = audio_data.tobytes()
    response = bedrock.invoke_model_with_response_stream(
        modelId=MODEL_ID,
        contentType="audio/lpcm",
        accept="audio/lpcm",
        body=audio_bytes,
    )
    output_audio = b""
    for event in response["body"]:
        if "chunk" in event:
            output_audio += event["chunk"]["bytes"]
    return output_audio


def play_audio(audio_bytes: bytes) -> None:
    """Play audio response through speakers."""
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    sd.play(audio_array, samplerate=SAMPLE_RATE)
    sd.wait()


def process_voice_input(audio_data: np.ndarray) -> bytes:
    """Process voice input through agent and Nova Sonic."""
    response_audio = stream_to_nova_sonic(audio_data)
    return response_audio


def run():
    """Main loop for voice agent."""
    print("Voice Agent ready. Press Ctrl+C to exit.")
    while True:
        try:
            audio = record_audio()
            response = process_voice_input(audio)
            if response:
                play_audio(response)
        except KeyboardInterrupt:
            print("\nExiting.")
            break


if __name__ == "__main__":
    run()
