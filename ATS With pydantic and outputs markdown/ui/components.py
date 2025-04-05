"""
UI components for the ATS Portal dashboard and visualization
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from typing import List, Dict, Any, Union, Tuple, Optional

# --- Import Pydantic Models ---
from models.job_match_models import MatchAnalysis
from models.decision_models import DecisionFeedback

def create_progress_bar(label: str, value: int, color: str = "blue", max_value: int = 100):
    """Create a custom progress bar with label and percentage"""
    # Set the color based on the value
    if color == "auto":
        if value < 40:
            color = "#FF4B4B"  # Red
        elif value < 70:
            color = "#FFA500"  # Orange
        else:
            color = "#00CC96"  # Green
    
    # Create the progress bar with dark theme styling
    st.markdown(f"""
    <div style="margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <div style="color: white;"><strong>{label}</strong></div>
            <div style="color: white;">{value}%</div>
        </div>
        <div style="height: 8px; background-color: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
            <div style="width: {value}%; height: 100%; background-color: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_score_gauge(score: int, title: str = "Overall Score", color: str = "auto", size: int = 200):
    """Create a circular gauge for displaying scores"""
    if color == "auto":
        if score < 40:
            color = "#FF4B4B"  # Red
        elif score < 70:
            color = "#FFA500"  # Orange 
        else:
            color = "#00CC96"  # Green
    
    # Create a gauge with matplotlib
    fig, ax = plt.subplots(figsize=(size/100, size/100), subplot_kw={'projection': 'polar'})
    
    # Set dark background
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')
    
    # Adjust the appearance
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)
    
    # Set limits
    ax.set_ylim(0, 1)
    
    # Create the gauge
    theta = np.linspace(0, 2*np.pi, 100)
    r = np.ones_like(theta) * 0.8
    
    # Background
    ax.fill(theta, r, color='#333333', alpha=0.5)
    
    # Value portion
    theta_value = np.linspace(0, 2*np.pi*score/100, 100)
    ax.fill(theta_value, r[:len(theta_value)], color=color, alpha=0.8)
    
    # Add center text
    ax.text(0, 0, f"{score}%", ha='center', va='center', fontsize=size/5, fontweight='bold', color='white')
    
    # Remove grid, ticks, and spines
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown(f"<div style='text-align:center; color:white;'><strong>{title}</strong></div>", unsafe_allow_html=True)

def create_heatmap_score(score: int, label: str = "Heatmap Score"):
    """Create a horizontal heatmap score visualization"""
    # Define colors and thresholds
    colors = ["#FF4B4B", "#FFA500", "#FFDF00", "#A0D636", "#00CC96"]
    thresholds = [0, 25, 50, 75, 90, 100]
    labels = ["Needs Improvements", "Average", "Excellent Match"]
    
    # Calculate position of indicator on the heatmap
    indicator_pos = int((score / 100) * 100)
    
    # Create layout columns
    st.markdown(f"### {label}")
    
    # Create the heatmap bar - using f-string to avoid formatting issues
    st.markdown(f"""
    <style>
    .heatmap-container {{
        width: 100%;
        height: 20px;
        background: linear-gradient(to right, #FF4B4B, #FFA500, #FFDF00, #A0D636, #00CC96);
        border-radius: 10px;
        margin: 20px 0;
        position: relative;
    }}
    .indicator {{
        width: 20px;
        height: 20px;
        background-color: white;
        border: 2px solid #333;
        border-radius: 50%;
        position: absolute;
        top: -10px;
        transform: translateX(-50%);
    }}
    .threshold-label {{
        position: absolute;
        transform: translateX(-50%);
        font-size: 12px;
        margin-top: 10px;
    }}
    .score-label {{
        position: absolute;
        bottom: -40px;
        font-weight: bold;
        transform: translateX(-50%);
    }}
    </style>
    <div class="heatmap-container">
        <div class="indicator" style="left: {indicator_pos}%;"></div>
    </div>
    
    <div style="display: flex; justify-content: space-between; margin-top: 30px; color: white;">
        <div style="text-align: left;">Needs Improvements</div>
        <div style="text-align: center;">Average</div>
        <div style="text-align: right;">Excellent Match</div>
    </div>
    """, unsafe_allow_html=True)

def create_match_metrics(match_analysis: Optional[MatchAnalysis]):
    """Create a visualization of match metrics from job matching analysis"""
    if not match_analysis:
        st.warning("Match analysis data not available")
        return
    
    # Extract scores from the match analysis components
    scores = {
        "Skills": match_analysis.skills_match.score,
        "Experience": match_analysis.experience_match.score,
        "Education": match_analysis.education_match.score
    }
    
    # Display overall score first
    col1, col2 = st.columns([1, 2])
    
    with col1:
        create_score_gauge(int(match_analysis.overall_match_score * 100), "Overall Match Score")
    
    with col2:
        st.markdown("<h3 style='color:white;'>Key Match Metrics</h3>", unsafe_allow_html=True)
        for category, score in scores.items():
            create_progress_bar(category, int(score * 100), "auto")
    
    # Display details and insights
    st.markdown("<h3 style='color:white;'>Skills Match Details</h3>", unsafe_allow_html=True)
    for detail in match_analysis.skills_match.details:
        st.markdown(f"- {detail}")

    st.markdown("<h3 style='color:white;'>Experience Match Details</h3>", unsafe_allow_html=True)
    for detail in match_analysis.experience_match.details:
        st.markdown(f"- {detail}")

    st.markdown("<h3 style='color:white;'>Education Match Details</h3>", unsafe_allow_html=True)
    for detail in match_analysis.education_match.details:
        st.markdown(f"- {detail}")

    if match_analysis.additional_insights:
        st.markdown("<h3 style='color:white;'>Additional Insights</h3>", unsafe_allow_html=True)
        for insight in match_analysis.additional_insights:
            st.markdown(f"- {insight}")

    if match_analysis.recommended_interview_questions:
        st.markdown("<h3 style='color:white;'>Recommended Interview Questions</h3>", unsafe_allow_html=True)
        for question in match_analysis.recommended_interview_questions:
            st.markdown(f"- {question}")

def create_cultural_fit_metrics(decision_data: Optional[DecisionFeedback]):
    """Create cultural fit score metrics based on decision feedback (currently uses placeholders)"""
    if not decision_data:
        st.warning("Decision data not available")
        return
    
    st.markdown("<h3 style='color:white;'>Cultural Fit Score</h3>", unsafe_allow_html=True)
    
    # Define cultural metrics (PLACEHOLDER - update this logic if needed based on decision_data fields)
    # Example: could try to derive scores from decision_data.rationale or decision_data.hiring_manager_notes
    metrics = {
        "Passion": 16,
        "Delegation": 28,
        "Communication": 22,
        "Leadership": 36,
        "Customer Centricity": 50
    }
    
    # Display each metric
    for metric, value in metrics.items():
        create_progress_bar(metric, value, "blue")
    
    # Add legend
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="display: flex; align-items: center; color:white;">'
                  '<div style="width: 12px; height: 12px; border-radius: 50%; background-color: blue; margin-right: 8px;"></div>'
                  '<div>Reported</div>'
                  '</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="display: flex; align-items: center; color:white;">'
                  '<div style="width: 12px; height: 12px; border-radius: 50%; background-color: lightblue; margin-right: 8px;"></div>'
                  '<div>Claimed</div>'
                  '</div>', unsafe_allow_html=True)

def create_keyword_match_indicator(score: int, label: str = "Keyword Match Score"):
    """Create a semicircular indicator for keyword match score"""
    # Create a gauge with matplotlib
    fig, ax = plt.subplots(figsize=(3, 1.5), subplot_kw={'projection': 'polar'})
    
    # Set dark background
    fig.patch.set_facecolor('#121212')
    ax.set_facecolor('#121212')
    
    # Set color based on score
    if score < 40:
        color = "#FF4B4B"  # Red
    elif score < 70:
        color = "#FFA500"  # Orange 
    else:
        color = "#1E90FF"  # Blue
    
    # Create the semicircular gauge
    theta = np.linspace(0, np.pi, 100)
    r = np.ones_like(theta)
    
    # Background
    ax.fill_between(theta, 0, r, color='#333333', alpha=0.5)
    
    # Value portion
    theta_value = np.linspace(0, np.pi*score/100, 100)
    ax.fill_between(theta_value, 0, r[:len(theta_value)], color=color, alpha=0.8)
    
    # Add center text
    ax.text(np.pi/2, 0.5, f"{score}%", ha='center', va='center', fontsize=20, fontweight='bold', color='white')
    
    # Remove grid, ticks, and spines
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Set limits
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    plt.tight_layout()
    
    return fig

def create_social_presence_summary(social_score: int = 50, plagiarism_score: int = 64, 
                                  jd_match: int = 88, format_score: int = 78):
    """Create a summary of social presence and other metrics"""
    # Create layout with metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        fig = create_keyword_match_indicator(70, "Keyword Match")
        st.pyplot(fig)
        st.markdown("<div style='text-align:center; color:white;'>Keyword Match<br>Score</div>", unsafe_allow_html=True)
    
    with col2:
        fig = create_keyword_match_indicator(social_score, "Social Network")
        st.pyplot(fig)
        st.markdown("<div style='text-align:center; color:white;'>Social Network<br>Score</div>", unsafe_allow_html=True)
    
    with col3:
        fig = create_keyword_match_indicator(plagiarism_score, "Plagiarism") 
        st.pyplot(fig)
        st.markdown("<div style='text-align:center; color:white;'>Plagiarism<br>Score</div>", unsafe_allow_html=True)
    
    with col4:
        fig = create_keyword_match_indicator(jd_match, "JD Match")
        st.pyplot(fig)
        st.markdown("<div style='text-align:center; color:white;'>JD Match<br>Score</div>", unsafe_allow_html=True)
    
    with col5:
        fig = create_keyword_match_indicator(format_score, "Format & Content")
        st.pyplot(fig)
        st.markdown("<div style='text-align:center; color:white;'>Format &<br>Content Score</div>", unsafe_allow_html=True)

def create_verification_item(title: str, description: str, status: str = "Completed"):
    """Create a verification item with check mark"""
    # Set status color and icon
    if status == "Completed":
        icon = "✅"
        progress = 100
        status_color = "#00CC96"  # Green
    else:
        icon = "⏳"
        progress = 50  
        status_color = "#FFA500"  # Orange
    
    # Create the item with dark theme styling
    st.markdown(f"""
    <div style="display: flex; margin-bottom: 20px; align-items: flex-start; background-color:#1E2F4D; padding:15px; border-radius:8px;">
        <div style="font-size: 24px; margin-right: 10px;">{icon}</div>
        <div style="flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; color:white;">
                <strong>{title}</strong>
                <div>
                    <div style="width: 100px; height: 6px; background-color: rgba(255,255,255,0.2); border-radius: 3px; margin-top: 8px;">
                        <div style="width: {progress}%; height: 100%; background-color: {status_color};"></div>
                    </div>
                </div>
            </div>
            <div style="color: #aaa; font-size: 14px; margin-top: 5px;">{description}</div>
        </div>
        <div style="margin-left: 20px;">
            <a href="#" style="color: #1E90FF; text-decoration: none; font-size: 14px; background-color:rgba(30,144,255,0.2); padding:5px 10px; border-radius:4px;">Take Me There &rarr;</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_verification_items():
    """Create verification items for the candidate screening summary"""
    create_verification_item(
        "Social Network Analysis",
        "Checked for all Social Networks provided."
    )
    
    create_verification_item(
        "Plagiarism & Content Analysis",
        "Checked for unique contributions and experience"
    )
    
    create_verification_item(
        "Data Extraction and Parsing",
        "Extracted all relevant information"
    )
    
    create_verification_item(
        "Scoring and Ranking",
        "Normalized against the parameters and scored."
    )