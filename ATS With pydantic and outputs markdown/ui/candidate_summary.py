"""
Candidate summary module for the ATS Portal
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import random
import datetime # Added import for date calculations

# --- Import Pydantic Models ---
from models.resume_models import ParsedResume
from models.job_match_models import MatchAnalysis
from models.decision_models import DecisionFeedback

from ui.components import create_verification_item, create_progress_bar
from ui.social_media_analysis import create_social_media_analysis_section, create_screening_summary, create_verification_progress

def generate_candidate_metrics(parsed_resume: Optional[ParsedResume], job_description: str = "") -> Dict[str, Any]:
    """
    Generate metrics for the candidate based on the parsed resume and job description.
    This is a placeholder function - in a real implementation, you would use more sophisticated
    analysis to generate these metrics.
    """
    # Generate base metrics with reasonable defaults
    metrics = {
        "keyword_match": 0,
        "social_network": 0,
        "plagiarism": 0,
        "jd_match": 0,
        "format_score": 0,
    }
    
    # Try to make more realistic scores based on resume content
    if parsed_resume:
        # Keyword match based on skills list
        if parsed_resume.skills:
            metrics["keyword_match"] = min(95, 80 + len(parsed_resume.skills) * 2)
        
        # JD match based on experience
        if parsed_resume.experience:
            metrics["jd_match"] = min(98, 85 + len(parsed_resume.experience) * 3)
        
        # Format score based on completeness
        format_score = 60  # Base score
        if parsed_resume.personal_info and parsed_resume.personal_info.name:
            format_score += 10
        if parsed_resume.education and len(parsed_resume.education) > 0:
            format_score += 10
        if parsed_resume.experience and len(parsed_resume.experience) > 0:
            format_score += 10
        if parsed_resume.skills and len(parsed_resume.skills) > 0:
            format_score += 10
        metrics["format_score"] = format_score
        
        # Placeholder scores for other metrics
        metrics["social_network"] = 70
        metrics["plagiarism"] = 85
    
    return metrics

def create_candidate_summary_page(
    parsed_resume: Optional[ParsedResume],
    match_analysis: Optional[MatchAnalysis] = None,
    decision: Optional[DecisionFeedback] = None,
    job_description: str = ""
):
    """Create the full candidate summary page with all details"""
    if not parsed_resume:
        st.warning("No resume data available. Please upload a resume first.")
        return
    
    # Calculate metrics - use match analysis if available
    metrics = generate_candidate_metrics(parsed_resume, job_description)
    
    if match_analysis:
        # Use attribute access with safe defaults
        metrics["keyword_match"] = int(match_analysis.overall_match_score * 100)
        metrics["jd_match"] = int(match_analysis.overall_match_score * 100)
    
    # Extract candidate info using attribute access and providing defaults
    name = parsed_resume.personal_info.name if parsed_resume.personal_info else "Candidate"
    
    # Try to get most recent job title using attribute access with safe defaults
    role = "Candidate"
    if parsed_resume.experience and len(parsed_resume.experience) > 0:
        role = parsed_resume.experience[0].title or "Candidate"

    location = parsed_resume.personal_info.location if parsed_resume.personal_info else ""
    
    # Calculate experience using attribute access with safe defaults
    experience_years = 0
    experience_months = 0
    if parsed_resume.experience:
        for exp in parsed_resume.experience:
            start = exp.start_date
            end = exp.end_date or "Present"
            
            try:
                # Assuming format YYYY-MM or YYYY
                start_year = 0
                start_month = 1
                if start:
                    if "-" in start:
                        parts = start.split("-")
                        if len(parts) >= 1:
                            start_year = int(parts[0])
                        if len(parts) >= 2:
                            start_month = int(parts[1])
                    elif start.isdigit():
                        start_year = int(start)
                    
                end_year = 0
                end_month = 0
                if end == "Present":
                    now = datetime.datetime.now()
                    end_year = now.year
                    end_month = now.month
                elif end:
                    if "-" in end:
                        parts = end.split("-")
                        if len(parts) >= 1:
                            end_year = int(parts[0])
                        if len(parts) >= 2:
                            end_month = int(parts[1])
                        else:  # Assume YYYY means end of year if month missing
                            end_month = 12
                    elif end.isdigit():
                        end_year = int(end)
                        end_month = 12  # Assume end of year if only year given
                
                if start_year > 0 and end_year > 0:
                    months = (end_year - start_year) * 12 + (end_month - start_month)
                    if months > 0:
                        total_months = months
                        experience_years = total_months // 12
                        experience_months = total_months % 12
            except (ValueError, AttributeError) as e:
                print(f"Error calculating experience duration: {str(e)}")
                continue
    
    # Create the summary page
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Candidate Summary</h1>", unsafe_allow_html=True)
    
    # Create tabs for different sections
    candidate_tabs = st.tabs(["Overview", "Screening Summary", "Match Details"])
    
    # Tab 1: Overview
    with candidate_tabs[0]:
        st.markdown("<h3 style='margin-bottom: 20px;'>Candidate Overview</h3>", unsafe_allow_html=True)
        
        # Basic info section
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown(f"""
            <div style="background-color: #1E2F4D; padding: 20px; border-radius: 10px;">
                <h2 style="margin:0; color: white;">{name}</h2>
                <p style="color: #B0B0B0; margin-top: 5px;">{role}</p>
                <p style="color: #B0B0B0;">{location}</p>
                <p style="color: #B0B0B0;">Experience: {experience_years}y {experience_months}m</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if match_analysis:
                score = int(match_analysis.overall_match_score * 100)
                st.markdown(f"""
                <div style="background-color: #1E2F4D; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3 style="margin:0; color: white;">Match Score</h3>
                    <h1 style="color: #1E90FF; margin:10px 0;">{score}%</h1>
                </div>
                """, unsafe_allow_html=True)
    
        # Create social media analysis section
        create_social_media_analysis_section()
    
    # Tab 2: Screening Summary
    with candidate_tabs[1]:
        st.markdown("<h3 style='margin-bottom: 20px;'>Screening Summary</h3>", unsafe_allow_html=True)
        create_screening_summary()
        create_verification_progress()
    
    # Tab 3: Match Details
    with candidate_tabs[2]:
        st.markdown("<h3 style='margin-bottom: 20px;'>Job Match Details</h3>", unsafe_allow_html=True)
        
        if match_analysis:
            # Display match score
            score = int(match_analysis.overall_match_score * 100)
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:20px;">
                <div style="font-size:48px; font-weight:bold; color:#1E90FF;">
                    {score}%
                </div>
                <div style="font-size:16px;">Overall Match Score</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display category scores
            cols = st.columns(3)
            categories = {
                "Skills": match_analysis.skills_match,
                "Experience": match_analysis.experience_match,
                "Education": match_analysis.education_match
            }
            
            for i, (category, breakdown) in enumerate(categories.items()):
                with cols[i]:
                    score = int(breakdown.score * 100)
                    st.markdown(f"""
                    <div style="text-align:center; background-color:#1E2F4D; padding:10px; border-radius:8px;">
                        <div style="font-size:24px; font-weight:bold; color:#1E90FF;">{score}%</div>
                        <div style="font-size:14px; color:white;">{category}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display details
            st.markdown("<div style='background-color:#1E2F4D; padding:20px; border-radius:8px; margin-top:20px;'>", unsafe_allow_html=True)
            
            # Display skills details
            st.markdown("#### Skills Match")
            for detail in match_analysis.skills_match.details:
                st.markdown(f"- {detail}")
            
            # Display experience details
            st.markdown("#### Experience Match")
            for detail in match_analysis.experience_match.details:
                st.markdown(f"- {detail}")
            
            # Display education details
            st.markdown("#### Education Match")
            for detail in match_analysis.education_match.details:
                st.markdown(f"- {detail}")
            
            # Display additional insights
            if match_analysis.additional_insights:
                st.markdown("#### Additional Insights")
                for insight in match_analysis.additional_insights:
                    st.markdown(f"- {insight}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No match analysis available. Please process a job description to see match details.")

def create_candidate_list(candidates):
    """Create a list of candidates with summary metrics"""
    st.markdown("### Candidate List")
    
    # If no candidates, show message
    if not candidates:
        st.info("No candidates available")
        return
    
    # Display candidates in a table
    for candidate in candidates:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.image("https://via.placeholder.com/100", width=100)
        
        with col2:
            st.markdown(f"**{candidate['name']}**")
            st.markdown(f"{candidate['role']}")
            st.markdown(f"Experience: {candidate['experience']} years")
        
        with col3:
            st.markdown(f"Match Score: {candidate['match_score']}%")
            st.markdown(f"Status: {candidate['status']}")
            st.button("View Details", key=f"view_{candidate['id']}")
        
        st.markdown("---")