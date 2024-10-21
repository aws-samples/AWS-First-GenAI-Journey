import streamlit as st
import product_description_lib as glib
import sys
sys.path.append("../Libs")
import Libs as lib 


def product_description():

    st.title("Generate Product Description")
    prompt_text =""

    st.subheader("Select an Image") 
    uploaded_file = st.file_uploader("Select an image", type=['png', 'jpeg'], label_visibility="collapsed")
    if uploaded_file:
        uploaded_image_preview = lib.get_bytesio_from_bytes(uploaded_file.getvalue())
        st.image(uploaded_image_preview)
    
    prizm = st.text_area(label="Update your PRIZM", value = lib.prizm)
    go_button = st.button("Generate Product Description", type="primary")
    st.subheader("Result")


    if go_button:
        with st.spinner("Processing..."):
            image_bytes = uploaded_file.getvalue()
            response = glib.get_response_from_model(
            prompt_content=prompt_text, 
            image_bytes=image_bytes,
            prizm=prizm
        )
        st.write_stream(response)
