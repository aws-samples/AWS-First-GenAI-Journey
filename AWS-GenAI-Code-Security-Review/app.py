import streamlit as st
import os
import re
from code_review.git_handler import analyze_repository, output_messages
from code_review.bedrock_analyze import analyze_file_contents
import chardet

def _sanitize_name(name):
    """Sanitize a name to prevent path traversal."""
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    sanitized = sanitized.replace('..', '').lstrip('.')
    return sanitized or 'unnamed'

def analyze_uploaded_file(uploaded_file):
    try:
        file_contents = uploaded_file.read()
        detected_encoding = chardet.detect(file_contents)['encoding']
        file_contents = file_contents.decode(detected_encoding or 'utf-8')

        st.write("File analysis complete. Here are the contents:")
        st.code(file_contents) 
        
        response = analyze_file_contents(file_contents)

        if response:
            for content in response['content']:
                st.markdown(content['text'])
        
    except UnicodeDecodeError as e:
        st.error(f"Error decoding the uploaded file: {e}")
    except Exception as e:
        st.error(f"An error occurred while analyzing the file: {e}")

def main():
    st.title('Demo Source Code Review')

    url = st.text_input('Enter the GitHub URL or Local path:')
    uploaded_file = st.file_uploader('Or upload a file:', type=['zip', 'py', 'js', 'html', 'css'])

    if st.button('Analyze'):
        if url:
            st.write('Analyzing...')
            if url.endswith('.git'):
                analyze_repository(url)
            else:
                st.warning('The URL should be end with .git')
            output_messages.clear() 

            st.write('Analysis complete.')

            report_path = f"report/{url.split('/')[-1].replace('.git', '')}" if 'http' in url else f"report/{os.path.basename(url)}"
            st.write(f"Report path: {report_path}") 
            
            if os.path.exists(report_path):
                reports = [f for f in os.listdir(report_path) if f.endswith('.md')]
                if reports:
                    for report in reports:
                        try:
                            with open(f"report/{url.split('/')[-1].replace('.git', '')}/{report}", 'r') as file:
                                report_content = file.read()
                                st.markdown(report_content) 
                        except Exception as e:
                            st.error(f"Error reading the report: {e}")
                else:
                    st.warning('No reports found in the selected directory.')
            else:
                st.warning(f"Report path does not exist: {report_path}")

        elif uploaded_file:
            st.write('Analyzing the uploaded file...')
            analyze_uploaded_file(uploaded_file)
        else:
            st.warning('Please enter a GitHub URL or upload a file.')

if __name__ == '__main__':
    main()
