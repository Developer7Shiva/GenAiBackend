import shutil
from fastapi import FastAPI, File, UploadFile, Form
from typing_extensions import Annotated
from mangum import Mangum
import google.generativeai as genai
import os
import docx2txt
import PyPDF2 as pdf
from dotenv import load_dotenv

app = FastAPI()
handler = Mangum(app)

# Load environment variables from a .env file
load_dotenv()

# Configure the generative AI model with the Google API key
# genai.configure(api_key=os.getenv())
genai.configure(api_key="AIzaSyBSRXYNsoPobSx1hFm_QWAcDF4EJKKeISo")
credential_path = r"venv/assets/recruitrador-genai-1fe5100c2786.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

#Extracting Data from PDF
def extract_text_from_pdf_file(pdf_file):
    # Use PdfReader to read the text content from a PDF file
    pdf_reader = pdf.PdfReader(pdf_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += str(page.extract_text())
    return text_content

#Extracting Data from docx
def extract_text_from_docx_file(docx_file):
    return docx2txt.process(docx_file)

# Set up the model configuration for text generation
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}
# Define safety settings for content generation
safety_settings = [
    {"category": f"HARM_CATEGORY_{category}", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    for category in [
        "HARASSMENT",
        "HATE_SPEECH",
        "SEXUALLY_EXPLICIT",
        "DANGEROUS_CONTENT",
    ]
]

#API Connecting Place
# Create a GenerativeModel instance with 'gemini-pro' as the model type
def generate_response_from_gemini(input_text, job_description):
    llm = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        safety_settings=safety_settings,
    )
    # Generate content based on the input text
    output = llm.generate_content(input_text.format(job_description=job_description))

    # Return the generated text
    return output.text
# Prompt Template
input_prompt_template = """As an experienced Applicant Tracking System (ATS) analyst,
with profound knowledge in technology, software engineering, data science, full stack web development, cloud enginner, 
cloud developers, devops engineer and big data engineering, your role involves evaluating resumes against job descriptions.
Recognizing the competitive job market, provide top-notch assistance for resume improvement.
Your goal is to analyze the resume against the given job description, 
assign a percentage match based on key criteria, and pinpoint missing keywords accurately.
resume:{text}
description:{job_description}
I want the response in one single string having the structure Profile Match Score: as a percentage format
"""

def GenApiCalling():
    resume_path = (r"venv/assets/Shiva_Resume.pdf")
    job_description = """"Proficiency in Java, with a good understanding of its ecosystems
Sound knowledge of Object-Oriented Programming (OOP) Patterns and Concepts
Familiarity with different design and architectural patterns
Skill for writing reusable Java libraries 
Know how of Java concurrency patterns
Basic Understanding of the concepts of MVC (Model-View-Controller) Pattern, JDBC (Java Database Connectivity), and RESTful web services
Experience in working with popular web application frameworks like Play and Spark
Relevant Knowledge of Java GUI frameworks like Swing, SWT, AWT according to project requirements
Ability to write clean, readable Java code
Basic knowhow of class loading mechanism in Java
Experience in handling external and embedded databases
Understanding basic design principles behind a scalable application
Skilled at creating database schemas that characterize and support business processes
Basic knowledge of JVM (Java Virtual Machine), its drawbacks, weaknesses, and workarounds
Implementing automated testing platforms and unit tests 
In-depth knowledge of code versioning tools, for instance, Git
Understanding of building tools like Ant, Maven, Gradle, etc
Expertise in continuous integration
Other required skills of java developer include the basic knowledge of:
JavaServer pages (JSP) and servlets
Web frameworks like Struts and Spring
Service-oriented architecture 
Web Technologies like HTML, JavaScript, CSS, JQuery
Markup Languages such as XML, JSON
Abstract classes and interfaces
Constructors, lists, maps, sets
File IO and serialization
Exceptions
Generics
Java Keywords like static, volatile, synchronized, transient, etc
Multithreading and Synchronization
"""

    if os.path.exists(resume_path):
        if resume_path.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf_file(resume_path)
        elif resume_path.lower().endswith(".docx"):
            resume_text = extract_text_from_docx_file(resume_path)
        else:
            print("Unsupported file format. Please provide a PDF or DOCX file.")
            return

        response_text = generate_response_from_gemini(
            input_prompt_template.format(text=resume_text, job_description=job_description), job_description=job_description
        )
        # print(response_text)
    return response_text

#Uploading File with Checking the dir exists or not
def save_file_to_assets(directory: str, file: UploadFile) -> str:
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Save the file to the directory
    with open(os.path.join(directory, file.filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file.filename

#Root URL Greeting Message
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def endpoint_0():
    try:
        return {"Message": "Hi, I'm HR Genie"}
    except Exception as e:
        print("Invalid Request")
        return {"error": str(e)}


#Getting Data from HRGenie
@app.post("/profile")
async def endpoint_3(name: Annotated[str, Form()],
                     experience: Annotated[str, Form()],
                     job_title: Annotated[str, Form()],
                     skills: Annotated[str, Form()],
                     job_description: Annotated[str, Form()],
                     file: Annotated[UploadFile, File(description="A file read as UploadFile")]):
    try:
        saved_filename = save_file_to_assets("UploadedFiles", file)
        result = GenApiCalling()
        return {
            "Username": name,
            "title": job_title,
            "experience": experience,
            "Skills": skills,
            "Job Desc": job_description,
            "File Name": saved_filename,
            "Profile Match": result
        }
    except Exception as e:
        print("Exception is:", e)
        return {"error": str(e)}


#Getting Profile matched percentage only
@app.get("/score")
async def endpoint_1():
    try:
        Api_Response = GenApiCalling()
        output = {"Output": Api_Response}
        return output
    except Exception as e:
        print("Exception occurred:", e)
        return {"error": str(e)}

