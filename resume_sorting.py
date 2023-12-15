import cv2
import pytesseract
import mysql.connector
import os
import re
import streamlit as st
from datetime import date, timedelta
from PIL import Image
import fitz
import tempfile

# To define a dictionary with job categories and associated skills as keywords
job_category_keywords = {
    'Data Scientist': ['sql', 'python', 'machine learning', 'spark'],
    'Data Engineer': ['hadoop', 'spark', 'sql', 'python', 'aws'],
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
    'mobile app development': 5,
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
    today = date.today() + timedelta(days=2)  # To give interview date after 2 days from today
    while today.weekday() == 6:  # 6 corresponds to Sunday
        today += timedelta(days=1)  # If it is sunday, then it chooses the next day
    return today

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

# To view in streamlit 
background_color = "#B0E57C"
custom_style = f"""
    <style>
    .stApp {{
        background-color: {background_color};
    }}
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)
st.title("Resume Shortlisting")

uploaded_file = st.file_uploader("Upload a resume", type=["pdf", "jpg", "png"])

def extract_text_from_pdf(file):
    with st.spinner("Extracting text from PDF..."):
        pdf_document = fitz.open(file)
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text

def display_image(file):
    if file.type.startswith("image"):
        st.image(file, caption="Uploaded Image", use_column_width=True)
    elif file.type == "application/pdf":
        st.warning("PDF file detected")
    else:
        st.error("Unsupported file type. Please upload a PDF or an image (jpg/png).")
        st.stop()

if uploaded_file is not None:
    # Save the uploaded file locally
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
        temp_file.write(uploaded_file.read())

    # Display the uploaded image or PDF
    display_image(uploaded_file)

    # Extract text from the uploaded file
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(temp_path)
    elif uploaded_file.type.startswith("image"):
        text = extract_text(uploaded_file)
    else:
        st.stop()
        
    # To extract name from the PDF file path
    name = os.path.splitext(os.path.basename(uploaded_file.name))[0]
    
    # To extract email using regular expression
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    email_match = re.search(email_pattern, text)
    email = email_match.group() if email_match else "N/A"

    # To calculate the resume score
    resume_score = calculate_resume_score(text)

    # To categorize the resume
    job_category = categorize_resume(text)

    # To assign the interview date
    interview_date = assign_interview_date()

    # Check if the resume score is 3 or above
    if resume_score >= 3:
        extracted_info = {
            "Name": name,
            "Email": email,
            "Job Role": job_category,
            "Resume Score": f"{resume_score:.2f} out of 5",
            "Interview Date": interview_date.strftime("%d-%m-%Y")
        }
        st.write("<p style='color:red;'>Candidate shortlisted</p>", unsafe_allow_html=True)
        st.subheader("Candidate Details:")
        for key, value in extracted_info.items():
            st.write(f"{key}: {value}")
            
        # To insert the resume information into the database
        query = "insert into shortlisted_resumes(interview_date, name, email, job_category) VALUES (%s, %s, %s, %s)"
        data = (interview_date, name, email, job_category)
        cursor.execute(query, data)
        
        # Commit changes
        conn.commit()
    else:
        st.write("<p style='color:red;'>Candidate not shortlisted. Resume score is below 3.</p>", unsafe_allow_html=True)

    # Remove the temporary file
    os.unlink(temp_path)

# Close the database connection
cursor.close()
conn.close()