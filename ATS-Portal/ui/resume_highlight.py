"""
Resume highlighting module for the ATS Portal
Provides color-coded feedback on resumes
"""

import streamlit as st
import re
from typing import Dict, Any, List, Optional

def highlight_resume_section(text: str, section_type: str) -> str:
    """Apply color highlighting to a resume section based on its type"""
    colors = {
        "good": "#90EE90",  # Light green
        "average": "#FFD580",  # Light orange
        "needs_improvement": "#FFCCCB",  # Light red
        "neutral": "#ADD8E6"  # Light blue
    }
    
    color = colors.get(section_type, "#FFFFFF")  # Default to white if type not found
    
    return f'<div style="background-color: {color}; padding: 10px; margin: 5px 0; border-radius: 5px;">{text}</div>'

def create_resume_feedback(parsed_resume: Dict[str, Any], match_analysis: Optional[Dict[str, Any]] = None) -> str:
    """Create an HTML representation of a resume with feedback highlighting"""
    if not parsed_resume:
        return "<p>No resume data available</p>"
    
    html_content = f'<div style="font-family: Arial, sans-serif;">'
    
    # Personal info section
    name = parsed_resume.get("personal_info", {}).get("name", "")
    email = parsed_resume.get("personal_info", {}).get("email", "")
    phone = parsed_resume.get("personal_info", {}).get("phone", "")
    location = parsed_resume.get("personal_info", {}).get("location", "")
    
    html_content += f'<h1 style="text-align: center;">{name}</h1>'
    html_content += f'<p style="text-align: center;">{email} • {phone} • {location}</p>'
    
    # Education section
    if parsed_resume.get("education"):
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">EDUCATION</h2>'
        
        for edu in parsed_resume.get("education", []):
            institution = edu.get("institution", "")
            degree = edu.get("degree", "")
            field = edu.get("field", "")
            graduation_date = edu.get("graduation_date", "")
            gpa = edu.get("gpa", "")
            
            # Determine highlighting based on education quality
            section_type = "neutral"
            if "GPA" in degree or (gpa and float(gpa.replace("GPA: ", "").strip() or 0) > 3.5):
                section_type = "good"
            elif not field or not degree:
                section_type = "needs_improvement"
            else:
                section_type = "average"
            
            edu_content = f'<div style="display: flex; justify-content: space-between;">'
            edu_content += f'<div><strong>{institution}</strong></div>'
            edu_content += f'<div>City, ST</div>'
            edu_content += f'</div>'
            
            edu_content += f'<div style="display: flex; justify-content: space-between;">'
            edu_content += f'<div><em>{degree}{" in " + field if field else ""}</em></div>'
            edu_content += f'<div>{graduation_date}</div>'
            edu_content += f'</div>'
            
            if gpa:
                edu_content += f'<div>• GPA: {gpa}</div>'
            
            # Add feedback suggestions
            edu_content += '<div style="margin-top: 5px;">'
            edu_content += '• Awards: Add named honors and describe each.<br>'
            edu_content += '• Projects: For anything you worked on that points out analytical/project management skills.'
            edu_content += '</div>'
            
            html_content += highlight_resume_section(edu_content, section_type)
    
    # Experience section
    if parsed_resume.get("experience"):
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">EXPERIENCE</h2>'
        
        for i, exp in enumerate(parsed_resume.get("experience", [])):
            company = exp.get("company", "")
            title = exp.get("title", "")
            location = exp.get("location", "")
            start_date = exp.get("start_date", "")
            end_date = exp.get("end_date", "")
            responsibilities = exp.get("responsibilities", [])
            
            # Determine highlighting based on experience quality
            section_type = "average"
            if len(responsibilities) > 3:
                section_type = "good"
            elif len(responsibilities) < 2:
                section_type = "needs_improvement"
            
            exp_content = f'<div style="display: flex; justify-content: space-between;">'
            exp_content += f'<div><strong>{company}</strong></div>'
            exp_content += f'<div>City, ST</div>'
            exp_content += f'</div>'
            
            exp_content += f'<div style="display: flex; justify-content: space-between;">'
            exp_content += f'<div><em>{title}</em></div>'
            exp_content += f'<div>{start_date} - {end_date}</div>'
            exp_content += f'</div>'
            
            if responsibilities:
                exp_content += '<ul style="margin-top: 5px;">'
                for resp in responsibilities:
                    exp_content += f'<li>{resp}</li>'
                exp_content += '</ul>'
            
            # Add feedback suggestions
            exp_content += '<div style="margin-top: 5px;">'
            exp_content += '• Each line needs to have a data point and key takeaway.<br>'
            exp_content += '• Sub-bullet if it makes sense to explain key areas or if multiple projects support a common theme.<br>'
            exp_content += '• 3-4 big bullets are the ideal for each entry.'
            exp_content += '</div>'
            
            html_content += highlight_resume_section(exp_content, section_type)
    
    # Skills section
    if parsed_resume.get("skills"):
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">SKILLS</h2>'
        
        technical_skills = parsed_resume.get("skills", {}).get("technical", [])
        soft_skills = parsed_resume.get("skills", {}).get("soft", [])
        
        # Determine highlighting based on skills quality
        section_type = "average"
        if len(technical_skills) > 5 and len(soft_skills) > 3:
            section_type = "good"
        elif len(technical_skills) < 3:
            section_type = "needs_improvement"
        
        skills_content = '<div>'
        
        if technical_skills:
            skills_content += '<strong>Technical Skills:</strong> ' + ', '.join(technical_skills) + '<br>'
        
        if soft_skills:
            skills_content += '<strong>Soft Skills:</strong> ' + ', '.join(soft_skills)
        
        skills_content += '</div>'
        
        html_content += highlight_resume_section(skills_content, section_type)
    
    # Projects section
    if parsed_resume.get("projects"):
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">PROJECTS</h2>'
        
        for project in parsed_resume.get("projects", []):
            name = project.get("name", "")
            description = project.get("description", "")
            technologies = project.get("technologies", [])
            
            # Determine highlighting based on project quality
            section_type = "neutral"
            if technologies and len(technologies) > 3 and description:
                section_type = "good"
            elif not description:
                section_type = "needs_improvement"
            else:
                section_type = "average"
            
            project_content = f'<div><strong>{name}</strong></div>'
            
            if description:
                project_content += f'<div>{description}</div>'
            
            if technologies:
                project_content += f'<div><em>Technologies:</em> {", ".join(technologies)}</div>'
            
            html_content += highlight_resume_section(project_content, section_type)
    
    # Leadership section (if available in the match analysis)
    if match_analysis and "leadership" in str(match_analysis).lower():
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">LEADERSHIP</h2>'
        
        leadership_content = '<div>'
        leadership_content += '<strong>Organization name - Position</strong><br>'
        leadership_content += '• Each line needs to have a data point and key takeaway.<br>'
        leadership_content += '• These lines need to be different from one another.'
        leadership_content += '</div>'
        
        html_content += highlight_resume_section(leadership_content, "good")
    
    html_content += '</div>'
    
    return html_content

def display_resume_with_feedback(parsed_resume: Dict[str, Any], match_analysis: Optional[Dict[str, Any]] = None):
    """Display a resume with color-coded feedback in Streamlit"""
    st.markdown("<h2 style='color:white;'>Resume Feedback</h2>", unsafe_allow_html=True)
    
    # Apply dark theme to the resume content
    st.markdown("""
    <style>
    .resume-card {
        background-color: white;
        color: black;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the resume in a white card
    st.markdown("<div class='resume-card'>", unsafe_allow_html=True)
    html_content = create_resume_feedback(parsed_resume, match_analysis)
    st.markdown(html_content, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add legend
    st.markdown("<h3 style='color:white;'>Color Legend</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            '<div style="background-color: #90EE90; padding: 10px; border-radius: 5px; text-align: center; color: black;">Good</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            '<div style="background-color: #FFD580; padding: 10px; border-radius: 5px; text-align: center; color: black;">Average</div>',
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            '<div style="background-color: #FFCCCB; padding: 10px; border-radius: 5px; text-align: center; color: black;">Needs Improvement</div>',
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            '<div style="background-color: #ADD8E6; padding: 10px; border-radius: 5px; text-align: center; color: black;">Neutral</div>',
            unsafe_allow_html=True
        )
    
    # Explanation of the feedback
    st.markdown("<h3 style='color:white;'>How to Use This Feedback</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color:#1E2F4D; padding:20px; border-radius:10px; margin-top:20px;'>
        <p>This color-coded feedback highlights the strengths and areas for improvement in your resume:</p>
        <ul>
            <li><strong style='color:#90EE90;'>Green sections</strong> are strong and well-developed</li>
            <li><strong style='color:#FFD580;'>Orange sections</strong> are adequate but could be improved</li>
            <li><strong style='color:#FFCCCB;'>Red sections</strong> need attention and enhancement</li>
            <li><strong style='color:#ADD8E6;'>Blue sections</strong> are neutral or supplementary information</li>
        </ul>
        <p>Follow the specific suggestions in each section to improve your resume and increase your match score for the current job position.</p>

        <h4>Best Practices for Resume Enhancement:</h4>
        <ul>
            <li>Use strong action verbs at the beginning of each bullet point</li>
            <li>Quantify achievements with specific metrics and numbers</li>
            <li>Tailor your resume to the specific job description</li>
            <li>Focus on accomplishments rather than just responsibilities</li>
            <li>Keep formatting consistent throughout the document</li>
            <li>Ensure all content is relevant to the position you're applying for</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)