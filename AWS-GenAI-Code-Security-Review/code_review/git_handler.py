import git
import re
import os
import sys
import datetime
import chardet
import fnmatch
import shutil
import zipfile
from . import bedrock_analyze

# Define the cost per token and per second
COST_IN_TOKEN = 0.00025
COST_OUT_TOKEN = 0.00125

# Define the blacklist of file names
BLACKLIST = [
    "*.md", "changelog.txt", "*.txt", "*.ico", "README", "LICENSE",
    "*.csproj", "*.sln", ".git*", ".DS_Store", ".idea", ".vscode",
    "node_modules", "bower_components", "package-lock.json", "yarn.lock",
    "*file.js", "*config.js", "composer.*", "Gemfile*", "Procfile",
    ".travis.yml", ".gitlab-ci.yml", ".circleci", ".github", ".editorconfig",
    ".htaccess", ".htpasswd", "nginx.conf", "docker-compose.yml", "Jenkinsfile",
    "Makefile", ".mailmap"
]

output_messages = []

def _sanitize_name(name):
    """Sanitize a name to prevent path traversal. Only allow alphanumeric, hyphens, underscores, and dots."""
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    # Remove path traversal sequences and leading dots
    sanitized = sanitized.replace('..', '')
    sanitized = sanitized.lstrip('.')
    if not sanitized:
        sanitized = 'unnamed'
    return sanitized

def clear_report_directory():
    """Clear the 'report' directory before running analysis."""
    report_path = f"{os.getcwd()}/report"
    if os.path.exists(report_path):
        shutil.rmtree(report_path) 
    os.makedirs(report_path) 

def analyze_repository(repo_url):
    clear_report_directory() 
    
    repo_name = _sanitize_name(repo_url.split("/")[-1].replace(".git", ""))
    local_repo_path = os.path.join("source", repo_name)

    if os.path.isdir(local_repo_path):
        repo = git.Repo(local_repo_path)
        origin = repo.remote(name='origin')
        origin.pull()
        output_messages.append(f"Repository successfully updated: {repo_url} --> {local_repo_path}")
    else:
        try:
            git.Repo.clone_from(repo_url, local_repo_path)
            output_messages.append(f"Cloning is successful: {repo_url} --> {local_repo_path}")
        except git.exc.GitCommandError as e:
            output_messages.append(f"An error occurred while cloning the repository: {e}")
            sys.exit(1)

    analyze_files(local_repo_path)
    shutil.rmtree(local_repo_path)  

def analyze_local_path(local_path):
    clear_report_directory()
    
    if local_path.endswith('.zip'):
        repo_name = os.path.basename(local_path).replace('.zip', '')
        extract_path = os.path.join(os.getcwd(), repo_name)
        with zipfile.ZipFile(local_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        analyze_files(extract_path)
        shutil.rmtree(extract_path)  
    elif os.path.isdir(local_path):
        analyze_files(local_path)
    else:
        output_messages.append(f"Invalid path: {local_path}")
        sys.exit(1)

max_analyzing_files = int(os.getenv("QUOTAS_FILE_ANALLYZING"))
def analyze_files(path):
    repo_name = os.path.basename(path)
    report_dir = f'report/{repo_name}'

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    blacklist = [item.lower() for item in BLACKLIST]
    files_processed = 0 

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            print(file_path)

            if any(fnmatch.fnmatch(file.lower(), pattern) for pattern in blacklist):
                output_messages.append(f"Excluding file: {file}")
                continue

            if not file.endswith(('.py', '.js')):
                continue

            with open(file_path, 'rb') as f:
                file_contents = f.read()

            detected_encoding = chardet.detect(file_contents)['encoding']
            
            try:
                file_contents = file_contents.decode(detected_encoding or 'utf-8')

                analysis = bedrock_analyze.analyze_file_contents(file_contents)

                if analysis is None:
                    continue
                    
                now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S").replace(':', '-')
                report_file_path = f'report/{repo_name}/{now}.md'

                with open(report_file_path, 'a') as reporting:
                    sys.stdout = reporting
                    
                    input_tokens = int(analysis['usage']['input_tokens'])
                    output_tokens = int(analysis['usage']['output_tokens'])
                    total_cost = input_tokens * COST_IN_TOKEN + output_tokens * COST_OUT_TOKEN
                    
                    print(f"---\n### Report for: {file}")
                    print(f"###### Total tokens used: {input_tokens + output_tokens}")
                    print(f"###### Total cost is: ${total_cost:.2f}")
                    for content in analysis["content"]:
                        print(f'{content["text"]}\n')

                    sys.stdout = sys.__stdout__

                files_processed += 1
                if files_processed >= max_analyzing_files:
                    return  

            except UnicodeDecodeError as e:
                output_messages.append(f"Error decoding file {file_path}: {e}. Skipping file.")
            except Exception as e:
                output_messages.append(f"An error occurred with file {file_path}: {e}")
