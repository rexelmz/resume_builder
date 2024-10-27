import streamlit as st
import pandas as pd

def run():
    st.title("Resume Builder")

    # Personal Information
    st.header("Personal Information")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")

    # Profession
    st.header("Profession")
    profession = st.selectbox("Select your profession", ["Software Developer", "Data Scientist", "Product Manager", "Other"])
    if profession == "Other":
        profession = st.text_input("Specify your profession")

    # Skills
    st.header("Skills")
    skills = st_tags(label='Enter your skills',
                     text='Press enter to add more',
                     value=['Python', 'Data Analysis'],
                     key='skills')

    # Skill Proficiency
    st.subheader("Skill Proficiency")
    skill_proficiency = {}
    for skill in skills:
        skill_proficiency[skill] = st.select_slider(f"Proficiency in {skill}", options=['Beginner', 'Intermediate', 'Advanced', 'Expert'], key=skill)

    # Education
    st.header("Education")
    education_level = st.selectbox("Highest Education Level", ["High School", "Bachelor's", "Master's", "PhD"])
    institution = st.text_input("Institution Name")
    graduation_year = st.number_input("Graduation Year", min_value=1950, max_value=2030, value=2020)

    # Work Experience
    st.header("Work Experience")
    num_experiences = st.number_input("Number of work experiences", min_value=0, max_value=10, value=1)
    experiences = []
    for i in range(num_experiences):
        st.subheader(f"Experience {i+1}")
        company = st.text_input(f"Company Name", key=f"company_{i}")
        position = st.text_input(f"Position", key=f"position_{i}")
        start_date = st.date_input(f"Start Date", key=f"start_date_{i}")
        end_date = st.date_input(f"End Date", key=f"end_date_{i}")
        description = st.text_area(f"Description", key=f"description_{i}")
        experiences.append({
            "company": company,
            "position": position,
            "start_date": start_date,
            "end_date": end_date,
            "description": description
        })

    # Generate Resume
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
        
        # Here you can add functionality to format and download the resume

def st_tags(label, text, value, key=None):
    """Custom function to mimic st_tags from streamlit_tags"""
    return st.multiselect(label, options=value + [""], default=value, key=key)

if __name__ == "__main__":
    run()
