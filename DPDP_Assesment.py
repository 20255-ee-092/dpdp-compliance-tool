import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import json
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="DPDP Compliance Assessment Tool",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'current_section' not in st.session_state:
    st.session_state.current_section = 0
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'assessment_complete' not in st.session_state:
    st.session_state.assessment_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'organization_name' not in st.session_state:
    st.session_state.organization_name = ""
if 'assessment_date' not in st.session_state:
    st.session_state.assessment_date = datetime.now().strftime("%Y-%m-%d")

# Define sections and questions (directly from our questionnaire)
sections = [
    {
        "name": "Consent Management",
        "weight": 0.15,
        "questions": [
            "Does your organization obtain explicit consent before collecting personal data?",
            "Is your consent mechanism presented in clear, plain language?",
            "Do you have separate consent mechanisms for different data processing activities?",
            "Can users easily withdraw their consent?"
        ],
        "options": [
            ["Yes, with clear affirmative action required", "Partially, but consent mechanisms need improvement", "No, we rely on implicit consent", "Not applicable"],
            ["Yes, we use simple language and avoid legal jargon", "Partially, but needs simplification", "No, our consent notices use technical/legal terminology", "Not applicable"],
            ["Yes, we obtain separate consent for each purpose", "Partially, but some purposes are bundled", "No, we use a single consent for all processing", "Not applicable"],
            ["Yes, through a simple, accessible process", "Yes, but the process is somewhat complicated", "No, withdrawal options are difficult to access", "Not applicable"]
        ]
    },
    {
        "name": "Purpose Limitation",
        "weight": 0.12,
        "questions": [
            "Does your organization clearly document all purposes for which personal data is processed?",
            "Is personal data used only for the specific purposes for which it was collected?",
            "Do you have mechanisms to prevent data use beyond stated purposes?"
        ],
        "options": [
            ["Yes, all purposes are documented and reviewed regularly", "Partially, some purposes are documented", "No, purposes are not systematically documented", "Not applicable"],
            ["Yes, strictly limited to stated purposes", "Mostly, with rare exceptions", "No, data is often repurposed", "Not applicable"],
            ["Yes, we have technical and policy controls", "Partially, some controls exist", "No, limited controls exist", "Not applicable"]
        ]
    },
    {
        "name": "Data Minimization",
        "weight": 0.10,
        "questions": [
            "Does your organization collect only data that is necessary for specified purposes?",
            "Do you have processes to identify and remove redundant or excessive data?"
        ],
        "options": [
            ["Yes, we regularly review and minimize data collection", "Partially, some unnecessary data may be collected", "No, we collect data that may not be necessary", "Not applicable"],
            ["Yes, regular data minimization reviews", "Partially, occasional reviews", "No systematic process", "Not applicable"]
        ]
    },
    {
        "name": "Data Retention",
        "weight": 0.10,
        "questions": [
            "Does your organization have a documented data retention policy?",
            "Are retention periods defined for different categories of personal data?",
            "Do you have automated processes to delete or anonymize data after retention periods expire?"
        ],
        "options": [
            ["Yes, comprehensive and regularly reviewed", "Partially, basic policy exists", "No documented policy", "Not applicable"],
            ["Yes, specific periods for each data category", "Partially, general periods defined", "No defined periods", "Not applicable"],
            ["Yes, fully automated", "Partially automated with manual oversight", "Manual process only", "No systematic process", "Not applicable"]
        ]
    },
    {
        "name": "Data Subject Rights",
        "weight": 0.15,
        "questions": [
            "Does your organization have procedures to handle data subject access requests?",
            "Can you provide data subjects with copies of their personal data in a structured, commonly used format?",
            "Do you have processes to correct inaccurate personal data upon request?",
            "Can you completely erase personal data upon valid request ('right to be forgotten')?"
        ],
        "options": [
            ["Yes, comprehensive procedures", "Basic procedures exist", "No formal procedures", "Not applicable"],
            ["Yes, automated export functionality", "Yes, but manual process", "Limited capability", "No capability", "Not applicable"],
            ["Yes, systematic process", "Basic process exists", "Ad hoc handling", "No process", "Not applicable"],
            ["Yes, across all systems", "Partially, in primary systems", "Limited capability", "No capability", "Not applicable"]
        ]
    },
    {
        "name": "Security Measures",
        "weight": 0.15,
        "questions": [
            "Does your organization implement appropriate technical security measures for personal data?",
            "Do you conduct regular security assessments of systems processing personal data?",
            "Do you have access controls limiting who can access personal data?",
            "Is personal data encrypted at rest and in transit?"
        ],
        "options": [
            ["Yes, comprehensive measures following industry standards", "Basic security measures", "Minimal security measures", "Not applicable"],
            ["Yes, scheduled regular assessments", "Occasional assessments", "Rarely or never", "Not applicable"],
            ["Yes, role-based access with principle of least privilege", "Basic access controls", "Limited or no access controls", "Not applicable"],
            ["Yes, comprehensive encryption", "Partial encryption (either at rest or in transit)", "Limited or no encryption", "Not applicable"]
        ]
    },
    {
        "name": "Data Breach Management",
        "weight": 0.12,
        "questions": [
            "Does your organization have a data breach response plan?",
            "Can you detect data breaches in a timely manner?",
            "Do you have procedures to notify authorities of data breaches within required timeframes?",
            "Do you document all data breaches and remediation actions?"
        ],
        "options": [
            ["Yes, comprehensive and tested", "Basic plan exists", "No formal plan", "Not applicable"],
            ["Yes, monitoring systems in place", "Basic detection capabilities", "Limited or no detection capabilities", "Not applicable"],
            ["Yes, clear procedures", "Basic procedures exist", "No formal procedures", "Not applicable"],
            ["Yes, comprehensive documentation", "Basic documentation", "Limited or no documentation", "Not applicable"]
        ]
    },
    {
        "name": "Cross-Border Data Transfers",
        "weight": 0.05,
        "questions": [
            "Does your organization transfer personal data outside India?",
            "If yes, do you ensure adequate protection for cross-border data transfers?",
            "Do you maintain records of all cross-border data transfers?"
        ],
        "options": [
            ["Yes, regularly", "Occasionally", "No", "Not applicable"],
            ["Yes, comprehensive measures", "Basic measures", "Limited or no measures", "Not applicable"],
            ["Yes, detailed records", "Basic records", "Limited or no records", "Not applicable"]
        ]
    },
    {
        "name": "Data Protection Impact Assessments",
        "weight": 0.03,
        "questions": [
            "Do you conduct Data Protection Impact Assessments for high-risk processing activities?",
            "Are DPIA results incorporated into processing designs?"
        ],
        "options": [
            ["Yes, systematically", "Occasionally", "Rarely or never", "Not applicable"],
            ["Yes, systematically", "Sometimes", "Rarely or never", "Not applicable"]
        ]
    },
    {
        "name": "Data Protection Officer and Governance",
        "weight": 0.03,
        "questions": [
            "Has your organization designated a Data Protection Officer or equivalent role?",
            "Does your organization provide regular data protection training to staff?",
            "Is compliance with data protection regulations regularly audited?"
        ],
        "options": [
            ["Yes, dedicated DPO", "Yes, as additional responsibility", "No designated role", "Not applicable"],
            ["Yes, comprehensive training program", "Basic training provided", "Limited or no training", "Not applicable"],
            ["Yes, scheduled regular audits", "Occasional audits", "Rarely or never audited", "Not applicable"]
        ]
    }
]

# Define answer point values (directly from our scoring algorithm)
answer_points = {
    # Full compliance answers (1.0)
    "Yes, with clear affirmative action required": 1.0,
    "Yes, we use simple language and avoid legal jargon": 1.0,
    "Yes, we obtain separate consent for each purpose": 1.0,
    "Yes, through a simple, accessible process": 1.0,
    "Yes, all purposes are documented and reviewed regularly": 1.0,
    "Yes, strictly limited to stated purposes": 1.0,
    "Yes, we have technical and policy controls": 1.0,
    "Yes, we regularly review and minimize data collection": 1.0,
    "Yes, regular data minimization reviews": 1.0,
    "Yes, comprehensive and regularly reviewed": 1.0,
    "Yes, specific periods for each data category": 1.0,
    "Yes, fully automated": 1.0,
    "Yes, comprehensive procedures": 1.0,
    "Yes, automated export functionality": 1.0,
    "Yes, systematic process": 1.0,
    "Yes, across all systems": 1.0,
    "Yes, comprehensive measures following industry standards": 1.0,
    "Yes, scheduled regular assessments": 1.0,
    "Yes, role-based access with principle of least privilege": 1.0,
    "Yes, comprehensive encryption": 1.0,
    "Yes, comprehensive and tested": 1.0,
    "Yes, monitoring systems in place": 1.0,
    "Yes, clear procedures": 1.0,
    "Yes, comprehensive documentation": 1.0,
    "Yes, comprehensive measures": 1.0,
    "Yes, detailed records": 1.0,
    "Yes, systematically": 1.0,
    "Yes, dedicated DPO": 1.0,
    "Yes, comprehensive training program": 1.0,
    "Yes, scheduled regular audits": 1.0,
    
    # Partial compliance answers (0.5)
    "Partially, but consent mechanisms need improvement": 0.5,
    "Partially, but needs simplification": 0.5,
    "Partially, but some purposes are bundled": 0.5,
    "Yes, but the process is somewhat complicated": 0.5,
    "Partially, some purposes are documented": 0.5,
    "Mostly, with rare exceptions": 0.5,
    "Partially, some controls exist": 0.5,
    "Partially, some unnecessary data may be collected": 0.5,
    "Partially, occasional reviews": 0.5,
    "Partially, basic policy exists": 0.5,
    "Partially, general periods defined": 0.5,
    "Partially automated with manual oversight": 0.5,
    "Basic procedures exist": 0.5,
    "Yes, but manual process": 0.5,
    "Basic process exists": 0.5,
    "Partially, in primary systems": 0.5,
    "Basic security measures": 0.5,
    "Occasional assessments": 0.5,
    "Basic access controls": 0.5,
    "Partial encryption (either at rest or in transit)": 0.5,
    "Basic plan exists": 0.5,
    "Basic detection capabilities": 0.5,
    "Basic procedures exist": 0.5,
    "Basic documentation": 0.5,
    "Basic measures": 0.5,
    "Basic records": 0.5,
    "Occasionally": 0.5,
    "Sometimes": 0.5,
    "Yes, as additional responsibility": 0.5,
    "Basic training provided": 0.5,
    "Occasional audits": 0.5,
    
    # Non-compliance answers (0.0)
    "No, we rely on implicit consent": 0.0,
    "No, our consent notices use technical/legal terminology": 0.0,
    "No, we use a single consent for all processing": 0.0,
    "No, withdrawal options are difficult to access": 0.0,
    "No, purposes are not systematically documented": 0.0,
    "No, data is often repurposed": 0.0,
    "No, limited controls exist": 0.0,
    "No, we collect data that may not be necessary": 0.0,
    "No systematic process": 0.0,
    "No documented policy": 0.0,
    "No defined periods": 0.0,
    "Manual process only": 0.0,
    "No formal procedures": 0.0,
    "Limited capability": 0.0,
    "No capability": 0.0,
    "Ad hoc handling": 0.0,
    "No process": 0.0,
    "Minimal security measures": 0.0,
    "Rarely or never": 0.0,
    "Limited or no access controls": 0.0,
    "Limited or no encryption": 0.0,
    "No formal plan": 0.0,
    "Limited or no detection capabilities": 0.0,
    "Limited or no documentation": 0.0,
    "Limited or no measures": 0.0,
    "Limited or no records": 0.0,
    "No designated role": 0.0,
    "Limited or no training": 0.0,
    "Rarely or never audited": 0.0,
    
    # Special cases
    "No": 0.0,  # For cross-border transfers question
    "Not applicable": None
}

# Recommendations dictionary
recommendations = {
    # Consent Management
    "Consent Management": {
        "Partially, but consent mechanisms need improvement": "Implement clearer consent mechanisms with explicit opt-in options",
        "No, we rely on implicit consent": "Replace implicit consent with explicit consent mechanisms",
        "Partially, but needs simplification": "Simplify consent language and avoid technical jargon",
        "No, our consent notices use technical/legal terminology": "Rewrite consent notices in plain, simple language",
        "Partially, but some purposes are bundled": "Separate consent for different data processing purposes",
        "No, we use a single consent for all processing": "Implement granular consent options for different processing activities",
        "Yes, but the process is somewhat complicated": "Simplify the consent withdrawal process",
        "No, withdrawal options are difficult to access": "Make consent withdrawal options easily accessible"
    },
    # Purpose Limitation
    "Purpose Limitation": {
        "Partially, some purposes are documented": "Document all purposes for personal data processing",
        "No, purposes are not systematically documented": "Create a comprehensive data processing register",
        "Mostly, with rare exceptions": "Implement stricter controls to prevent purpose creep",
        "No, data is often repurposed": "Establish clear purpose limitation policy and controls",
        "Partially, some controls exist": "Strengthen controls to prevent data use beyond stated purposes",
        "No, limited controls exist": "Implement technical and policy controls for purpose limitation"
    },
    # Data Minimization
    "Data Minimization": {
        "Partially, some unnecessary data may be collected": "Review data collection processes to minimize data collected",
        "No, we collect data that may not be necessary": "Conduct a data inventory and eliminate unnecessary collection",
        "Partially, occasional reviews": "Implement regular data minimization reviews",
        "No systematic process": "Establish a systematic process for identifying redundant data"
    },
    # Data Retention
    "Data Retention": {
        "Partially, basic policy exists": "Develop a comprehensive data retention policy",
        "No documented policy": "Create and implement a formal data retention policy",
        "Partially, general periods defined": "Define specific retention periods for each data category",
        "No defined periods": "Establish clear retention periods for all data categories",
        "Partially automated with manual oversight": "Enhance automation of data deletion processes",
        "Manual process only": "Implement semi-automated data deletion processes",
        "No systematic process": "Establish a systematic process for data deletion after retention periods"
    },
    # Data Subject Rights
    "Data Subject Rights": {
        "Basic procedures exist": "Enhance procedures for handling data subject requests",
        "No formal procedures": "Establish formal procedures for data subject access requests",
        "Yes, but manual process": "Develop more automated export functionality",
        "Limited capability": "Improve capability to provide data in structured formats",
        "No capability": "Implement systems to export data in structured formats",
        "Basic process exists": "Enhance processes for correcting inaccurate data",
        "Ad hoc handling": "Formalize processes for handling correction requests",
        "No process": "Establish processes for correcting personal data upon request",
        "Partially, in primary systems": "Extend deletion capabilities to all systems",
        "Limited capability": "Improve data erasure capabilities across systems",
        "No capability": "Implement mechanisms for complete data erasure"
    },
    # Security Measures
    "Security Measures": {
        "Basic security measures": "Enhance security measures with encryption and access controls",
        "Minimal security measures": "Implement comprehensive security based on ISO 27001",
        "Occasional assessments": "Establish regular security assessment schedule",
        "Rarely or never": "Implement regular security assessments of data processing systems",
        "Basic access controls": "Implement role-based access with least privilege principle",
        "Limited or no access controls": "Develop comprehensive access control framework",
        "Partial encryption (either at rest or in transit)": "Implement full encryption for data at rest and in transit",
        "Limited or no encryption": "Establish encryption standards for all personal data"
    },
    # Data Breach Management
    "Data Breach Management": {
        "Basic plan exists": "Develop and test a comprehensive breach response plan",
        "No formal plan": "Create and implement a formal data breach response plan",
        "Basic detection capabilities": "Enhance breach detection systems",
        "Limited or no detection capabilities": "Implement monitoring systems for timely breach detection",
        "Basic procedures exist": "Enhance procedures for authority notifications",
        "No formal procedures": "Establish procedures for timely breach notifications",
        "Basic documentation": "Improve documentation processes for breaches",
        "Limited or no documentation": "Implement comprehensive breach documentation system"
    },
    # Cross-Border Data Transfers
    "Cross-Border Data Transfers": {
        "Basic measures": "Enhance protection measures for cross-border transfers",
        "Limited or no measures": "Implement adequate safeguards for international transfers",
        "Basic records": "Improve record-keeping for cross-border transfers",
        "Limited or no records": "Establish comprehensive records of all data transfers"
    },
    # Data Protection Impact Assessments
    "Data Protection Impact Assessments": {
        "Occasionally": "Conduct DPIAs systematically for all high-risk processing",
        "Rarely or never": "Implement DPIA framework for high-risk processing activities",
        "Sometimes": "Ensure DPIA results are consistently incorporated into designs",
        "Rarely or never": "Create processes to incorporate DPIA findings into system design"
    },
    # DPO and Governance
    "Data Protection Officer and Governance": {
        "Yes, as additional responsibility": "Consider dedicated DPO role based on processing volume",
        "No designated role": "Designate a Data Protection Officer or equivalent role",
        "Basic training provided": "Enhance data protection training program",
        "Limited or no training": "Implement regular data protection training for all staff",
        "Occasional audits": "Establish regular compliance audit schedule",
        "Rarely or never audited": "Implement regular compliance audits"
    }
}

# Function to calculate compliance scores
def calculate_compliance_score():
    section_scores = {}
    section_recommendations = {}
    
    # Calculate scores for each section
    for i, section in enumerate(sections):
        section_name = section["name"]
        section_weight = section["weight"]
        section_score = 0
        applicable_questions = 0
        section_recommendations[section_name] = []
        
        # Process each question in the section
        for j, question in enumerate(section["questions"]):
            question_key = f"s{i}_q{j}"
            
            if question_key in st.session_state.responses:
                response = st.session_state.responses[question_key]
                score = answer_points.get(response)
                
                # Skip N/A responses
                if score is None:
                    continue
                
                section_score += score
                applicable_questions += 1
                
                # Generate recommendation if score < 1
                if score < 1.0:
                    if response in recommendations.get(section_name, {}):
                        section_recommendations[section_name].append(
                            recommendations[section_name][response]
                        )
        
        # Calculate average score for the section
        if applicable_questions > 0:
            section_scores[section_name] = section_score / applicable_questions
        else:
            section_scores[section_name] = None
    
    # Calculate weighted overall score
    total_weighted_score = 0
    applicable_weight_sum = 0
    
    for section_name, score in section_scores.items():
        if score is not None:
            section_weight = next((s["weight"] for s in sections if s["name"] == section_name), 0)
            total_weighted_score += score * section_weight
            applicable_weight_sum += section_weight
    
    overall_score = 0
    if applicable_weight_sum > 0:
        overall_score = (total_weighted_score / applicable_weight_sum) * 100
    
    # Determine compliance level
    compliance_level = ""
    if overall_score >= 90:
        compliance_level = "High Compliance"
    elif overall_score >= 75:
        compliance_level = "Substantial Compliance"
    elif overall_score >= 50:
        compliance_level = "Partial Compliance"
    else:
        compliance_level = "Low Compliance"
    
    # Identify high risk areas (sections with scores below 0.6)
    high_risk_areas = [
        section for section, score in section_scores.items() 
        if score is not None and score < 0.6
    ]
    high_risk_areas.sort(key=lambda x: section_scores.get(x, 1))
    
    # Return results
    return {
        "overall_score": overall_score,
        "compliance_level": compliance_level,
        "section_scores": section_scores,
        "high_risk_areas": high_risk_areas,
        "recommendations": section_recommendations,
        "improvement_priorities": high_risk_areas[:3]  # Top 3 areas to focus on
    }

# Navigation functions
def go_to_page(page):
    st.session_state.current_page = page

def go_to_section(section_idx):
    if section_idx < 0:
        section_idx = 0
    if section_idx >= len(sections):
        # Completed all sections
        st.session_state.assessment_complete = True
        st.session_state.results = calculate_compliance_score()
        go_to_page('report')
        return
    
    st.session_state.current_section = section_idx
    go_to_page('assessment')

def save_response(section_idx, question_idx, response):
    key = f"s{section_idx}_q{question_idx}"
    st.session_state.responses[key] = response

# Application header
def render_header():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔒 DPDP Compliance Assessment Tool")
    with col2:
        st.write("")
        st.write("")
        if st.session_state.current_page != 'welcome':
            if st.button("Start New Assessment", type="primary"):
                # Reset session state
                st.session_state.responses = {}
                st.session_state.assessment_complete = False
                st.session_state.results = None
                st.session_state.current_section = 0
                st.session_state.organization_name = ""
                st.session_state.assessment_date = datetime.now().strftime("%Y-%m-%d")
                go_to_page('welcome')

# Sidebar navigation
def render_sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/data-protection.png", width=100)
        st.title("Navigation")
        
        if st.button("Dashboard", use_container_width=True):
            go_to_page('dashboard')
        
        if st.button("Start Assessment", use_container_width=True):
            if not st.session_state.organization_name:
                go_to_page('welcome')
            else:
                go_to_page('assessment')
                
        if st.button("View Report", use_container_width=True):
            if st.session_state.assessment_complete:
                go_to_page('report')
            else:
                st.sidebar.warning("Complete the assessment first to view the report")
                
        if st.button("Recommendations", use_container_width=True):
            if st.session_state.assessment_complete:
                go_to_page('recommendations')
            else:
                st.sidebar.warning("Complete the assessment first to view recommendations")
        
        st.divider()
        if st.session_state.organization_name:
            st.write(f"**Organization:** {st.session_state.organization_name}")
            st.write(f"**Assessment Date:** {st.session_state.assessment_date}")
            
            # Display progress
            if st.session_state.current_page == 'assessment':
                progress = st.session_state.current_section / len(sections)
                st.progress(progress)
                st.write(f"Section {st.session_state.current_section + 1} of {len(sections)}")

# Welcome page
def render_welcome_page():
    st.header("Welcome to the DPDP Compliance Assessment Tool")
    st.write("""
    This tool helps you assess your organization's compliance with the Digital Personal Data Protection (DPDP) Act.
    The assessment covers ten key areas of compliance and provides a detailed report with recommendations.
    """)
    
    st.subheader("Before you begin")
    st.write("""
    You'll be asked a series of questions across multiple sections. The assessment takes approximately 20-30 minutes to complete.
    Your responses will be used to calculate compliance scores and generate tailored recommendations.
    """)
    
    with st.form("organization_form"):
        st.subheader("Organization Information")
        org_name = st.text_input("Organization Name", key="org_name_input")
        assessment_date = st.date_input("Assessment Date", value=datetime.now())
        
        submitted = st.form_submit_button("Begin Assessment", type="primary")
        if submitted and org_name:
            st.session_state.organization_name = org_name
            st.session_state.assessment_date = assessment_date.strftime("%Y-%m-%d")
            go_to_section(0)
            st.rerun()

# Dashboard page
def render_dashboard():
    st.header("DPDP Compliance Dashboard")
    
    if not st.session_state.assessment_complete:
        st.info("Complete the assessment to view your compliance dashboard")
        if st.button("Start Assessment", type="primary"):
            if not st.session_state.organization_name:
                go_to_page('welcome')
            else:
                go_to_section(0)
        return
    
    results = st.session_state.results
    
    # Create dashboard layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Overall score gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=results["overall_score"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Compliance"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "red"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 90], 'color': "lightgreen"},
                    {'range': [90, 100], 'color': "green"},
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': results["overall_score"]
                }
            }
        ))
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Compliance Level")
        st.write(f"**{results['compliance_level']}**")
        
        # High risk areas
        if results["high_risk_areas"]:
            st.subheader("High Risk Areas")
            for area in results["high_risk_areas"]:
                score = results["section_scores"][area] * 100
                st.error(f"• {area} ({score:.1f}%)")
    
    with col2:
        # Section scores
        st.subheader("Section Compliance Scores")
        
        # Create dataframe for section scores
        section_data = []
        for section, score in results["section_scores"].items():
            if score is not None:
                section_data.append({
                    "Section": section,
                    "Score": score * 100
                })
        
        df = pd.DataFrame(section_data)
        df = df.sort_values("Score")
        
        # Create horizontal bar chart
        fig = px.bar(
            df, 
            x="Score", 
            y="Section", 
            orientation='h',
            color="Score",
            color_continuous_scale=["red", "orange", "lightgreen", "green"],
            range_color=[0, 100]
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Action Items
    st.subheader("Recommended Actions")
    if results["improvement_priorities"]:
        for i, area in enumerate(results["improvement_priorities"]):
            with st.expander(f"Priority {i+1}: {area}"):
                if area in results["recommendations"] and results["recommendations"][area]:
                    for rec in results["recommendations"][area]:
                        st.write(f"• {rec}")
                else:
                    st.write("No specific recommendations available for this area.")
# Continuing from the previous code...
# Continuing from the previous code...

# Assessment page (continued)
def render_assessment():
    if st.session_state.current_section >= len(sections):
        st.session_state.assessment_complete = True
        st.session_state.results = calculate_compliance_score()
        go_to_page('report')
        return
    
    section = sections[st.session_state.current_section]
    st.header(f"Section: {section['name']}")
    
    # Progress bar
    progress = st.session_state.current_section / len(sections)
    st.progress(progress)
    
    # Display questions
    for q_idx, question in enumerate(section["questions"]):
        st.subheader(f"Question {q_idx + 1}")
        st.write(question)
        
        # Get current response if any
        current_response = st.session_state.responses.get(f"s{st.session_state.current_section}_q{q_idx}", None)
        
        # Display options as radio buttons
        options = section["options"][q_idx]
        response = st.radio(
            "Select your answer:",
            options,
            key=f"radio_{st.session_state.current_section}_{q_idx}",
            index=options.index(current_response) if current_response in options else None
        )
        
        # Save response when selected
        if response:
            save_response(st.session_state.current_section, q_idx, response)
        
        st.divider()
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.current_section > 0:
            if st.button("Previous Section"):
                go_to_section(st.session_state.current_section - 1)
    
    with col3:
        if st.button("Next Section", type="primary"):
            # Check if all questions in current section are answered
            all_answered = True
            for q_idx in range(len(section["questions"])):
                key = f"s{st.session_state.current_section}_q{q_idx}"
                if key not in st.session_state.responses:
                    all_answered = False
            
            if all_answered:
                go_to_section(st.session_state.current_section + 1)
            else:
                st.error("Please answer all questions before proceeding.")

# Report page
def render_report():
    if not st.session_state.assessment_complete:
        st.info("Complete the assessment to view your compliance report")
        if st.button("Start Assessment", type="primary"):
            if not st.session_state.organization_name:
                go_to_page('welcome')
            else:
                go_to_section(0)
        return
    
    results = st.session_state.results
    
    st.header("DPDP Compliance Report")
    st.subheader(f"For: {st.session_state.organization_name}")
    st.write(f"Assessment Date: {st.session_state.assessment_date}")
    
    # Summary section
    st.markdown(f"""
    ### Overall Compliance: {results['overall_score']:.1f}% - {results['compliance_level']}
    
    This report provides a detailed assessment of your organization's compliance with the DPDP Act
    across ten key areas. Review the section scores and recommendations below to identify areas
    for improvement.
    """)
    
    # Section scores table
    st.subheader("Section Compliance Scores")
    
    # Create dataframe for section scores
    section_data = []
    for section in sections:
        section_name = section["name"]
        if section_name in results["section_scores"] and results["section_scores"][section_name] is not None:
            score = results["section_scores"][section_name] * 100
            section_data.append({
                "Section": section_name,
                "Score (%)": f"{score:.1f}%",
                "Weight": f"{section['weight'] * 100:.1f}%",
                "Status": "High Risk" if score < 60 else ("Moderate Risk" if score < 75 else "Compliant")
            })
    
    df = pd.DataFrame(section_data)
    st.dataframe(df, use_container_width=True)
    
    # Key findings
    st.subheader("Key Findings")
    
    # Strengths
    strengths = [
        section for section, score in results["section_scores"].items() 
        if score is not None and score >= 0.75
    ]
    
    if strengths:
        st.write("**Strengths:**")
        for strength in strengths[:3]:  # Top 3 strengths
            score = results["section_scores"][strength] * 100
            st.success(f"• {strength} ({score:.1f}%)")
    
    # Areas for improvement
    if results["high_risk_areas"]:
        st.write("**Areas for Improvement:**")
        for area in results["high_risk_areas"]:
            score = results["section_scores"][area] * 100
            st.error(f"• {area} ({score:.1f}%)")
    
    # Export options
    st.subheader("Export Report")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export as PDF"):
            st.info("PDF export functionality would be implemented here.")
    with col2:
        if st.button("Export as CSV"):
            st.info("CSV export functionality would be implemented here.")
    
    # Navigation buttons
    if st.button("View Detailed Recommendations", type="primary"):
        go_to_page('recommendations')

# Recommendations page
def render_recommendations():
    if not st.session_state.assessment_complete:
        st.info("Complete the assessment to view recommendations")
        if st.button("Start Assessment", type="primary"):
            if not st.session_state.organization_name:
                go_to_page('welcome')
            else:
                go_to_section(0)
        return
    
    results = st.session_state.results
    
    st.header("Detailed Recommendations")
    st.write("Based on your assessment, we recommend the following actions to improve DPDP compliance:")
    
    # Display recommendations by section
    for section in sections:
        section_name = section["name"]
        if section_name in results["recommendations"] and results["recommendations"][section_name]:
            with st.expander(f"{section_name}"):
                score = results["section_scores"].get(section_name, 0)
                if score is not None:
                    score_percentage = score * 100
                    st.write(f"Current compliance score: {score_percentage:.1f}%")
                
                st.write("**Recommended Actions:**")
                for rec in results["recommendations"][section_name]:
                    st.write(f"• {rec}")
                
                # Add some generic guidance based on section
                if section_name == "Consent Management":
                    st.write("""
                    **Additional Guidance:**
                    - Review and update all consent forms and notices
                    - Test consent mechanisms with users to ensure clarity
                    - Document your consent processes and justifications
                    """)
                elif section_name == "Data Breach Management":
                    st.write("""
                    **Additional Guidance:**
                    - Create a dedicated breach response team with clear roles
                    - Conduct regular breach simulation exercises
                    - Document all breach notification templates and procedures
                    """)
    
    # Priority action plan
    st.subheader("Priority Action Plan")
    st.write("Focus on these areas first to significantly improve your compliance:")
    
    for i, area in enumerate(results["improvement_priorities"][:3]):
        st.write(f"**Priority {i+1}: {area}**")
        if area in results["recommendations"] and results["recommendations"][area]:
            for rec in results["recommendations"][area][:3]:  # Top 3 recommendations
                st.write(f"• {rec}")
    
    # Resources
    st.subheader("Helpful Resources")
    st.write("""
    - [DPDP Act Official Website](https://digitalindia.gov.in/)
    - [Official DPDP Act Guidelines](https://digitalindia.gov.in/)
    - [DPDP Compliance Checklist](https://digitalindia.gov.in/)
    - [Contact a DPDP Compliance Expert](mailto:info@dpdpcompliance.com)
    """)

# Main app logic
def main():
    # Render header
    render_header()
    
    # Render sidebar
    render_sidebar()
    
    # Render current page
    if st.session_state.current_page == 'welcome':
        render_welcome_page()
    elif st.session_state.current_page == 'dashboard':
        render_dashboard()
    elif st.session_state.current_page == 'assessment':
        render_assessment()
    elif st.session_state.current_page == 'report':
        render_report()
    elif st.session_state.current_page == 'recommendations':
        render_recommendations()

if __name__ == "__main__":
    main()