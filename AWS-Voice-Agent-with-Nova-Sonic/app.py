"""Streamlit UI for Voice Agent with Nova Sonic."""
import streamlit as st
import numpy as np
from agent import process_voice_input, SAMPLE_RATE

st.set_page_config(page_title="Voice Agent - Nova Sonic", page_icon="🎙️")
st.title("🎙️ Voice Agent with Amazon Nova Sonic")

if "history" not in st.session_state:
    st.session_state.history = []

audio_input = st.audio_input("Speak to the agent")

if audio_input:
    st.audio(audio_input, format="audio/wav")
    audio_bytes = audio_input.getvalue()
    audio_array = np.frombuffer(audio_bytes[44:], dtype=np.int16)  # skip WAV header

    with st.spinner("Processing..."):
        response_audio = process_voice_input(audio_array)

    if response_audio:
        st.session_state.history.append({"role": "user", "audio": audio_bytes})
        st.session_state.history.append({"role": "assistant", "audio": response_audio})
        st.audio(response_audio, format="audio/wav", sample_rate=SAMPLE_RATE)

st.subheader("Chat History")
for i, msg in enumerate(st.session_state.history):
    role = "🧑 You" if msg["role"] == "user" else "🤖 Assistant"
    with st.expander(f"{role} - Message {i // 2 + 1}"):
        st.audio(msg["audio"], format="audio/wav")
