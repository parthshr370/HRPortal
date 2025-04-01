"""
Candidate summary module for the ATS Portal
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import random
from ui.components import create_verification_item, create_progress_bar
from ui.social_media_analysis import create_social_media_analysis_section, create_screening_summary, create_verification_progress

def generate_candidate_metrics(parsed_resume: Dict[str, Any], job_description: str = "") -> Dict[str, Any]:
    """
    Generate metrics for the candidate based on the parsed resume and job description.
    This is a placeholder function - in a real implementation, you would use more sophisticated
    analysis to generate these metrics.
    """
    # Generate random scores for demonstration purposes
    # In a real implementation, these would be calculated based on actual analysis
    metrics = {
        "keyword_match": random.randint(85, 95),
        "social_network": random.randint(50, 70),
        "plagiarism": random.randint(50, 70),
        "jd_match": random.randint(85, 98),
        "format_score": random.randint(60, 80),
    }
    
    # Try to make more realistic scores based on resume content
    if parsed_resume:
        # Keyword match could be based on skills matching
        if parsed_resume.get("skills") and parsed_resume["skills"].get("technical"):
            metrics["keyword_match"] = min(95, 80 + len(parsed_resume["skills"]["technical"]) * 1)
        
        # JD match could be based on experience relevance
        if parsed_resume.get("experience") and len(parsed_resume["experience"]) > 1:
            metrics["jd_match"] = min(98, 90 + len(parsed_resume["experience"]) * 2)
    
    return metrics

def create_candidate_summary_page(parsed_resume: Dict[str, Any], 
                                 match_analysis: Optional[Dict[str, Any]] = None,
                                 decision: Optional[Dict[str, Any]] = None,
                                 job_description: str = ""):
    """Create the full candidate summary page with all details"""
    if not parsed_resume:
        st.warning("No resume data available. Please upload a resume first.")
        return
    
    # Calculate metrics - use match analysis if available
    metrics = generate_candidate_metrics(parsed_resume, job_description)
    
    if match_analysis:
        metrics["keyword_match"] = match_analysis.get("match_score", metrics["keyword_match"])
        if "analysis" in match_analysis:
            if "skills" in match_analysis["analysis"]:
                metrics["keyword_match"] = match_analysis["analysis"]["skills"].get("score", metrics["keyword_match"])
            
            # Update JD match from the analysis overall score
            metrics["jd_match"] = match_analysis.get("match_score", metrics["jd_match"])
    
    # Extract candidate info
    name = parsed_resume.get("personal_info", {}).get("name", "Candidate")
    
    # Try to get most recent job title
    if parsed_resume.get("experience") and len(parsed_resume["experience"]) > 0:
        role = parsed_resume["experience"][0].get("title", "Candidate")
    else:
        role = "Candidate"
    
    location = parsed_resume.get("personal_info", {}).get("location", "")
    
    # Calculate experience
    experience_years = 0
    experience_months = 0
    if parsed_resume.get("experience"):
        # Simple count of number of jobs
        experience_years = len(parsed_resume["experience"])
        
        # Try to calculate more precise experience duration if dates are available
        total_months = 0
        for exp in parsed_resume.get("experience", []):
            start = exp.get("start_date", "")
            end = exp.get("end_date", "Present")
            
            # Simple parsing - would need more robust implementation in production
            if start and isinstance(start, str):
                try:
                    if "-" in start:
                        start_year, start_month = map(int, start.split("-"))
                    else:
                        start_year = int(start)
                        start_month = 1
                    
                    if end == "Present":
                        import datetime
                        end_year = datetime.datetime.now().year
                        end_month = datetime.datetime.now().month
                    elif "-" in end:
                        end_year, end_month = map(int, end.split("-"))
                    else:
                        end_year = int(end)
                        end_month = 12
                    
                    months = (end_year - start_year) * 12 + (end_month - start_month)
                    total_months += months
                except:
                    # Fallback if parsing fails
                    pass
        
        if total_months > 0:
            experience_years = total_months // 12
            experience_months = total_months % 12
    
    # Format email & phone for display
    email = parsed_resume.get("personal_info", {}).get("email", "")
    phone = parsed_resume.get("personal_info", {}).get("phone", "")
    
    # Display candidate information
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 30px;'>{name}</h1>", unsafe_allow_html=True)
    
    # Candidate header with photo and info
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Placeholder for candidate photo - in a real app, this would be the candidate's photo
        st.image("https://via.placeholder.com/150", width=150)
    
    with col2:
        st.markdown(f"<h2 style='margin-top: 0;'>{role}</h2>", unsafe_allow_html=True)
        st.markdown(f"Experience: {experience_years} years {experience_months} months")
        st.markdown(f"Location: {location}")
        if email:
            st.markdown(f"Email: <a href='mailto:{email}'>{email}</a>", unsafe_allow_html=True)
        if phone:
            st.markdown(f"Phone: {phone}")
    
    # Display metrics from job matching and analysis
    st.markdown("<h3 style='text-align: center; margin: 30px 0 20px 0;'>Candidate Metrics</h3>", unsafe_allow_html=True)
    
    # Use more consistent layout for metrics
    metric_cols = st.columns(5)
    metrics_data = [
        {"label": "Keyword Match<br>Score", "value": metrics['keyword_match']},
        {"label": "Social Network<br>Score", "value": metrics['social_network']},
        {"label": "Plagiarism<br>Score", "value": metrics['plagiarism']},
        {"label": "JD Match<br>Score", "value": metrics['jd_match']},
        {"label": "Format &<br>Content Score", "value": metrics['format_score']}
    ]
    
    for i, col in enumerate(metric_cols):
        with col:
            metric = metrics_data[i]
            st.markdown(f"""
            <div style="text-align:center; background-color:#1E2F4D; padding:15px; border-radius:8px; height:120px; display:flex; flex-direction:column; justify-content:center;">
                <div style="font-size:36px; font-weight:bold; color:#1E90FF;">{metric['value']}%</div>
                <div style="font-size:14px; color:white;">{metric['label']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Sub-tabs for different sections of the candidate report
    candidate_tabs = st.tabs(["Screening Summary", "Social Analysis", "Match Details", "Decision"])
    
    # Tab 1: Screening Summary
    with candidate_tabs[0]:
        create_screening_summary()
        create_verification_progress()
    
    # Tab 2: Social Media Analysis
    with candidate_tabs[1]:
        create_social_media_analysis_section()
    
    # Tab 3: Match Details
    with candidate_tabs[2]:
        st.markdown("<h3 style='margin-bottom: 20px;'>Job Match Details</h3>", unsafe_allow_html=True)
        
        if match_analysis:
            # Display match score
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:20px;">
                <div style="font-size:48px; font-weight:bold; color:#1E90FF;">
                    {match_analysis.get('match_score', 0)}%
                </div>
                <div style="font-size:16px;">Overall Match Score</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display category scores
            if "analysis" in match_analysis:
                cols = st.columns(4)
                categories = ["skills", "experience", "education", "additional"]
                
                for i, category in enumerate(categories):
                    with cols[i]:
                        if category in match_analysis["analysis"]:
                            score = match_analysis["analysis"][category].get("score", 0)
                            st.markdown(f"""
                            <div style="text-align:center; background-color:#1E2F4D; padding:10px; border-radius:8px;">
                                <div style="font-size:24px; font-weight:bold; color:#1E90FF;">{score}%</div>
                                <div style="font-size:14px; color:white;">{category.capitalize()}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Display matches and gaps
                st.markdown("<div style='background-color:#1E2F4D; padding:20px; border-radius:8px; margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("#### Skills")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Matches")
                    if "skills" in match_analysis["analysis"]:
                        for skill in match_analysis["analysis"]["skills"].get("matches", []):
                            st.markdown(f"- {skill}")
                
                with col2:
                    st.markdown("##### Gaps")
                    if "skills" in match_analysis["analysis"]:
                        for gap in match_analysis["analysis"]["skills"].get("gaps", []):
                            st.markdown(f"- {gap}")
                
                st.markdown("#### Experience")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Matches")
                    if "experience" in match_analysis["analysis"]:
                        for exp in match_analysis["analysis"]["experience"].get("matches", []):
                            st.markdown(f"- {exp}")
                
                with col2:
                    st.markdown("##### Gaps")
                    if "experience" in match_analysis["analysis"]:
                        for gap in match_analysis["analysis"]["experience"].get("gaps", []):
                            st.markdown(f"- {gap}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display recommendation
            if "recommendation" in match_analysis:
                st.markdown("<div style='background-color:#1E2F4D; padding:20px; border-radius:8px; margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("#### Recommendation")
                st.markdown(f"> {match_analysis['recommendation']}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display strengths and considerations
            st.markdown("<div style='background-color:#1E2F4D; padding:20px; border-radius:8px; margin-top:20px;'>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Key Strengths")
                for strength in match_analysis.get("key_strengths", []):
                    st.markdown(f"- {strength}")
            
            with col2:
                st.markdown("#### Areas for Consideration")
                for area in match_analysis.get("areas_for_consideration", []):
                    st.markdown(f"- {area}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No match analysis data available")
    
    # Tab 4: Decision
    with candidate_tabs[3]:
        st.markdown("<h3 style='margin-bottom: 20px;'>Hiring Decision</h3>", unsafe_allow_html=True)
        
        if decision:
            # Display decision status
            status = decision.get("decision", {}).get("status", "UNKNOWN")
            confidence = decision.get("decision", {}).get("confidence_score", 0)
            stage = decision.get("decision", {}).get("interview_stage", "UNKNOWN")
            
            # Set status color
            status_color = "#777777"  # Default gray
            if status == "PROCEED":
                status_color = "#00CC96"  # Green
            elif status == "HOLD":
                status_color = "#FFA500"  # Orange
            elif status == "REJECT":
                status_color = "#FF4B4B"  # Red
            
            # Create layout for Status, Confidence, and Stage
            cols = st.columns(3)
            
            with cols[0]:
                st.markdown(f"""
                <div style="background-color:{status_color}; color:white; text-align:center; padding:20px; border-radius:8px;">
                    <div style="font-size:24px; font-weight:bold;">Status</div>
                    <div style="font-size:36px;">{status}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cols[1]:
                st.markdown(f"""
                <div style="background-color:#1E2F4D; text-align:center; padding:20px; border-radius:8px;">
                    <div style="font-size:24px; font-weight:bold;">Confidence</div>
                    <div style="font-size:36px;">{confidence}%</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cols[2]:
                st.markdown(f"""
                <div style="background-color:#1E2F4D; text-align:center; padding:20px; border-radius:8px;">
                    <div style="font-size:24px; font-weight:bold;">Stage</div>
                    <div style="font-size:36px;">{stage}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Display rationale
            if "rationale" in decision:
                st.markdown("<div style='background-color:#1E2F4D; padding:20px; border-radius:8px; margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("#### Rationale")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("##### Key Strengths")
                    for strength in decision["rationale"].get("key_strengths", []):
                        st.markdown(f"- {strength}")
                
                with col2:
                    st.markdown("##### Concerns")
                    for concern in decision["rationale"].get("concerns", []):
                        st.markdown(f"- {concern}")
                
                st.markdown("##### Risk Factors")
                for risk in decision["rationale"].get("risk_factors", []):
                    st.markdown(f"- {risk}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display recommendations
            if "recommendations" in decision:
                st.markdown("<div style='background-color:#1E2F4D; padding:20px; border-radius:8px; margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("#### Recommendations")
                
                cols = st.columns(3)
                
                with cols[0]:
                    st.markdown("##### Interview Focus")
                    for focus in decision["recommendations"].get("interview_focus", []):
                        st.markdown(f"- {focus}")
                
                with cols[1]:
                    st.markdown("##### Skill Verification")
                    for skill in decision["recommendations"].get("skill_verification", []):
                        st.markdown(f"- {skill}")
                
                with cols[2]:
                    st.markdown("##### Discussion Points")
                    for point in decision["recommendations"].get("discussion_points", []):
                        st.markdown(f"- {point}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Display next steps
            if "next_steps" in decision:
                st.markdown("<div style='background-color:#1E2F4D; padding:20px; border-radius:8px; margin-top:20px;'>", unsafe_allow_html=True)
                st.markdown("#### Next Steps")
                
                st.markdown("##### Immediate Actions")
                for action in decision["next_steps"].get("immediate_actions", []):
                    st.markdown(f"- {action}")
                
                st.markdown("##### Required Approvals")
                for approval in decision["next_steps"].get("required_approvals", []):
                    st.markdown(f"- {approval}")
                
                st.markdown("##### Timeline Recommendation")
                st.markdown(f"> {decision['next_steps'].get('timeline_recommendation', 'No recommendation provided')}")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No decision data available")

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