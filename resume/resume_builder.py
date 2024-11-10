import streamlit as st
import pandas as pd
from fpdf import FPDF
from transformers import pipeline
import datetime
import random

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

def generate_description(profession, skills, skill_proficiency, education, work_experiences):
    templates = [
        "As a {profession} with a background in {education}, I have developed expertise in {skills_list}. With a strong proficiency in {key_skill} ({key_skill_level}), I have successfully contributed to projects at {latest_company}, where I {latest_experience}.",
        "With a solid foundation in {education} and hands-on experience in {skills_list}, I am a dedicated {profession}. My {key_skill} skills at {key_skill_level} level have proven valuable at {latest_company}, where I recently {latest_experience}.",
        "I am an experienced {profession} skilled in {skills_list}. Leveraging my {key_skill} skills ({key_skill_level}), I’ve made meaningful contributions at {latest_company} by {latest_experience}. My educational background in {education} supports my technical proficiency and problem-solving skills.",
        "In my role as a {profession}, I bring a wealth of knowledge in {skills_list} and am particularly proficient in {key_skill} ({key_skill_level}). My educational journey in {education} has equipped me to excel in demanding projects, such as those at {latest_company}, where I {latest_experience}."
    ]
    
    # Choose a random template
    template = random.choice(templates)
    
    # Process skills and skill proficiency
    skills_list = ', '.join([f"{skill} ({level})" for skill, level in skill_proficiency.items()])
    key_skill, key_skill_level = list(skill_proficiency.items())[0] if skill_proficiency else ("N/A", "N/A")
    
    # Get the latest work experience
    latest_experience = "worked on key projects"  # Default text if no experiences are provided
    latest_company = "previous employers"         # Default company if no experiences are provided
    if work_experiences:
        latest_experience = work_experiences[-1].get("description", latest_experience)
        latest_company = work_experiences[-1].get("company", latest_company)
    
    # Fill the template with provided information
    description = template.format(
        profession=profession,
        education=education['Level'],
        skills_list=skills_list,
        key_skill=key_skill,
        key_skill_level=key_skill_level,
        latest_company=latest_company,
        latest_experience=latest_experience
    )
    
    return description

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
        pdf.cell(200, 10, txt=f"{exp['start_date']} to {exp['end_date']}", ln=True)
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
        description = st.text_area(f"Description", key=f"description_{i}", height=100)

        experiences.append({
            "company": company,
            "position": position,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "description": description or "Worked on various projects contributing to company goals."
        })

    # Generate description and resume
    st.header("Generate Resume")
    if st.button("Generate Resume"):
        resume_data = {
            "Personal Information": {"Name": name, "Email": email, "Phone": phone},
            "Profession": profession,
            "Skills": skill_proficiency,
            "Education": {"Level": education_level, "Institution": institution, "Graduation Year": graduation_year},
            "Work Experience": experiences
        }
        
        description = generate_description(profession, selected_skills, skill_proficiency, resume_data['Education'], experiences)
        st.write(description)

        pdf_path = generate_pdf(resume_data)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(label="Download Resume", data=pdf_file, file_name="resume.pdf", mime="application/pdf")

run()
