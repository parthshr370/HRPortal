"""
Resume highlighting module for the ATS Portal
Provides color-coded feedback on resumes
"""

import streamlit as st
import re
import html
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

def analyze_skills(skills: List[str], match_analysis: Optional[MatchAnalysis] = None) -> Dict[str, str]:
    """Analyze skills and determine which are good, average, or need improvement"""
    result = {}
    if not match_analysis or not skills:
        return {skill: "neutral" for skill in skills}
    
    # Extract matched skills from analysis
    matched_skills = []
    missing_skills = []
    
    for detail in match_analysis.skills_match.details:
        if detail.startswith("+"):
            # Extract the skill name from the detail text (remove the + prefix)
            matched_text = detail[2:].lower()
            # Split if there's explanation text
            if ":" in matched_text:
                matched_text = matched_text.split(":", 1)[0].strip()
            matched_skills.append(matched_text)
        elif detail.startswith("-"):
            # Extract the missing skill name
            missing_text = detail[2:].lower()
            if ":" in missing_text:
                missing_text = missing_text.split(":", 1)[0].strip()
            missing_skills.append(missing_text)
    
    # Classify each skill
    for skill in skills:
        skill_lower = skill.lower()
        # Try to find if this skill appears in the matches
        found_match = False
        for matched in matched_skills:
            if skill_lower in matched or matched in skill_lower:
                result[skill] = "good"
                found_match = True
                break
        
        if not found_match:
            # Check if it's a missing skill
            for missing in missing_skills:
                if skill_lower in missing or missing in skill_lower:
                    result[skill] = "needs_improvement"
                    found_match = True
                    break
            
            if not found_match:
                # If not clearly matched or missing, consider it average
                result[skill] = "average"
    
    return result

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
    
    # Personal info is typically neutral
    personal_info_html = f'''
    <h1 style="text-align: center;">{name}</h1>
    <p style="text-align: center;">{" • ".join(filter(None, [email, phone, location]))}</p>
    '''
    html_content += highlight_resume_section(personal_info_html, "neutral")
    
    # Summary section
    if parsed_resume.summary:
        summary_html = f'''
        <h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">SUMMARY</h2>
        <p>{parsed_resume.summary}</p>
        '''
        # Determine summary quality - generally neutral unless we have specific feedback
        summary_type = "neutral"
        html_content += highlight_resume_section(summary_html, summary_type)
    
    # Education section
    if parsed_resume.education:
        edu_html = '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">EDUCATION</h2>'
        
        for edu in parsed_resume.education:
            institution = edu.institution or ""
            degree = edu.degree or ""
            field = edu.field or ""
            graduation_date = edu.graduation_date or ""
            gpa = edu.gpa or ""
            
            # Determine education quality
            edu_type = "neutral"  # Default
            
            if match_analysis and match_analysis.education_match.score > 0:
                # Check if education appears in match details
                edu_match_found = False
                for detail in match_analysis.education_match.details:
                    if detail.startswith("+") and (institution.lower() in detail.lower() or degree.lower() in detail.lower() or (field and field.lower() in detail.lower())):
                        edu_type = "good"
                        edu_match_found = True
                        break
                    elif detail.startswith("-") and (institution.lower() in detail.lower() or degree.lower() in detail.lower() or (field and field.lower() in detail.lower())):
                        edu_type = "needs_improvement"
                        edu_match_found = True
                        break
                
                # If degree is in a relevant field but not explicitly mentioned
                if not edu_match_found and match_analysis.education_match.score >= 0.7:
                    edu_type = "good"
                elif not edu_match_found and match_analysis.education_match.score >= 0.4:
                    edu_type = "average"
            
            # If degree is incomplete or in progress, mark as average
            if graduation_date and ("present" in str(graduation_date).lower() or "current" in str(graduation_date).lower()):
                edu_type = "average"
            
            # Format education entry
            edu_entry_html = f'''
            <div>
                <div style="display: flex; justify-content: space-between;">
                    <div><strong>{institution}</strong></div>
                    <div>{graduation_date}</div>
                </div>
                <div><em>{degree}{" in " + field if field else ""}</em></div>
                {f'<div>GPA: {gpa}</div>' if gpa else ''}
            </div>
            '''
            
            edu_html += highlight_resume_section(edu_entry_html, edu_type)
        
        html_content += edu_html
    
    # Experience section
    if parsed_resume.experience:
        exp_html = '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">EXPERIENCE</h2>'
        
        for exp in parsed_resume.experience:
            title = exp.title or ""
            company = exp.company or ""
            location = exp.location or ""
            start_date = exp.start_date or ""
            end_date = exp.end_date or ""
            responsibilities = exp.responsibilities or []
            
            # Determine experience quality
            exp_type = "neutral"  # Default
            
            if match_analysis and match_analysis.experience_match.score > 0:
                # Check if experience appears in match details
                exp_match_found = False
                for detail in match_analysis.experience_match.details:
                    if detail.startswith("+") and (company.lower() in detail.lower() or title.lower() in detail.lower()):
                        exp_type = "good"
                        exp_match_found = True
                        break
                    elif detail.startswith("-") and (company.lower() in detail.lower() or title.lower() in detail.lower()):
                        exp_type = "needs_improvement"
                        exp_match_found = True
                        break
                
                # If not explicitly mentioned but we have a good experience score
                if not exp_match_found and match_analysis.experience_match.score >= 0.7:
                    exp_type = "good"
                elif not exp_match_found and match_analysis.experience_match.score >= 0.4:
                    exp_type = "average"
            
            # Format experience entry
            duration = f"{start_date} - {end_date}" if start_date or end_date else ""
            resp_html = ""
            if responsibilities:
                resp_html = "<ul>"
                for resp in responsibilities:
                    resp_html += f"<li>{resp}</li>"
                resp_html += "</ul>"
            
            exp_entry_html = f'''
            <div>
                <div style="display: flex; justify-content: space-between;">
                    <div><strong>{company}</strong></div>
                    <div>{location}</div>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <div><em>{title}</em></div>
                    <div>{duration}</div>
                </div>
                {resp_html}
            </div>
            '''
            
            exp_html += highlight_resume_section(exp_entry_html, exp_type)
        
        html_content += exp_html
    
    # Skills section
    if parsed_resume.skills:
        skills_html = '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">SKILLS</h2>'
        
        # Analyze skills quality
        skill_ratings = analyze_skills(parsed_resume.skills, match_analysis)
        
        # Group skills by rating
        skill_groups = {
            "good": [],
            "average": [],
            "needs_improvement": []
        }
        
        for skill, rating in skill_ratings.items():
            if rating in skill_groups:
                skill_groups[rating].append(skill)
        
        # Add each skill group with appropriate highlighting
        for rating, skills in skill_groups.items():
            if skills:
                skills_str = ", ".join(skills)
                group_title = {
                    "good": "Strong Skills",
                    "average": "Adequate Skills",
                    "needs_improvement": "Skills to Develop"
                }.get(rating, "Skills")
                
                skill_group_html = f'''
                <div>
                    <strong>{group_title}:</strong>
                    <p>{skills_str}</p>
                </div>
                '''
                
                skills_html += highlight_resume_section(skill_group_html, rating)
        
        html_content += skills_html
    
    # Projects section
    if parsed_resume.projects:
        projects_html = '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">PROJECTS</h2>'
        
        for project in parsed_resume.projects:
            name = project.name or ""
            description = project.description or ""
            technologies = project.technologies or []
            url = project.url or ""
            
            # Determine project quality - based on technologies and relevance
            project_type = "average"  # Default
            
            if technologies and match_analysis:
                # Check if project technologies match job requirements
                tech_match_count = 0
                for tech in technologies:
                    for detail in match_analysis.skills_match.details:
                        if detail.startswith("+") and tech.lower() in detail.lower():
                            tech_match_count += 1
                
                # Rate based on percentage of matching technologies
                if technologies and tech_match_count / len(technologies) >= 0.7:
                    project_type = "good"
                elif technologies and tech_match_count / len(technologies) >= 0.3:
                    project_type = "average"
                else:
                    project_type = "neutral"
            
            # Format project entry
            tech_str = ", ".join(technologies) if technologies else ""
            
            project_entry_html = f'''
            <div>
                <strong>{name}</strong>{f' - <a href="{url}" target="_blank">Link</a>' if url else ''}
                <p>{description}</p>
                {f'<div>Technologies: {tech_str}</div>' if tech_str else ''}
            </div>
            '''
            
            projects_html += highlight_resume_section(project_entry_html, project_type)
        
        html_content += projects_html
    
    # Certifications section
    if parsed_resume.certifications:
        cert_html = '<h2 style="border-bottom: 1px solid #000; padding-bottom: 5px;">CERTIFICATIONS</h2>'
        
        for cert in parsed_resume.certifications:
            name = cert.name or ""
            issuer = cert.issuer or ""
            date = cert.date or ""
            
            # Determine certification quality - generally positive
            cert_type = "good"  # Default for certifications
            
            # Format certification entry
            cert_entry_html = f'''
            <div>
                <strong>{name}</strong>
                {f' - {issuer}' if issuer else ''}
                {f' ({date})' if date else ''}
            </div>
            '''
            
            cert_html += highlight_resume_section(cert_entry_html, cert_type)
        
        html_content += cert_html
    
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
    
    # Debugging info - show match analysis data
    if match_analysis and st.checkbox("Show Match Analysis Data", value=False):
        st.write("Match Analysis Data:", match_analysis)
    
    # Create the HTML content
    html_content = create_resume_feedback(parsed_resume, match_analysis)
    
    # Display the resume in a white card - using components.html instead of markdown
    try:
        from streamlit.components.v1 import html as st_html
        
        st.markdown("<div class='resume-card'>", unsafe_allow_html=True)
        st_html(html_content, height=600, scrolling=True)
        st.markdown("</div>", unsafe_allow_html=True)
    except ImportError:
        # Fallback to iframe if components.html is not available
        import base64
        html_bytes = html_content.encode('utf-8')
        encoded = base64.b64encode(html_bytes).decode()
        
        iframe_html = f"""
        <div class='resume-card'>
            <iframe srcdoc="{encoded}" width="100%" height="600" frameborder="0"></iframe>
        </div>
        """
        st.markdown(iframe_html, unsafe_allow_html=True)
    
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