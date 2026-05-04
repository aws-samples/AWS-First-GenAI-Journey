import streamlit as st
import os
import re
from code_review.git_handler import analyze_repository, output_messages
from code_review.bedrock_analyze import analyze_file_contents
import chardet

def _sanitize_name(name):
    """Sanitize a name to prevent path traversal."""
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    sanitized = sanitized.lstrip('.')
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

            report_path = os.path.join("report", _sanitize_name(url.split('/')[-1].replace('.git', ''))) if 'http' in url else os.path.join("report", _sanitize_name(os.path.basename(url)))
            st.write(f"Report path: {report_path}") 
            
            if os.path.exists(report_path):
                # Resolve the real path to prevent symlink-based traversal
                real_report_path = os.path.realpath(report_path)
                allowed_base = os.path.realpath("report")
                if not real_report_path.startswith(allowed_base):
                    st.error("Invalid report path detected.")
                else:
                    reports = [f for f in os.listdir(real_report_path) if f.endswith('.md')]
                    if reports:
                        for report in reports:
                            try:
                                report_file = os.path.join(real_report_path, report)
                                # Validate the final file path stays within the report directory
                                if not os.path.realpath(report_file).startswith(allowed_base):
                                    st.error(f"Invalid report file path: {report}")
                                    continue
                                with open(report_file, 'r') as file:
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
