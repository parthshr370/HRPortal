"""
Dashboard layout and metrics for the ATS Portal
"""

import streamlit as st
from typing import Dict, Any, List, Optional

# --- Import Pydantic Models ---
from models.resume_models import ParsedResume
from models.job_match_models import MatchAnalysis
from models.decision_models import DecisionFeedback

from ui.components import (
    create_score_gauge, 
    create_heatmap_score, 
    create_match_metrics,
    create_cultural_fit_metrics,
    create_social_presence_summary,
    create_verification_items
)

def create_analysis_dashboard(
    parsed_resume: Optional[ParsedResume],
    match_analysis: Optional[MatchAnalysis] = None,
    decision: Optional[DecisionFeedback] = None
):
    """Create the main analysis dashboard with all components"""
    if not parsed_resume:
        st.warning("No resume data available. Please upload a resume first.")
        return
    
    # Calculate overall score using attribute access with safe default
    match_score = match_analysis.overall_match_score * 100 if match_analysis else 0.0
    
    # Create page with consistent styling
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .dashboard-container {
            background-color: #1E2F4D;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            color: white;
        }
        .metric-container {
            background-color: #111a2b;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    # Main Analysis Dashboard
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>Analysis Dashboard</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Overall Score Section
        with st.container():
            st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
            create_score_gauge(match_score, "Overall Score")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Heatmap Score Section
        with st.container():
            st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
            create_heatmap_score(match_score)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Cultural Fit Section
        with st.container():
            st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
            create_cultural_fit_metrics(decision)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Detailed Match Analysis Section
        with st.container():
            st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
            if match_analysis:
                create_match_metrics(match_analysis)
            else:
                st.warning("No match analysis available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Decision Summary Section (if available)
        if decision and decision.decision:
            with st.container():
                st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)
                st.markdown("### Decision Summary")
                
                # Extract decision details using attribute access with safe defaults
                status = decision.decision.status or "PENDING"
                confidence = decision.decision.confidence_score or 0
                stage = decision.decision.interview_stage or "SCREENING"
                
                # Set status color
                status_color = "#777777"  # Default gray
                if status == "PROCEED":
                    status_color = "#00CC96"  # Green
                elif status == "HOLD":
                    status_color = "#FFA500"  # Orange
                elif status == "REJECT":
                    status_color = "#FF4B4B"  # Red
                
                # Display decision summary
                cols = st.columns(3)
                with cols[0]:
                    st.markdown(f"""
                    <div style="text-align:center; background-color: rgba(0,0,0,0.2); padding:10px; border-radius:5px;">
                        <div style="font-size:16px;">Status</div>
                        <div style="font-size:24px; color:{status_color}; font-weight:bold;">{status}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"""
                    <div style="text-align:center; background-color: rgba(0,0,0,0.2); padding:10px; border-radius:5px;">
                        <div style="font-size:16px;">Confidence</div>
                        <div style="font-size:24px; font-weight:bold;">{confidence}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[2]:
                    st.markdown(f"""
                    <div style="text-align:center; background-color: rgba(0,0,0,0.2); padding:10px; border-radius:5px;">
                        <div style="font-size:16px;">Stage</div>
                        <div style="font-size:24px; font-weight:bold;">{stage}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display key strengths and concerns with safe access
                if decision.rationale:
                    st.markdown("#### Key Points")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("##### Strengths")
                        strengths = decision.rationale.key_strengths or []
                        for strength in strengths[:3]:
                            st.markdown(f"- {strength}")
                    
                    with col2:
                        st.markdown("##### Concerns")
                        concerns = decision.rationale.concerns or []
                        for concern in concerns[:3]:
                            st.markdown(f"- {concern}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Show detailed resume information
    with st.expander("View Parsed Resume Data"):
        st.json(parsed_resume.model_dump() if parsed_resume else {})