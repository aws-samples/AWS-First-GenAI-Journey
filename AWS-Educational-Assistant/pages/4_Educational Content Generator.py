import streamlit as st
import Libs as glib

st.set_page_config(page_title="Educational Content Generator", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for full-screen UI design
st.markdown("""
    <style>
    body {
        background-color: #FFFFFF; /* Background trắng */
        margin: 0;
        padding: 0;
        overflow-x: hidden;
    }
    .main {
        background-color: #FFFFFF; /* Nền trắng cho phần chính */
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 0 auto;
        width: 100vw;
        height: 100vh;
        overflow-y: auto;
    }
    .stButton > button {
        background-color: #6A9CFD; /* Màu xanh dương nhạt */
        color: white;
        border: none;
        padding: 12px 24px;
        text-align: center;
        font-size: 16px;
        margin: 10px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #AEE4FF; /* Màu xanh dương nhạt hơn khi hover */
    }
    .stTextInput textarea, .stTextInput input {
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #ccc;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
        width: 100%;
        margin-bottom: 20px;
    }
    .stTextInput {
        margin-bottom: 20px;
    }
    .stMarkdown p {
        font-size: 1.1rem;
    }
    .stSelectbox {
        margin-bottom: 20px;
        width: 100%;
    }
    .sidebar .sidebar-content {
        padding: 20px;
        background-color: #FFBFB3; /* Màu cam nhạt cho sidebar */
        border-radius: 10px;
    }
    .columns {
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }
    .columns > div {
        flex: 1;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Educational Content Generator")
st.subheader("Create Custom Educational Content")

# Initialize session state variables if not present
if "clear_topic" not in st.session_state:
    st.session_state["clear_topic"] = ""
if "clear_subject" not in st.session_state:
    st.session_state["clear_subject"] = ""
if "clear_audience" not in st.session_state:
    st.session_state["clear_audience"] = "High School Students"

# Input fields for educational content generation
input_topic = st.text_input("Enter the topic for the lesson", value=st.session_state["clear_topic"])
subject_area = st.text_input("Enter the subject area", value=st.session_state["clear_subject"])
audience_level = st.selectbox("Select the target audience level", ["High School Students", "College Students", "Professionals"], index=["High School Students", "College Students", "Professionals"].index(st.session_state["clear_audience"]))

# Action buttons in a single row
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Generate Content"):
        if input_topic and subject_area and audience_level:
            with st.spinner("Generating educational content..."):
                # Create the formatted prompt
                prompt_template = (
                    "You are an expert educator with deep knowledge in {subject_area}. "
                    "Your task is to create an engaging and informative lesson on the topic of '{input_topic}'. "
                    "The content should be suitable for {audience_level}, and it should include the following elements:\n\n"
                    "1. **Introduction**: Start with an introduction that explains the importance of the topic and how it relates to the broader subject area.\n\n"
                    "2. **Key Concepts**: Clearly define and explain the key concepts, theories, or principles related to the topic. Use simple language and examples to ensure understanding.\n\n"
                    "3. **Practical Applications**: Describe how these concepts can be applied in real-world scenarios. Provide at least two examples or case studies.\n\n"
                    "4. **Common Misconceptions**: Identify any common misconceptions about the topic and provide clarifications to correct these misunderstandings.\n\n"
                    "5. **Summary**: End with a summary that recaps the main points covered in the lesson, highlighting the most important takeaways.\n\n"
                    "6. **Further Reading**: Suggest additional resources or readings for students who want to explore the topic in more depth.\n\n"
                    "Please write the content in a clear, concise, and engaging manner, suitable for the specified audience. Ensure that the information is accurate and up-to-date.\n\n"
                    "Here is the topic for the lesson:\n"
                    "{input_topic}\n\n"
                    "You may begin your lesson."
                )
                formatted_prompt = prompt_template.format(
                    subject_area=subject_area,
                    input_topic=input_topic,
                    audience_level=audience_level
                )
                
                response_text = ""
                # Call the generator function with the formatted prompt
                for response_chunk in glib.call_claude_sonet_stream(formatted_prompt):
                    if response_chunk:  # Check if response_chunk is not None
                        response_text += response_chunk
                
                st.markdown(response_text)  # Display the combined response as markdown

            st.success("Content generation complete.")
        else:
            st.warning("Please fill out all fields before submitting.")

with col2:
    if st.button("Clear"):
        st.session_state["clear_topic"] = ""
        st.session_state["clear_subject"] = ""
        st.session_state["clear_audience"] = "High School Students"
        st.experimental_rerun()

# Sidebar with info and user guide
st.sidebar.title("Educational Content Generator")
st.sidebar.info("""
    **How to Use:**
    1. Enter the topic for the lesson.
    2. Specify the subject area.
    3. Choose the target audience level.
    4. Click 'Generate Content' to receive a custom lesson plan.
    5. If needed, click 'Clear' to reset the inputs.
""")

# Sidebar with additional resources
st.sidebar.markdown("### Additional Resources")
st.sidebar.markdown("""
    - [Educational Resources](https://www.education.com/)
    - [Teaching Strategies](https://www.edutopia.org/)
    - [Lesson Plan Ideas](https://www.lessonplans.com/)
""")

st.sidebar.markdown("### About This Tool")
st.sidebar.markdown("""
    This tool helps educators create customized lesson plans based on specific topics and audience levels. 
    It's designed to save time and ensure content is tailored to students' needs.
""")
