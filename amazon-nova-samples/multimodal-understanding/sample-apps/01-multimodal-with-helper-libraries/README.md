# Multi-modal Understanding

This folder contains a sample Streamlit application and Jupyter notebook demonstrating some of the multi-modal understanding capabilities of the Amazon models.

It provides some helper functions for video formatting under the `utils.py` file.

To get started, you can create a Python virtual environment such as with:

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

To run the Streamlit application after installing everything in `requirements.txt`, run:
```
streamlit run mm_understanding.py
```

The helper libraries will create files under a `./tmp` directory for the purpose of video formatting with either ffmpeg or OpenCV.