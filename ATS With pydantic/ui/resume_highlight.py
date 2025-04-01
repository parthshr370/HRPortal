"""
Resume highlighting module for the ATS Portal
Provides color-coded feedback on resumes
"""

import streamlit as st
import re
from typing import Dict, Any, List, Optional

# --- Import Pydantic Models ---
from models.resume_models import ParsedResume
from models.job_match_models import MatchAnalysis

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

def create_resume_feedback(parsed_resume: Optional[ParsedResume], match_analysis: Optional[MatchAnalysis] = None) -> str:
    """Create an HTML representation of a resume with feedback highlighting"""
    if not parsed_resume:
        return "<p>No resume data available</p>"
    
    html_content = '<div style="font-family: Arial, sans-serif;">'
    
    # Personal info section using attribute access with safe defaults
    name = parsed_resume.personal_info.name if parsed_resume.personal_info else ""
    email = parsed_resume.personal_info.email if parsed_resume.personal_info else ""
    phone = parsed_resume.personal_info.phone if parsed_resume.personal_info else ""
    location = parsed_resume.personal_info.location if parsed_resume.personal_info else ""
    
    html_content += f'<h1 style="text-align: center;">{name}</h1>'
    contact_info = []
    if email:
        contact_info.append(email)
    if phone:
        contact_info.append(phone)
    if location:
        contact_info.append(location)
    html_content += f'<p style="text-align: center;">{" • ".join(contact_info)}</p>'
    
    # Summary section
    if parsed_resume.summary:
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">SUMMARY</h2>'
        html_content += f'<p>{parsed_resume.summary}</p>'
    
    # Education section
    if parsed_resume.education:
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">EDUCATION</h2>'
        
        for edu in parsed_resume.education:
            institution = edu.institution or ""
            degree = edu.degree or ""
            field = edu.field or ""
            graduation_year = edu.graduation_year or ""
            gpa = edu.gpa or ""
            
            # Determine highlighting based on education quality
            section_type = "neutral"
            if gpa:
                try:
                    gpa_value = float(str(gpa))  # Convert to string first in case it's already a float
                    if gpa_value > 3.5:
                        section_type = "good"
                except ValueError:
                    pass  # Ignore if GPA is not a valid number

            if not field or not degree:
                section_type = "needs_improvement"
            elif section_type == "neutral":  # Only change to average if not already good/bad
                section_type = "average"
            
            html_content += f'<div class="{section_type}">'
            html_content += f'<div style="display: flex; justify-content: space-between;">'
            html_content += f'<div><strong>{institution}</strong></div>'
            if location:
                html_content += f'<div>{location}</div>'
            html_content += f'</div>'
            
            html_content += f'<div style="display: flex; justify-content: space-between;">'
            html_content += f'<div><em>{degree}{" in " + field if field else ""}</em></div>'
            if graduation_year:
                html_content += f'<div>{graduation_year}</div>'
            html_content += f'</div>'
            
            if gpa:
                html_content += f'<div>• GPA: {gpa}</div>'
            html_content += '</div>'
    
    # Experience section
    if parsed_resume.experience:
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">EXPERIENCE</h2>'
        
        for exp in parsed_resume.experience:
            title = exp.title or ""
            company = exp.company or ""
            duration = exp.duration or ""
            description = exp.description or []
            location = exp.location or ""
            
            html_content += '<div class="experience-item">'
            html_content += f'<div style="display: flex; justify-content: space-between;">'
            html_content += f'<div><strong>{company}</strong></div>'
            if location:
                html_content += f'<div>{location}</div>'
            html_content += f'</div>'
            
            html_content += f'<div style="display: flex; justify-content: space-between;">'
            html_content += f'<div><em>{title}</em></div>'
            html_content += f'<div>{duration}</div>'
            html_content += f'</div>'
            
            if description:
                html_content += '<ul style="margin-top: 5px;">'
                for bullet in description:
                    html_content += f'<li>{bullet}</li>'
                html_content += '</ul>'
            html_content += '</div>'
    
    # Skills section
    if parsed_resume.skills:
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">SKILLS</h2>'
        html_content += '<ul>'
        for skill in parsed_resume.skills:
            html_content += f'<li>{skill}</li>'
        html_content += '</ul>'
    
    # Projects section
    if parsed_resume.projects:
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">PROJECTS</h2>'
        for project in parsed_resume.projects:
            name = project.name or ""
            description = project.description or ""
            technologies = project.technologies or []
            url = project.url or ""
            
            html_content += '<div class="project-item">'
            html_content += f'<strong>{name}</strong>'
            if url:
                html_content += f' - <a href="{url}" target="_blank">Link</a>'
            if description:
                html_content += f'<p>{description}</p>'
            if technologies:
                html_content += '<div>Technologies: ' + ', '.join(technologies) + '</div>'
            html_content += '</div>'
    
    # Certifications section
    if parsed_resume.certifications:
        html_content += '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">CERTIFICATIONS</h2>'
        for cert in parsed_resume.certifications:
            name = cert.name or ""
            issuer = cert.issuer or ""
            date = cert.date or ""
            
            html_content += '<div class="certification-item">'
            html_content += f'<strong>{name}</strong>'
            if issuer:
                html_content += f' - {issuer}'
            if date:
                html_content += f' ({date})'
            html_content += '</div>'
    
    html_content += '</div>'
    return html_content

def display_resume_with_feedback(parsed_resume: Optional[ParsedResume], match_analysis: Optional[MatchAnalysis] = None):
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