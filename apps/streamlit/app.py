# apps/streamlit/app.py
"""
Main Streamlit application for PII scanning
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import streamlit as st
from components.text_scanner import render_text_scanner
from components.file_scanner import render_file_scanner
from components.anonymizer import render_anonymizer
from utils import setup_streamlit_config, get_app_scanner

def main():
    """Main Streamlit application"""
    
    # Setup page config
    setup_streamlit_config()
    
    # Initialize scanner
    scanner = get_app_scanner()
    
    # Main title
    st.title("🔍 PII Scanner")
    st.markdown("**Detect and anonymize personally identifiable information**")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/4ECDC4/FFFFFF?text=PII+Scanner", 
                width=200)
        
        st.markdown("### Navigation")
        tab_selection = st.radio(
            "Choose a tool:",
            ["Text Scanner", "File Scanner", "Text Anonymizer"],
            index=0
        )
        
        # Scanner status
        st.markdown("---")
        st.markdown("### Status")
        if scanner and scanner.is_ready():
            st.success("✅ Scanner Ready")
        else:
            st.error("❌ Scanner Not Ready")
        
        st.markdown("### Settings")
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0, 
            value=0.5,
            step=0.1,
            help="Minimum confidence for PII detection"
        )
    
    # Main content area
    if tab_selection == "Text Scanner":
        render_text_scanner(scanner, confidence_threshold)
    elif tab_selection == "File Scanner":
        render_file_scanner(scanner, confidence_threshold)
    elif tab_selection == "Text Anonymizer":
        render_anonymizer(scanner, confidence_threshold)

if __name__ == "__main__":
    main()