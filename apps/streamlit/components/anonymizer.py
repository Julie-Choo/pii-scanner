# apps/streamlit/components/anonymizer.py
"""
Text anonymization UI component
"""

import streamlit as st
from pii_scanner import ScanOptions

def render_anonymizer(scanner, confidence_threshold):
    """Render text anonymization interface"""
    
    st.header("🎭 Text Anonymizer")
    st.write("Replace PII in text with anonymized versions")
    
    # Sample texts for anonymization
    sample_texts = {
        "Email Example": "Please contact John Doe at john.doe@company.com for more information.",
        "Contact Info": "Call me at (555) 123-4567 or email me at alice@email.com",
        "Personal Data": "My SSN is 123-45-6789 and I live at 123 Main St, Anytown, NY",
        "Customer Record": "Customer Jane Smith (jane.smith@email.com) called from (555) 987-6543",
        "Custom": ""
    }
    
    # Sample selection
    sample_choice = st.selectbox(
        "Quick Examples:",
        list(sample_texts.keys()),
        help="Select a sample text or choose 'Custom' to enter your own"
    )
    
    # Text input
    text_to_anonymize = st.text_area(
        "Enter text to anonymize:",
        value=sample_texts.get(sample_choice, ""),
        height=150,
        placeholder="Enter text containing PII that you want to anonymize...",
        help="All detected PII will be replaced with anonymized versions"
    )
    
    # Anonymization options
    with st.expander("Anonymization Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            show_detection_details = st.checkbox("Show Detection Details", value=True)
            preserve_format = st.checkbox("Preserve Text Format", value=True)
        
        with col2:
            anonymization_mode = st.selectbox(
                "Anonymization Mode:",
                ["Smart Masking", "Complete Replacement", "Consistent Hashing"],
                help="Different ways to anonymize the detected PII"
            )
    
    # Anonymize button
    if st.button("🎭 Anonymize Text", type="primary", use_container_width=True):
        if not text_to_anonymize.strip():
            st.warning("Please enter some text to anonymize")
            return
        
        with st.spinner("Anonymizing text..."):
            try:
                # Configure options
                options = ScanOptions(
                    confidence_threshold=confidence_threshold,
                    include_context=show_detection_details
                )
                
                # First, detect PII to show what will be anonymized
                scan_result = scanner.scan_text(text_to_anonymize, options)
                
                # Then anonymize the text
                anonymized_text = scanner.anonymize_text(text_to_anonymize, options)
                
                # Display results
                _display_anonymization_results(
                    text_to_anonymize, 
                    anonymized_text, 
                    scan_result, 
                    show_detection_details
                )
                
            except Exception as e:
                st.error(f"Error during anonymization: {str(e)}")

def _display_anonymization_results(original_text, anonymized_text, scan_result, show_details):
    """Display anonymization results"""
    
    st.success(f"✅ Anonymization complete! Found and anonymized {len(scan_result.matches)} PII entities.")
    
    # Side-by-side comparison
    st.subheader("Before and After")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Original Text:**")
        st.text_area(
            "", 
            value=original_text, 
            height=200, 
            disabled=True,
            key="original_display"
        )
    
    with col2:
        st.write("**Anonymized Text:**")
        st.text_area(
            "", 
            value=anonymized_text, 
            height=200, 
            disabled=True,
            key="anonymized_display"
        )
    
    # Copy anonymized text button
    if st.button("📋 Copy Anonymized Text", help="Copy to clipboard"):
        # Use JavaScript to copy to clipboard
        st.write("Anonymized text is ready to copy from the text area above")
    
    # Show detection details if requested
    if show_details and scan_result.matches:
        st.subheader("What Was Anonymized")
        
        # Summary of changes
        entity_counts = {}
        for match in scan_result.matches:
            entity_counts[match.entity_type] = entity_counts.get(match.entity_type, 0) + 1
        
        for entity_type, count in entity_counts.items():
            st.write(f"• **{entity_type}:** {count} instance{'s' if count > 1 else ''} anonymized")
        
        # Detailed changes table
        with st.expander("Detailed Changes"):
            import pandas as pd
            
            table_data = []
            for match in scan_result.matches:
                table_data.append({
                    "Entity Type": match.entity_type,
                    "Original": match.text,
                    "Anonymized": match.anonymized_text,
                    "Confidence": f"{match.confidence:.1%}",
                    "Position": f"{match.start}-{match.end}"
                })
            
            if table_data:
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True)
    
    # Download options
    st.subheader("Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.download_button(
            label="📥 Download Anonymized Text",
            data=anonymized_text,
            file_name="anonymized_text.txt",
            mime="text/plain"
        ):
            st.success("Download started!")
    
    with col2:
        if scan_result.matches and st.download_button(
            label="📊 Download Report (JSON)",
            data=scan_result.to_dict().__str__(),
            file_name="pii_report.json", 
            mime="application/json"
        ):
            st.success("Report downloaded!")