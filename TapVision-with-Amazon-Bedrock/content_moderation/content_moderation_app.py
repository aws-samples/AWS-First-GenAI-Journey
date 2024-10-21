import streamlit as st
import content_moderation.content_moderation_lib as glib
import sys
sys.path.append("../Libs")
import Libs as lib 

def content_moderation():

    st.title("Content Moderation")

    st.subheader("Select an Image") 
    uploaded_file = st.file_uploader("Select an image", type=['png', 'jpeg'], label_visibility="collapsed")
    if uploaded_file:
        uploaded_image_preview = lib.get_bytesio_from_bytes(uploaded_file.getvalue())
        st.image(uploaded_image_preview)
    
    prompt_text = st.text_area(label="Update your prompt", value = glib.prompt)
    go_button = st.button("Validation content", type="primary")
    st.subheader("Result")


    if go_button:
        with st.spinner("Processing..."):
            image_bytes = uploaded_file.getvalue()
            response = glib.get_response_from_model(
            prompt_content=prompt_text, 
            image_bytes=image_bytes
        )
        st.write_stream(response)
