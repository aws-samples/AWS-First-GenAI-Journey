"""Streamlit app for Amazon Nova Model Distillation."""

import streamlit as st
from distill import start_distillation_job, get_job_status

st.set_page_config(page_title="Amazon Nova Model Distillation", page_icon="🧬")
st.title("🧬 Amazon Nova Model Distillation")
st.markdown("Create smaller, faster models by distilling knowledge from larger teacher models.")

TEACHER_MODELS = {
    "Amazon Nova Pro": "amazon.nova-pro-v1:0",
    "Amazon Nova Lite": "amazon.nova-lite-v1:0",
    "Amazon Nova Premier": "amazon.nova-premier-v1:0",
}

STUDENT_MODELS = {
    "Amazon Nova Micro": "amazon.nova-micro-v1:0",
    "Amazon Nova Lite": "amazon.nova-lite-v1:0",
}

st.header("1. Select Models")
col1, col2 = st.columns(2)
with col1:
    teacher = st.selectbox("Teacher Model (larger)", list(TEACHER_MODELS.keys()))
with col2:
    student = st.selectbox("Student Model (smaller)", list(STUDENT_MODELS.keys()))

st.header("2. Configure Distillation")
job_name = st.text_input("Job Name", "nova-distillation-demo")
training_s3 = st.text_input("Training Data S3 URI", "s3://my-bucket/distillation/train.jsonl")
output_s3 = st.text_input("Output S3 URI", "s3://my-bucket/distillation/output/")

col1, col2, col3 = st.columns(3)
with col1:
    epochs = st.number_input("Epochs", min_value=1, max_value=10, value=3)
with col2:
    batch_size = st.selectbox("Batch Size", [4, 8, 16, 32], index=1)
with col3:
    lr = st.number_input("Learning Rate", min_value=1e-6, max_value=1e-3, value=1e-5, format="%.1e")

st.header("3. Launch Distillation")
if st.button("🚀 Start Distillation Job", type="primary"):
    try:
        job_arn = start_distillation_job(
            job_name=job_name,
            teacher_model_id=TEACHER_MODELS[teacher],
            student_model_id=STUDENT_MODELS[student],
            training_data_s3=training_s3,
            output_s3=output_s3,
            max_epochs=epochs,
            batch_size=batch_size,
            learning_rate=lr,
        )
        st.success(f"Job launched! ARN: `{job_arn}`")
        st.session_state["job_arn"] = job_arn
    except Exception as e:
        st.error(f"Failed to start job: {e}")

st.header("4. Check Job Status")
job_arn_input = st.text_input("Job ARN", value=st.session_state.get("job_arn", ""))
if st.button("🔄 Refresh Status") and job_arn_input:
    try:
        status = get_job_status(job_arn_input)
        st.json({"status": status["status"], "jobName": status.get("jobName", ""),
                 "creationTime": str(status.get("creationTime", "")),
                 "outputModelName": status.get("outputModelName", "")})
        if status["status"] == "Completed":
            st.balloons()
            st.success("✅ Distillation complete! Your smaller model is ready.")
        elif status["status"] == "Failed":
            st.error(f"Job failed: {status.get('failureMessage', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error checking status: {e}")
