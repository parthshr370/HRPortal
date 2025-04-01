"""
Social media analysis functions for the ATS Portal
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from ui.components import create_progress_bar

def create_social_media_analysis_section():
    """Create a section showing social media analysis results with proper HTML rendering"""
    st.markdown("<h3 style='margin-bottom: 20px;'>Social Media Analysis</h3>", unsafe_allow_html=True)
    
    # LinkedIn Profile Analysis with proper HTML
    st.markdown("""
    <div style="background-color: #1E2F4D; padding: 20px; border-radius: 8px; margin-bottom: 15px; color: white;">
        <h4>LinkedIn Profile Analysis</h4>
        <ul>
            <li><strong>Connections:</strong> 450+ professional connections</li>
            <li><strong>Endorsements:</strong> 28 skills endorsed by 65+ connections</li>
            <li><strong>Activity:</strong> Regular professional posts and engagement</li>
            <li><strong>Groups:</strong> Member of 5 relevant professional groups</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # GitHub Activity with proper HTML
    st.markdown("""
    <div style="background-color: #1E2F4D; padding: 20px; border-radius: 8px; margin-bottom: 15px; color: white;">
        <h4>GitHub Activity</h4>
        <ul>
            <li><strong>Repositories:</strong> 12 public repositories</li>
            <li><strong>Contributions:</strong> 647 contributions in the last year</li>
            <li><strong>Stars:</strong> 45 stars across projects</li>
            <li><strong>Languages:</strong> Python (65%), JavaScript (25%), Other (10%)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Social Media Metrics - Using three columns
    st.markdown("<h3 style='margin: 30px 0 20px 0;'>Social Media Metrics</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h4 style='text-align: center;'>Professional Presence</h4>", unsafe_allow_html=True)
        create_progress_bar("LinkedIn", 85, "#0077B5")
        create_progress_bar("GitHub", 78, "#333333")
        create_progress_bar("Stack Overflow", 62, "#F48024")
    
    with col2:
        st.markdown("<h4 style='text-align: center;'>Content Quality</h4>", unsafe_allow_html=True)
        create_progress_bar("Technical Posts", 76, "#00CC96")
        create_progress_bar("Project Documentation", 82, "#00CC96")
        create_progress_bar("Code Quality", 79, "#00CC96")
    
    with col3:
        st.markdown("<h4 style='text-align: center;'>Red Flags</h4>", unsafe_allow_html=True)
        create_progress_bar("Inappropriate Content", 5, "#FF4B4B")
        create_progress_bar("Inconsistencies", 12, "#FF4B4B")
        create_progress_bar("Inactivity Periods", 25, "#FFA500")

def create_screening_summary():
    """Create the candidate screening summary section with proper HTML rendering"""
    st.markdown("<h3 style='margin-bottom: 20px;'>Candidate Screening Summary</h3>", unsafe_allow_html=True)
    
    # Container for screening summary
    st.markdown("""
    <div style="background-color: #1E2F4D; padding: 20px; border-radius: 8px; margin-bottom: 20px; color: white;">
        <p>Automated the initial screening by analyzing resumes for:</p>
        <ul>
            <li><strong>Keywords:</strong> Matching job requirements.</li>
            <li><strong>Experience:</strong> Verifying relevant work history.</li>
            <li><strong>Education:</strong> Confirming necessary qualifications.</li>
        </ul>
        
        <p>Social network analysis highlighted strengths and potential concerns.</p>
        <ul>
            <li>This adds a layer of depth: The ATS didn't just look at resumes; it also analyzed 
            candidates' online presence, revealing:</li>
            <li><strong>Strengths:</strong> Positive professional activity, endorsements, relevant connections.</li>
            <li><strong>Potential concerns:</strong> Red flags from public posts or associations.</li>
        </ul>
        
        <p><strong>Recommendations:</strong> Interview top candidates, investigate red flags, address 
        screening question weaknesses.</p>
    </div>
    """, unsafe_allow_html=True)

def create_verification_progress():
    """Create the verification progress section with proper styling"""
    st.markdown("<h3 style='margin: 30px 0 20px 0;'>Verification Progress</h3>", unsafe_allow_html=True)
    
    verification_items = [
        {
            "title": "Social Network Analysis",
            "description": "Checked for all Social Networks provided.",
            "status": "Completed",
            "progress": 100
        },
        {
            "title": "Plagiarism & Content Analysis",
            "description": "Checked for unique contributions and experience",
            "status": "Completed",
            "progress": 100
        },
        {
            "title": "Data Extraction and Parsing",
            "description": "Extracted all relevant information",
            "status": "Completed", 
            "progress": 100
        },
        {
            "title": "Scoring and Ranking",
            "description": "Normalized against the parameters and scored.",
            "status": "Completed",
            "progress": 100
        }
    ]
    
    for item in verification_items:
        create_verification_item_styled(
            title=item["title"],
            description=item["description"],
            status=item["status"],
            progress=item["progress"]
        )

def create_verification_item_styled(title: str, description: str, status: str = "Completed", progress: int = 100):
    """Create a verification item with more elaborate styling"""
    # Determine status styling
    if status == "Completed":
        icon = "✅"
        status_color = "#00CC96"  # Green
        status_text = "Completed"
    else:
        icon = "⏳"
        status_color = "#FFA500"  # Orange
        status_text = "In Progress"
    
    # Create the item with improved styling
    st.markdown(f"""
    <div style="display: flex; margin-bottom: 20px; background-color: #1E2F4D; padding: 15px; border-radius: 8px; color: white;">
        <div style="font-size: 24px; margin-right: 15px;">{icon}</div>
        <div style="flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 18px; font-weight: bold;">{title}</div>
                <div style="width: 200px; height: 8px; background-color: rgba(255,255,255,0.2); border-radius: 4px; margin-left: 20px;">
                    <div style="width: {progress}%; height: 100%; background-color: {status_color}; border-radius: 4px;"></div>
                </div>
            </div>
            <div style="font-size: 14px; margin-top: 8px; opacity: 0.8;">{description}</div>
        </div>
        <div style="margin-left: 20px; display: flex; align-items: center;">
            <a href="#" style="color: #1E90FF; text-decoration: none; background-color: rgba(30,144,255,0.2); padding: 8px 12px; border-radius: 4px; font-size: 14px;">Take Me There →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)