import cv2
import pytesseract
import mysql.connector
import os
import fitz
from datetime import date, timedelta
import re

# To define a dictionary with job categories and assosiated skills as keywords
job_category_keywords = {
    'Data Scientist': ['sql', 'python', 'machine learning','spark'],
    'Data Engineer': ['hadoop', 'spark', 'sql','python', 'aws'],
    'Data Analyst': ['powerbi', 'tableau', 'python', 'sql', 'excel'],
    'Front-End Developer': ['front end developer', 'html', 'css', 'bootstrap', 'javascript', 'angular', 'react', 'material ui', 'mongodb', 'node js'],
    'Flutter Developer': ['flutter', 'dart', 'mobile app development', 'cross platform development', 'ui ux design', 'widget']
}

# To define a dictionary for assigning scores for the skills
keyword_scores = {
    'spark': 5,
    'machine learning': 5,
    'hadoop': 4,
    'aws': 4,
    'sql': 5,
    'excel': 5,
    'powerbi': 5,
    'tableau': 5,
    'python': 5,
    'front end developer': 5,
    'html': 3,
    'css': 3,
    'bootstrap': 3,
    'javascript': 4,
    'angular': 5,
    'react': 5,
    'material ui': 3,
    'mongodb': 4,
    'node js': 5,
    'flutter': 5,
    'dart': 5,
    'mobile app development': 4,
    'cross platform development': 4,
    'ui ux design': 4,
    'widget': 4
}

# To create a function to calculate the resume score
def calculate_resume_score(resume_text):
    score = 0
    for keyword in keyword_scores:
        if keyword in resume_text.lower():
            score += keyword_scores[keyword]
    return min(score / 25.0, 1.0) * 5  

# To create a function to assign interview dates
def assign_interview_date():
    today = date.today()
    interview_date = today + timedelta(days=7)
    return interview_date

# To create a function to extract text from images using OpenCV and pytesseract
def extract_text(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    return text

# To create a function for categorizing the resumes
def categorize_resume(resume_text):
    max_score = 0
    category = 'Uncategorized'
    for category_name, keywords in job_category_keywords.items():
        score = sum(keyword_scores[keyword] for keyword in keywords if keyword in resume_text.lower())
        if score > max_score:
            max_score = score
            category = category_name
    return category

# To connect to the mysql database
conn = mysql.connector.connect(
    host="localhost",
    database="resume_sorting",
    user="root",
    password="Luminar@1234")
cursor = conn.cursor()

resumes_folder = r"C:\Users\user\Desktop\dl project\resume_analyser\resume"

for resume_file in os.listdir(resumes_folder):
    if resume_file.endswith(".pdf") or resume_file.endswith(".jpg") or resume_file.endswith(".png"):
        resume_path = os.path.join(resumes_folder, resume_file)

        if resume_file.endswith((".jpg", ".png")):
            # To extract text from image-based resumes
            image_text = extract_text(resume_path)
            text = image_text
        else:
            # To extract text from the PDF using PyMuPDF
            pdf_document = fitz.open(resume_path)
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()

        # To calculate the resume score
        resume_score = calculate_resume_score(text)

        # To categorize the resume
        job_category = categorize_resume(text)

        if job_category != 'Uncategorized' and resume_score >= 3.0: 
            # To extract name from the PDF file path
            name = os.path.splitext(os.path.basename(resume_file))[0]

            # To extract email using regular expression
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
            email_match = re.search(email_pattern, text)
            email = email_match.group() if email_match else "N/A"

            # To assign the interview date
            interview_date = assign_interview_date()

            # To insert the resume information into the database
            query = "insert into shortlisted_resumes(interview_date, name, email, job_category) VALUES (%s, %s, %s, %s)"
            data = (interview_date, name, email, job_category)
            cursor.execute(query, data)

            # To print the extracted information and score
            print(f"Job Role: {job_category}")
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Resume Score: {resume_score:.2f} out of 5")
            print(f"Interview Date: {interview_date}")
            print("-" * 50)

# Commit changes and close the database connection
conn.commit()
cursor.close()
conn.close()


