import streamlit as st 
import Libs as glib 
import json
import sys
sys.path.append("../Libs")
import Libs as lib 


def main():
    st.title("Input your text and image")
    st.markdown("Generate Katalon code to test the page") 
    st.markdown("Count number of pigs in the image") 

    input_text = st.text_area("Input your question") 
    image_bytes = ""
    st.subheader("Select an Image") 
    uploaded_file = st.file_uploader("Select an image", type=['png', 'jpeg'], label_visibility="collapsed")
    if uploaded_file:
        uploaded_image_preview = lib.get_bytesio_from_bytes(uploaded_file.getvalue())
        image_bytes = uploaded_file.getvalue()

        st.image(uploaded_image_preview)

    go_button = st.button("Go", type="primary")

    if input_text and go_button: 
        response = glib.get_response_from_model(input_text, image_bytes)
        st.write_stream(response)
    
    
