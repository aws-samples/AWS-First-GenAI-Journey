import streamlit as st
import pandas as pd
from transformers import AutoTokenizer
import streamlit.components.v1 as components
import random

icons = {
    "assistant": "img/fcj.png",
    "user": "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/amazonwebservices/amazonwebservices-original-wordmark.svg",
}

particles_js = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Particles.js</title>
  <style>
  #particles-js {
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: -1; /* Send the animation to the back */
  }
  .content {
    position: relative;
    z-index: 1;
    color: white;
  }
  
</style>
</head>
<body>
  <div id="particles-js"></div>
  <div class="content">
    <!-- Placeholder for Streamlit content -->
  </div>
  <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
  <script>
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 300,
          "density": {
            "enable": true,
            "value_area": 800
          }
        },
        "color": {
          "value": "#000000"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#ffffff"
          },
          "polygon": {
            "nb_sides": 5
          },
          "image": {
            "src": "img/github.svg",
            "width": 100,
            "height": 100
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.2,
            "sync": false
          }
        },
        "size": {
          "value": 2,
          "random": true,
          "anim": {
            "enable": false,
            "speed": 40,
            "size_min": 0.1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#000000",
          "opacity": 0.22,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 0.2,
          "direction": "none",
          "random": false,
          "straight": false,
          "out_mode": "out",
          "bounce": true,
          "attract": {
            "enable": false,
            "rotateX": 600,
            "rotateY": 1200
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": true,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 2,
            "duration": 2,
            "opacity": 0.5,
            "speed": 1
          },
          "repulse": {
            "distance": 200,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 2
          },
          "remove": {
            "particles_nb": 3
          }
        }
      },
      "retina_detect": true
    });
  </script>
</body>
</html>
"""
welcome_messages = [
    "Xin chào! Tôi là AWS First GenAI Journey, trợ lý AI. Bạn hãy hỏi tôi bất cứ điều gì!",
    "Chào! Tôi là AWS First GenAI Journey, trợ lý AI giải thích dữ liệu First GenAI Journey. Tôi có thể giúp gì cho bạn?",
    "Hey! Tôi là AWS First GenAI Journey, hướng dẫn viên AI về metadata hình ảnh. Bạn muốn khám phá gì?",
    "Xin chào! Tôi là AWS First GenAI Journey, công cụ AI giúp bạn hiểu metadata hình ảnh. Tôi có thể giúp gì?",
    "Chào bạn! Tôi là AWS First GenAI Journey, công cụ AI giải thích metadata hình ảnh. Bạn cần gì?",
    "Chào! Tôi là AWS First GenAI Journey, trợ lý AI giúp hiểu dữ liệu First GenAI Journey dễ dàng. Tôi giúp được gì?",
    "Chào mừng! Tôi là AWS First GenAI Journey, công cụ AI thông minh giải thích dữ liệu First GenAI Journey. Tôi có thể hỗ trợ gì?",
    "Xin chào! Tôi là AWS First GenAI Journey, hướng dẫn viên AI về metadata hình ảnh. Hỏi tôi bất cứ điều gì!",
    "Chào! Tôi là AWS First GenAI Journey, trợ lý AI thông minh giúp hiểu metadata hình ảnh. Bạn muốn khám phá gì?",
    "Hey! Tôi là AWS First GenAI Journey, trợ lý AI giải thích dữ liệu AWS First GenAI Journey. Tôi có thể giúp gì hôm nay?",
]

message = random.choice(welcome_messages)

system_prompt = """
    You are an advanced AI financial advisor with extensive market knowledge and analytical capabilities. Your name is First GenAI Journey Advisor. The current date is July 2024. Your role is to assist traders and investors with stock analysis, market insights, and trading strategies. Please adhere to the following guidelines:
    1. Expertise: Demonstrate deep understanding of financial markets, trading strategies, technical analysis, and market structures.
    2. Analysis: Provide thorough, data-driven analysis of market trends, specific stocks, or trading strategies as requested.
    3. Explanations: Offer clear, comprehensive explanations suitable for traders of all experience levels. Break down complex concepts when necessary.
    4. Asset Evaluation: When asked, use your knowledge to identify potential trading assets. Provide a detailed list with supporting data and rationale for each recommendation.
    5. Current Information: Ensure all advice and analysis is based on the most up-to-date market information available to you. If you need to access real-time data, inform the user and proceed to retrieve the latest information.
    6. Honesty: If you're unsure about something or don't have the necessary information, clearly state this. Do not provide speculative or potentially misleading information.
    7. Language: Provide all responses in Vietnamese.
    8. Adaptability: Tailor your responses to the specific needs and questions of each user, whether they're seeking general market insights or detailed analysis of particular stocks or strategies.
    9. Markdown Format: Provide all responses in Markdown format, highlighting key points using bold text.
    """

def init_home_state(_message): 
  if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": message}]
  if "exif_df" not in st.session_state:
      st.session_state["exif_df"] = pd.DataFrame()
  if "url_exif_df" not in st.session_state:
      st.session_state["url_exif_df"] = pd.DataFrame()
  if "show_expanders" not in st.session_state:
      st.session_state.show_expanders = True
  if "reset_trigger" not in st.session_state:
      st.session_state.reset_trigger = False
  if "image_url" not in st.session_state:
      st.session_state["image_url"] = ""
  if "follow_up" not in st.session_state:
      st.session_state.follow_up = False
  if "show_animation" not in st.session_state:
      st.session_state.show_animation = True


def init_stock_advisor(): 
  if "messages" not in st.session_state:
      st.session_state["messages"] = [{"role": "assistant", "content": message}]
  if 'generated' not in st.session_state:
      st.session_state['generated'] = []
  if 'past' not in st.session_state:
      st.session_state['past'] = []
  if 'model_name' not in st.session_state:
      st.session_state['model_name'] = []
  if 'cost' not in st.session_state:
      st.session_state['cost'] = []
  if 'total_tokens' not in st.session_state:
      st.session_state['total_tokens'] = []
  if 'total_cost' not in st.session_state:
      st.session_state['total_cost'] = 0.0

def init_slidebar():
  with st.sidebar:
      image_url = (
          "https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/amazonwebservices/amazonwebservices-original-wordmark.svg"
      )

      st.markdown(
          f"""
          <div style='display: flex; align-items: center;'>
              <img src='{image_url}' style='height: 96px; padding: 10px; margin-right: 10px;'>
              <h1 style='margin: 0;'>AWS First GenAI Journey</h1>
          </div>
          """,
          unsafe_allow_html=True,
      )

      st.markdown(
          """
          <style>
              [data-testid="stSidebarNav"]::before {
                  content: "First GenAI Journey";
                  margin-left: 20px;
                  font-size: 20px;
                  position: relative;
              }
          </style>
          """,
          unsafe_allow_html=True,
      )
      
      st.sidebar.button(
          "🗑 Xóa lịch sử chat",
          on_click=clear_chat_history,
          key="sidebar_clear_chat_history",
      )

def init_animation():
  if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = False
  if st.session_state.reset_trigger:
      unique_key = "chat_input_" + str(hash("Snowflake Arctic is cool"))
      st.session_state.show_animation = False
      
  if "has_snowed" not in st.session_state:
      st.snow()
      st.session_state["has_snowed"] = True

  if 'show_animation' not in st.session_state:
    st.session_state.show_animation = False

  if st.session_state.show_animation:
      components.html(particles_js, height=370, scrolling=False)

def init_dialog():
  for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=icons[message["role"]]):
        st.write(message["content"])
        if message == st.session_state["messages"][0]:
            if st.button("Giới thiệu AWS First GenAI Journey?"):
                show_video("https://www.youtube.com/watch?v=AQlsd0nWdZk&list=PLahN4TLWtox2a3vElknwzU_urND8hLn1i")
                
                
def right_message(st, message):
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 10px;">
            <div style="text-align: right;">
                {message}
            </div>
            <img src="https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/user.gif" alt="avatar" style="height: 40px; border-radius: 50%; margin-left: 10px;">
        </div>
        """,
        unsafe_allow_html=True
    )

def clear_chat_history():
    st.session_state.reset_trigger = not st.session_state.reset_trigger
    st.session_state.show_expanders = True
    st.session_state.show_animation = True
    st.session_state.messages = [{"role": "assistant", "content": message}]
    st.session_state["exif_df"] = pd.DataFrame()
    st.session_state["url_exif_df"] = pd.DataFrame()
    st.cache_data.clear()
    st.success("Chat History Cleared!")

def clear_stock_advisor():
    st.session_state.show_animation = True
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state.messages = [{"role": "assistant", "content": message}]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    #counter_placeholder.write(f"Total cost of this conversation: $${st.session_state['total_cost']:.5f}")

@st.experimental_dialog("How to use First GenAI Journey", width=1920)
def show_video(video_url):
    st.video(video_url, loop=False, autoplay=True, muted=False)

@st.cache_resource(show_spinner=False)
def get_tokenizer():
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)


