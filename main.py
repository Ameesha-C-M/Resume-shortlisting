import cv2
import pytesseract
import mysql.connector
import os
import fitz
from datetime import date, timedelta
import re

# Define a dictionary of job categories and associated keywords
job_categories_keywords = {
    'Data_scientist': ['spark', 'mysql', 'data science', 'machine learning', 'natural language processing', 'deep learning'],
    'Data_engineer': ['hadoop', 'spark', 'mysql', 'machine learning', 'aws'],
    'Data_analyst': ['powerbi', 'tableau', 'data analytics', 'machine learning', 'python', 'SQL'],
    'Front-End Developer': ['front-end developer', 'HTML', 'CSS', 'Bootstrap', 'Javascript', 'Angular', 'React', 'Material UI', 'Mongodb', 'Node js'],
    'Flutter Developer': ['Flutter', 'Dart', 'Mobile App Development', 'Cross-Platform Development', 'UI/UX Design', 'Widget']
}

# Function to categorize resumes
def categorize_resume(resume_text):
    for category, keywords in job_categories_keywords.items():
        if any(keyword in resume_text.lower() for keyword in keywords):
            return category
    return 'Uncategorized'

# Function to assign interview dates
def assign_interview_date():
    today = date.today()
    interview_date = today + timedelta(days=7)
    return interview_date

# Function to extract text from images using OpenCV and pytesseract
def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img)
    return text

# Connect to the database
conn = mysql.connector.connect(
    host="localhost",
    database="resume_sorting",
    user="root",
    password="Luminar@1234")
cursor = conn.cursor()

resumes_folder = r"C:\Users\user\Desktop\dl project\resume_analyser"

for resume_file in os.listdir(resumes_folder):
    if resume_file.endswith(".pdf") or resume_file.endswith(".jpg") or resume_file.endswith(".png"):
        resume_path = os.path.join(resumes_folder, resume_file)

        if resume_file.endswith((".jpg", ".png")):
            # Extract text from image-based resumes
            image_text = extract_text_from_image(resume_path)
            text = image_text
        else:
            # Extract text from the PDF using PyMuPDF
            pdf_document = fitz.open(resume_path)
            text = ""
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()

        # Categorize the resume
        job_category = categorize_resume(text)

        if job_category != 'Uncategorized':  # Skip uncategorized resumes
            # Extract name from the PDF file path
            name = os.path.splitext(os.path.basename(resume_file))[0]

            # Extract email using regular expression
            email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
            email_match = re.search(email_pattern, text)
            email = email_match.group() if email_match else "N/A"

            # Assign an interview date
            interview_date = assign_interview_date()

            # Insert the resume information into the database
            query = "INSERT INTO shortlisted_resumes(interview_date, name, email, job_category) VALUES (%s, %s, %s, %s)"
            data = (interview_date, name, email, job_category)
            cursor.execute(query, data)

            # Print the extracted information
            print(f"Job Role: {job_category}")
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Interview Date: {interview_date}")
            print("-" * 50)

# Commit changes and close the database connection
conn.commit()
cursor.close()
conn.close()