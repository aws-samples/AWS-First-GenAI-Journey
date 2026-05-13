import streamlit as st
import boto3
import uuid
import time
import json

st.title("Meeting Summarizer with Amazon Bedrock")

s3 = boto3.client("s3")
transcribe = boto3.client("transcribe")
bedrock = boto3.client("bedrock-runtime")

BUCKET = st.text_input("S3 Bucket for audio upload", "meeting-summarizer-" + boto3.client("sts").get_caller_identity()["Account"])

uploaded = st.file_uploader("Upload meeting audio/video", type=["mp3", "mp4", "wav", "m4a", "webm"])

if uploaded and st.button("Transcribe & Summarize"):
    with st.spinner("Uploading to S3..."):
        key = f"uploads/{uuid.uuid4()}/{uploaded.name}"
        s3.put_object(Bucket=BUCKET, Key=key, Body=uploaded.read())

    job_name = f"meeting-{uuid.uuid4().hex[:8]}"
    media_uri = f"s3://{BUCKET}/{key}"
    ext = uploaded.name.rsplit(".", 1)[-1]
    fmt_map = {"mp3": "mp3", "mp4": "mp4", "wav": "wav", "m4a": "mp4", "webm": "webm"}

    with st.spinner("Transcribing with Amazon Transcribe..."):
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": media_uri},
            MediaFormat=fmt_map.get(ext, "mp3"),
            LanguageCode="en-US",
            Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": 10},
        )
        while True:
            resp = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = resp["TranscriptionJob"]["TranscriptionJobStatus"]
            if status in ("COMPLETED", "FAILED"):
                break
            time.sleep(5)

    if status == "FAILED":
        st.error("Transcription failed.")
    else:
        import urllib.request
        transcript_url = resp["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        transcript_json = json.loads(urllib.request.urlopen(transcript_url).read())
        transcript_text = transcript_json["results"]["transcripts"][0]["transcript"]

        st.subheader("Transcript")
        st.text_area("Full transcript", transcript_text, height=150)

        prompt = f"""Analyze this meeting transcript and provide:
1. **Summary** - A concise summary of the meeting
2. **Action Items** - List each action item with the responsible person
3. **Key Decisions** - List decisions made during the meeting
4. **Attendee Contributions** - Summarize each speaker's main contributions

Transcript:
{transcript_text}"""

        with st.spinner("Summarizing with Bedrock..."):
            response = bedrock.converse(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                messages=[{"role": "user", "content": [{"text": prompt}]}],
            )
            summary = response["output"]["message"]["content"][0]["text"]

        st.subheader("Meeting Analysis")
        st.markdown(summary)
