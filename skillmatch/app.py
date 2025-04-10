from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import spacy
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from spacy.matcher import PhraseMatcher
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Categorized skill list
skill_categories = {
    'Programming': ['python', 'java', 'sql', 'html', 'css', 'javascript'],
    'Cloud': ['aws', 'azure', 'gcp'],
    'DevOps': ['docker', 'kubernetes', 'jenkins'],
    'Frameworks': ['flask', 'django', 'react', 'node.js'],
    'Databases': ['mysql', 'mongodb'],
    'Tools': ['git', 'jira', 'linux'],
    'Data Science': ['machine learning', 'deep learning', 'data analysis'],
    'Soft Skills': ['communication', 'teamwork', 'leadership']
}

def extract_skills_from_text(text):
    found_skills = []
    for category, skills in skill_categories.items():
        for skill in skills:
            if skill in text and skill not in found_skills:
                found_skills.append(skill)
    return sorted(found_skills)

# Scrape required skills from job description

def fetch_skills_from_web(job_title):
    job_title_query = job_title.replace(' ', '+')
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        url = f"https://jobicy.com/jobs/?q={job_title_query}"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find job description snippets
        descriptions = soup.find_all('div', class_='job-list-item__desc')
        all_text = " ".join([desc.get_text(strip=True) for desc in descriptions]).lower()

        print(f"[DEBUG] Scraped {len(descriptions)} job postings from Jobicy")

        if all_text.strip():
            return extract_skills_from_text(all_text)
    except Exception as e:
        print(f"[ERROR] Jobicy scrape failed: {e}")

    return []



# Example job roles (default if scraping fails or not used)
default_job_roles = {
    'Data Scientist': ['python', 'machine learning', 'data analysis', 'sql', 'deep learning', 'communication'],
    'Cloud Engineer': ['aws', 'azure', 'linux', 'git', 'docker', 'communication'],
    'DevOps Engineer': ['docker', 'kubernetes', 'jenkins', 'linux', 'git', 'python'],
    'Full Stack Developer': ['html', 'css', 'javascript', 'react', 'node.js', 'mysql', 'git'],
    'Backend Developer': ['python', 'flask', 'django', 'mysql', 'mongodb', 'linux']
}

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        return extract_pdf_text(file_path)
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

def extract_skills_by_category(text):
    text = text.lower()
    doc = nlp(text)

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    categorized_skills = {}

    for category, keywords in skill_categories.items():
        patterns = [nlp.make_doc(skill) for skill in keywords]
        matcher.add(category, patterns)

    matches = matcher(doc)
    found = {}

    for match_id, start, end in matches:
        category = nlp.vocab.strings[match_id]
        skill = doc[start:end].text.lower()
        if category not in found:
            found[category] = set()
        found[category].add(skill)

    categorized_skills = {cat: sorted(list(skills)) for cat, skills in found.items()}
    return categorized_skills

def analyze_skill_gap(extracted_skills, target_role):
    required_skills = set(fetch_skills_from_web(target_role) or default_job_roles.get(target_role.title(), []))

    extracted_flat_skills = set()
    for skills in extracted_skills.values():
        extracted_flat_skills.update(skills)

    print(f"[DEBUG] Target role: {target_role}")
    print(f"[DEBUG] Fetched required skills: {required_skills}")
    print(f"[DEBUG] Extracted user skills: {extracted_flat_skills}")

    matched = sorted(list(required_skills.intersection(extracted_flat_skills)))
    missing = sorted(list(required_skills.difference(extracted_flat_skills)))

    return {
        'target_role': target_role,
        'matched_skills': matched,
        'missing_skills': missing
    }


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/extract', methods=['POST'])
def extract_resume_skills():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400

    file = request.files['resume']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    text = extract_text(file_path)
    categorized_skills = extract_skills_by_category(text)

    return jsonify({'categorized_skills': categorized_skills})

@app.route('/analyze', methods=['POST'])
def analyze_skills():
    data = request.get_json()
    extracted_skills = data.get('skills', {})
    target_role = data.get('role', '')

    if not extracted_skills or not target_role:
        return jsonify({'error': 'Missing skills or role data'}), 400

    result = analyze_skill_gap(extracted_skills, target_role)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
