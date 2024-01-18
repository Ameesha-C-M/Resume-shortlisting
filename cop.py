import cv2
import numpy as np
import mysql.connector
import os
import pytesseract
import re
from pdf2image import convert_from_path

# Function to load the resume image
def load_image(image_path):
    return cv2.imread(image_path)

# Function to perform OCR on the image
def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

# Function to calculate the score based on keyword matching
def calculate_score(text, keywords):
    text_lower = text.lower()
    score = sum(keyword.lower() in text_lower for keyword in keywords)
    return score

# Function to extract email from the OCR text using regular expression
def extract_email(text):
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text.lower())
    return email_match.group() if email_match else None

if __name__ == "__main__":
    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",
        database="resume_sorting",
        user="root",
        password="Luminar@1234")
    cursor = conn.cursor()

    # Fetch data from the database
    cursor.execute("SELECT * FROM url_project")

    # Consume any unread results from the SELECT query
    cursor.fetchall()

    resumes_folder = os.path.join(os.path.expanduser("/home/abhay/Documents/DL Projects/ResumeAnalyzing_OCR_PROJECT"), "resume")

    keywords = ["python", "mysql", "machine learning", "data analysis",
                'natural language processing', 'tableau', 'powerbi',
                'data science', "deep learning", 'hadoop', 'spark', 'pyspark', 'aws',
                'Html', 'Css','Bootstrap','Javascript','Angular','React','Material UI','Mongodb',
                'Node js','Typescript','Flutter','Dart','Mobile App Development',
                'Cross-Platform Development','UI/UX Design','Widget']  # Adding relevant keywords 
    threshold_score = 4  # minimum required score for selecting the resume

    job_roles_keywords = {
        'data_scientist': ['hadoop', 'spark', 'mysql', 'data science', 'machine learning',
                           'natural language processing', 'aws', 'deep learning'],
        'data_engineer': ['hadoop', 'spark', 'mysql', 'data science', 'machine learning',
                          'natural language processing', 'aws'],
        'data_analyst': ['powerbi', 'tableau', 'data analytics', 'machine learning','python','SQL'],
        'Front-End Developer': ['Html', 'Css', 'Bootstrap', 'Javascript', 'Angular', 'React', 'Material UI', 'Mongodb',
                                'Node js', 'Typescript'],
        'Flutter Developer': ['Flutter', 'Dart', 'Mobile App Development',
                              'Cross-Platform Development', 'UI/UX Design', 'Widget']
    }

    date1 = ('2023-09-11', '2023-09-15', '2023-09-20', '2023-09-23', '2023-09-30')
    all_shortlisted_resumes = []

     # Dictionary mapping each keyword to its corresponding job category
    keyword_to_job_category = {
        'hadoop': 'Data Engineer',
        'spark': 'Data Engineer',
        'mysql': 'Data Engineer',
        'data science': 'Data Engineer',
        'machine learning': 'Data Engineer',
        'natural language processing': 'Data Engineer',
        'aws': 'Data Engineer',
        'deep learning': 'Data Scientist',
        'powerbi': 'Data Analyst',
        'tableau': 'Data Analyst',
        'data analytics': 'Data Analyst',
        'python': 'Data Analyst',
        'SQL': 'Data Analyst',
        'Html': 'Front-End Developer',
        'Css': 'Front-End Developer',
        'Bootstrap': 'Front-End Developer',
        'Javascript': 'Front-End Developer',
        'Angular': 'Front-End Developer',
        'React': 'Front-End Developer',
        'Material UI': 'Front-End Developer',
        'Mongodb': 'Front-End Developer',
        'Node js': 'Front-End Developer',
        'Typescript': 'Front-End Developer',
        'Flutter': 'Flutter Developer',
        'Dart': 'Flutter Developer',
        'Mobile App Development': 'Flutter Developer',
        'Cross-Platform Development': 'Flutter Developer',
        'UI/UX Design': 'Flutter Developer',
        'Widget': 'Flutter Developer',
        'Machine Learning' :'Data Scientist',
        'python' : "Data Scientist",
        'DataScience' :'Data Scientist',
        'openCV' : 'Data Scientist'
    }


    for role, keywords in job_roles_keywords.items():
        print(f"Job Role: {role}")

        # Create a list to store shortlisted resumes for each job role
        shortlisted_resumes = []

        for resume_file in os.listdir(resumes_folder):
            resume_path = os.path.join(resumes_folder, resume_file)

            # Convert PDF to images using pdf2image
            images = convert_from_path(resume_path)

            for idx, image in enumerate(images):
                # Save the image temporarily to process with pytesseract
                temp_image_path = f"temp_image_{idx}.png"
                image.save(temp_image_path)

                # Process the image with pytesseract
                image_cv2 = load_image(temp_image_path)
                extracted_text = extract_text_from_image(image_cv2)
                score = calculate_score(extracted_text, keywords)

                if score >= threshold_score:
                    # Job role classification logic
                    matched_keywords = [keyword for keyword in keywords if keyword.lower() in extracted_text.lower()]
                    job_category = 'nill'

                    for keyword in matched_keywords:
                        if keyword.lower() in keyword_to_job_category:
                            job_category = keyword_to_job_category[keyword.lower()]
                            break  # Stop at the first matched keyword's job category

                    resume_name = resume_file  # Extract only the name
                    email = extract_email(extracted_text)  # Extract email 

                    shortlisted_resumes.append((date1, resume_name, email, job_category))

                # Remove the temporary image file
                os.remove(temp_image_path)


            
        if shortlisted_resumes:
            print("Shortlisted Resumes:")
            for date_value in date1:
                for date_interview, resume_name, email, job_category in shortlisted_resumes:
                    #if date_value == date_interview:
                    print(f"Interview Date: {date_value}")
                    print(f"Name: {resume_name}")
                    print(f"Email: {email}")
                    print(f"Job Category: {job_category}")
                    print()

                    query = "SELECT * FROM Modified_resumes WHERE name = %s AND Interview_date = %s"
                    data = (resume_name, date_value)
                    cursor.execute(query, data)
                    result = cursor.fetchone()

                    if not result:
                        query = "INSERT INTO Modified_resumes (Interview_date, name, email, job_category) VALUES (%s, %s, %s, %s)"
                        insert_data = (date_value, resume_name, email, job_category)
                        cursor.execute(query, insert_data)

                all_shortlisted_resumes.append({"Job Category": role, "Resumes": shortlisted_resumes})

                print()
        else:
            print("No matched keywords found.")
        shortlisted_resumes.clear()

    conn.commit()
    cursor.close()
    conn.close()
