import streamlit as st
import pandas as pd
from fpdf import FPDF
from transformers import pipeline
import datetime

# Initialize Hugging Face text generation model
generator = pipeline("text-generation", model="gpt2")

# Dictionary of predefined skills based on profession
profession_skills = {
    "Software Developer": ["Python", "JavaScript", "SQL", "Git"],
    "Data Scientist": ["Python", "Machine Learning", "Data Analysis", "SQL"],
    "Product Manager": ["Project Management", "Market Research", "Agile", "Communication"]
}

# Skill proficiency suggestions
proficiency_suggestions = {
    "Software Developer": {"Python": "Advanced", "JavaScript": "Intermediate", "SQL": "Intermediate"},
    "Data Scientist": {"Python": "Advanced", "Data Analysis": "Advanced", "SQL": "Intermediate"},
}

def generate_description(position, company):
    prompt = f"Write a concise and professional job description for a {position} role at {company}. Include 3-4 key responsibilities, 3-4 required skills, and any specific experience necessary for this role."
    response = generator(prompt, max_length=150, num_return_sequences=1)
    return response[0]['generated_text'].strip()


def generate_pdf(resume_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Set up the title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Resume", ln=True, align="C")
    pdf.ln(10)

    # Personal Information
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Personal Information", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Name: {resume_data['Personal Information']['Name']}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {resume_data['Personal Information']['Email']}", ln=True)
    pdf.cell(200, 10, txt=f"Phone: {resume_data['Personal Information']['Phone']}", ln=True)
    pdf.ln(5)

    # Profession
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Profession", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"{resume_data['Profession']}", ln=True)
    pdf.ln(5)

    # Skills Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Skills and Proficiency", ln=True)
    pdf.set_font("Arial", "", 12)
    for skill, level in resume_data['Skills'].items():
        pdf.cell(200, 10, txt=f"{skill}: {level}", ln=True)
    pdf.ln(5)

    # Education Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Education", ln=True)
    pdf.set_font("Arial", "", 12)
    education = resume_data['Education']
    pdf.cell(200, 10, txt=f"{education['Level']} from {education['Institution']} - Graduated in {education['Graduation Year']}", ln=True)
    pdf.ln(5)

    # Work Experience Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Work Experience", ln=True)
    pdf.set_font("Arial", "", 12)
    for exp in resume_data['Work Experience']:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, txt=f"{exp['position']} at {exp['company']}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, txt=f"{exp['start_date'].strftime('%Y-%m-%d')} to {exp['end_date'].strftime('%Y-%m-%d')}", ln=True)
        pdf.multi_cell(0, 10, txt=exp['description'])
        pdf.ln(5)

    # Footer with a line
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "Generated using AI Resume Builder", 0, 0, "C")

    # Save PDF to a buffer
    pdf_output = "generated_resume.pdf"
    pdf.output(pdf_output)
    return pdf_output


def run():
    st.title("AI Resume Builder")

    # Personal Information
    st.header("Personal Information")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")

    # Profession
    st.header("Profession")
    profession = st.selectbox("Select your profession", list(profession_skills.keys()) + ["Other"])
    if profession == "Other":
        profession = st.text_input("Specify your profession")

    # Skills and Proficiency
    st.header("Skills")
    skills = profession_skills.get(profession, [""])
    selected_skills = st.multiselect("Select or add your skills", skills, default=skills)

    st.subheader("Skill Proficiency")
    skill_proficiency = {}
    for skill in selected_skills:
        default_level = proficiency_suggestions.get(profession, {}).get(skill, "Beginner")
        skill_proficiency[skill] = st.select_slider(f"Proficiency in {skill}", options=['Beginner', 'Intermediate', 'Advanced', 'Expert'], value=default_level)

    # Education
    st.header("Education")
    education_level = st.selectbox("Highest Education Level", ["High School", "Bachelor's", "Master's", "PhD"])
    institution = st.text_input("Institution Name")
    graduation_year = st.number_input("Graduation Year", min_value=1950, max_value=2030, value=2020)

    # Work Experience
    st.header("Work Experience")
    num_experiences = st.number_input("Number of work experiences", min_value=0, max_value=10, value=1)
    experiences = []
    for i in range(int(num_experiences)):
        st.subheader(f"Experience {i+1}")
        company = st.text_input(f"Company Name", key=f"company_{i}")
        position = st.text_input(f"Position", key=f"position_{i}")
        start_date = st.date_input(f"Start Date", key=f"start_date_{i}")
        end_date = st.date_input(f"End Date", key=f"end_date_{i}")
        description = generate_description(position, company)
        st.text_area(f"Description", key=f"description_{i}", value=description, height=100)

        experiences.append({
            "company": company,
            "position": position,
            "start_date": start_date,
            "end_date": end_date,
            "description": description
        })

    # Button to generate resume and PDF download
    if st.button("Generate Resume"):
        resume = {
            "Personal Information": {
                "Name": name,
                "Email": email,
                "Phone": phone
            },
            "Profession": profession,
            "Skills": skill_proficiency,
            "Education": {
                "Level": education_level,
                "Institution": institution,
                "Graduation Year": graduation_year
            },
            "Work Experience": experiences
        }
        st.json(resume)

        # Generate and download PDF
        pdf_path = generate_pdf(resume)
        with open(pdf_path, "rb") as file:
            st.download_button("Download Resume as PDF", file, file_name="resume.pdf")

if __name__ == "__main__":
    run()
