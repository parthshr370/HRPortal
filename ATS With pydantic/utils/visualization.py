"""
Visualization utilities for the ATS Portal
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from typing import Dict, Any, List, Tuple, Optional

def calculate_match_metrics(match_analysis: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate metrics from match analysis data
    """
    metrics = {
        "match_score": match_analysis.get("match_score", 0),
        "skills_score": 0,
        "experience_score": 0,
        "education_score": 0,
        "additional_score": 0
    }
    
    if "analysis" in match_analysis:
        if "skills" in match_analysis["analysis"]:
            metrics["skills_score"] = match_analysis["analysis"]["skills"].get("score", 0)
        
        if "experience" in match_analysis["analysis"]:
            metrics["experience_score"] = match_analysis["analysis"]["experience"].get("score", 0)
        
        if "education" in match_analysis["analysis"]:
            metrics["education_score"] = match_analysis["analysis"]["education"].get("score", 0)
        
        if "additional" in match_analysis["analysis"]:
            metrics["additional_score"] = match_analysis["analysis"]["additional"].get("score", 0)
    
    return metrics

def create_radar_chart(metrics: Dict[str, float], title: str = "Skills Radar") -> plt.Figure:
    """
    Create a radar chart for visualizing multiple metrics
    """
    # Categories and values
    categories = list(metrics.keys())
    values = [metrics[category] for category in categories]
    
    # Convert to 0-1 scale
    values_normalized = [v / 100 for v in values]
    
    # Number of categories
    N = len(categories)
    
    # Create angles for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop
    
    # Values for the chart
    values_normalized += values_normalized[:1]  # Close the loop
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Draw the chart
    ax.plot(angles, values_normalized, linewidth=1, linestyle='solid')
    ax.fill(angles, values_normalized, alpha=0.1)
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    
    # Set y-ticks
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['25%', '50%', '75%', '100%'])
    ax.set_rlim(0, 1)
    
    # Add title
    plt.title(title, size=15, y=1.1)
    
    return fig

def create_comparative_bars(candidates: List[Dict[str, Any]], metric: str = "match_score") -> plt.Figure:
    """
    Create comparative bar chart for multiple candidates on a specific metric
    """
    # Extract names and values
    names = [c.get("name", f"Candidate {i+1}") for i, c in enumerate(candidates)]
    values = [c.get(metric, 0) for c in candidates]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bars
    bars = ax.barh(names, values, height=0.5)
    
    # Color bars based on values
    for i, bar in enumerate(bars):
        if values[i] < 40:
            bar.set_color('#FF4B4B')  # Red
        elif values[i] < 70:
            bar.set_color('#FFA500')  # Orange
        else:
            bar.set_color('#00CC96')  # Green
    
    # Add labels and values
    for i, v in enumerate(values):
        ax.text(v + 1, i, f"{v}%", va='center')
    
    # Set limits and remove spines
    ax.set_xlim(0, 105)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add title and labels
    metric_label = " ".join(metric.split('_')).title()
    ax.set_title(f'Candidate Comparison: {metric_label}')
    ax.set_xlabel('Score (%)')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_decision_distribution_chart(decisions: List[Dict[str, Any]]) -> plt.Figure:
    """
    Create a pie chart showing the distribution of hiring decisions
    """
    # Count decisions by status
    status_counts = {
        "PROCEED": 0,
        "HOLD": 0,
        "REJECT": 0
    }
    
    for decision in decisions:
        if "decision" in decision and "status" in decision["decision"]:
            status = decision["decision"]["status"]
            if status in status_counts:
                status_counts[status] += 1
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Create pie chart
    labels = list(status_counts.keys())
    sizes = list(status_counts.values())
    colors = ['#00CC96', '#FFA500', '#FF4B4B']  # Green, Orange, Red
    
    # Only include non-zero values
    non_zero_indices = [i for i, size in enumerate(sizes) if size > 0]
    filtered_labels = [labels[i] for i in non_zero_indices]
    filtered_sizes = [sizes[i] for i in non_zero_indices]
    filtered_colors = [colors[i] for i in non_zero_indices]
    
    if sum(filtered_sizes) > 0:
        ax.pie(
            filtered_sizes, 
            labels=filtered_labels, 
            colors=filtered_colors,
            autopct='%1.1f%%', 
            startangle=90
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Add title
        plt.title('Decision Distribution', size=15)
    else:
        ax.text(0.5, 0.5, 'No decision data available', ha='center', va='center')
        ax.axis('off')
    
    return fig

def create_timeline_chart(candidates: List[Dict[str, Any]]) -> plt.Figure:
    """
    Create a timeline chart for candidate progress
    """
    # Stages
    stages = ['Applied', 'Screening', 'Interview', 'Offer', 'Hired']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create timeline
    for i, candidate in enumerate(candidates):
        # Get current stage (simulated)
        current_stage = candidate.get('stage', 0)
        
        # Plot line for each candidate
        ax.plot(
            range(len(stages)), 
            [i] * len(stages), 
            'o-', 
            color='#ddd', 
            linewidth=2
        )
        
        # Highlight completed stages
        for stage in range(current_stage + 1):
            ax.plot(stage, i, 'o', color='#1E90FF', markersize=10)
    
    # Set labels
    ax.set_yticks(range(len(candidates)))
    ax.set_yticklabels([c.get('name', f"Candidate {i+1}") for i, c in enumerate(candidates)])
    
    ax.set_xticks(range(len(stages)))
    ax.set_xticklabels(stages)
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Add grid
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add title
    ax.set_title('Candidate Progress Timeline')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_skill_gap_analysis(match_analysis: Dict[str, Any]) -> Tuple[plt.Figure, Dict[str, List[str]]]:
    """
    Create a skill gap analysis visualization
    """
    # Extract skills information
    skills_data = {"required": [], "matched": [], "missing": []}
    
    if "analysis" in match_analysis and "skills" in match_analysis["analysis"]:
        skills_section = match_analysis["analysis"]["skills"]
        
        # Extract matched skills
        matched_skills = skills_section.get("matches", [])
        skills_data["matched"] = matched_skills
        
        # Extract missing skills
        missing_skills = skills_section.get("gaps", [])
        skills_data["missing"] = missing_skills
        
        # Combine to get all required skills
        skills_data["required"] = matched_skills + missing_skills
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set up data for chart
    n_skills = len(skills_data["required"])
    
    if n_skills == 0:
        ax.text(0.5, 0.5, 'No skills data available', ha='center', va='center')
        ax.axis('off')
        return fig, skills_data
    
    # Create indices for skills
    indices = np.arange(n_skills)
    
    # Create matched and missing skill indicators
    matched_indicators = [1 if skill in skills_data["matched"] else 0 for skill in skills_data["required"]]
    missing_indicators = [1 if skill in skills_data["missing"] else 0 for skill in skills_data["required"]]
    
    # Bar width
    width = 0.35
    
    # Create bars
    matched_bars = ax.bar(indices, matched_indicators, width, label='Matched', color='#00CC96')
    missing_bars = ax.bar(indices + width, missing_indicators, width, label='Missing', color='#FF4B4B')
    
    # Add labels and title
    ax.set_xlabel('Skills')
    ax.set_ylabel('Status')
    ax.set_title('Skill Gap Analysis')
    ax.set_xticks(indices + width / 2)
    ax.set_xticklabels(skills_data["required"], rotation=45, ha='right')
    ax.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, skills_data

def create_experience_timeline(parsed_resume: Dict[str, Any]) -> plt.Figure:
    """
    Create a timeline visualization of the candidate's experience
    """
    # Extract experience information
    experiences = []
    
    if "experience" in parsed_resume and parsed_resume["experience"]:
        for exp in parsed_resume["experience"]:
            start_date = exp.get("start_date", "")
            end_date = exp.get("end_date", "Present")
            
            # Try to convert dates to years
            try:
                if isinstance(start_date, str) and start_date.isdigit():
                    start_year = int(start_date)
                elif isinstance(start_date, str) and "-" in start_date:
                    start_year = int(start_date.split("-")[0])
                else:
                    start_year = 2015  # Default if parsing fails
                
                if end_date == "Present":
                    import datetime
                    end_year = datetime.datetime.now().year
                elif isinstance(end_date, str) and end_date.isdigit():
                    end_year = int(end_date)
                elif isinstance(end_date, str) and "-" in end_date:
                    end_year = int(end_date.split("-")[0])
                else:
                    end_year = 2025  # Default if parsing fails
                
                experiences.append({
                    "company": exp.get("company", "Unknown"),
                    "title": exp.get("title", "Unknown"),
                    "start_year": start_year,
                    "end_year": end_year
                })
            except:
                # Skip this experience if date parsing fails
                pass
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if not experiences:
        ax.text(0.5, 0.5, 'No experience data available', ha='center', va='center')
        ax.axis('off')
        return fig
    
    # Sort experiences by start date
    experiences.sort(key=lambda x: x["start_year"])
    
    # Create timeline
    for i, exp in enumerate(experiences):
        # Create bar for experience period
        ax.barh(
            i, 
            exp["end_year"] - exp["start_year"], 
            left=exp["start_year"], 
            height=0.5, 
            color='#1E90FF',
            alpha=0.7
        )
        
        # Add company and title
        ax.text(
            exp["start_year"], 
            i + 0.25, 
            f"{exp['company']} - {exp['title']}", 
            va='center',
            fontsize=10
        )
    
    # Set labels
    ax.set_yticks(range(len(experiences)))
    ax.set_yticklabels([])  # Hide y-labels as we have text in the bars
    
    # Set x-axis limits
    min_year = min([exp["start_year"] for exp in experiences]) - 1
    max_year = max([exp["end_year"] for exp in experiences]) + 1
    ax.set_xlim(min_year, max_year)
    
    # Add grid
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Remove spines
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    
    # Add title
    ax.set_title('Experience Timeline')
    ax.set_xlabel('Year')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_education_visualization(parsed_resume: Dict[str, Any]) -> plt.Figure:
    """
    Create a visualization of the candidate's education
    """
    # Extract education information
    education_entries = []
    
    if "education" in parsed_resume and parsed_resume["education"]:
        for edu in parsed_resume["education"]:
            institution = edu.get("institution", "Unknown")
            degree = edu.get("degree", "Unknown")
            field = edu.get("field", "")
            graduation_date = edu.get("graduation_date", "")
            
            # Try to extract year
            grad_year = None
            if isinstance(graduation_date, str):
                # Try various formats
                if graduation_date.isdigit():
                    grad_year = int(graduation_date)
                elif "-" in graduation_date:
                    parts = graduation_date.split("-")
                    for part in parts:
                        if part.strip().isdigit() and len(part.strip()) == 4:
                            grad_year = int(part.strip())
                            break
            
            education_entries.append({
                "institution": institution,
                "degree": degree,
                "field": field,
                "year": grad_year if grad_year else 0
            })
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if not education_entries:
        ax.text(0.5, 0.5, 'No education data available', ha='center', va='center')
        ax.axis('off')
        return fig
    
    # Sort by year if available
    education_entries.sort(key=lambda x: x["year"] if x["year"] else 0)
    
    # Create visualization
    for i, edu in enumerate(education_entries):
        # Create marker for graduation
        if edu["year"]:
            ax.plot(edu["year"], i, 'o', markersize=10, color='#1E90FF')
            
            # Add line from left to marker
            ax.plot([min([e["year"] for e in education_entries if e["year"]]) - 1, edu["year"]], 
                   [i, i], '-', color='#ddd')
        
        # Add institution and degree
        degree_text = f"{edu['degree']}"
        if edu["field"]:
            degree_text += f" in {edu['field']}"
        
        if edu["year"]:
            ax.text(
                edu["year"] + 0.5, 
                i, 
                f"{edu['institution']} - {degree_text}", 
                va='center'
            )
        else:
            ax.text(
                min([e["year"] for e in education_entries if e["year"]]) - 0.5 if any(e["year"] for e in education_entries) else 2020, 
                i, 
                f"{edu['institution']} - {degree_text}", 
                va='center',
                ha='right'
            )
    
    # Set labels
    ax.set_yticks(range(len(education_entries)))
    ax.set_yticklabels([])  # Hide y-labels as we have text in the chart
    
    # Set x-axis limits
    years = [e["year"] for e in education_entries if e["year"]]
    if years:
        min_year = min(years) - 2
        max_year = max(years) + 2
        ax.set_xlim(min_year, max_year)
    else:
        ax.set_xlim(2015, 2025)  # Default range
    
    # Add grid
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Remove spines
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    
    # Add title
    ax.set_title('Education Timeline')
    ax.set_xlabel('Year')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig

def create_skill_distribution_chart(parsed_resume: Dict[str, Any]) -> plt.Figure:
    """
    Create a visualization of the candidate's skill distribution
    """
    # Extract skills
    technical_skills = []
    soft_skills = []
    
    if "skills" in parsed_resume:
        if "technical" in parsed_resume["skills"]:
            technical_skills = parsed_resume["skills"]["technical"]
        
        if "soft" in parsed_resume["skills"]:
            soft_skills = parsed_resume["skills"]["soft"]
    
    # Prepare data for visualization
    categories = ['Technical Skills', 'Soft Skills']
    counts = [len(technical_skills), len(soft_skills)]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))
    
    if sum(counts) == 0:
        ax.text(0.5, 0.5, 'No skills data available', ha='center', va='center')
        ax.axis('off')
        return fig
    
    # Create bars
    bars = ax.bar(categories, counts, color=['#1E90FF', '#00CC96'])
    
    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    # Remove spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    
    # Add title and labels
    ax.set_title('Skills Distribution')
    ax.set_ylabel('Count')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig