# apps/streamlit/components/text_scanner.py
"""
Text scanning UI component
"""

import streamlit as st
import pandas as pd
from pii_scanner import ScanOptions

def render_text_scanner(scanner, confidence_threshold):
    """Render text scanning interface"""
    
    st.header("📝 Text PII Scanner")
    st.write("Scan any text for personally identifiable information")
    
    # Sample text for quick testing
    sample_texts = {
        "Contact Info": """John Smith
Email: john.smith@company.com
Phone: (555) 123-4567
SSN: 123-45-6789""",
        
        "Customer Data": """Customer: Jane Doe
Contact: jane.doe@email.com
Phone: 555-987-6543
Address: 123 Main St, Anytown, NY 12345""",
        
        "Employee Record": """Employee ID: EMP001
Name: Bob Johnson  
Email: bob.johnson@company.com
Phone: (555) 456-7890
Emergency Contact: (555) 111-2222""",
        
        "Custom": ""
    }
    
    # Sample text selection
    col1, col2 = st.columns([1, 3])
    
    with col1:
        sample_choice = st.selectbox(
            "Quick Examples:",
            list(sample_texts.keys()),
            help="Select a sample text or choose 'Custom' to enter your own"
        )
    
    # Text input
    text_input = st.text_area(
        "Enter text to scan:",
        value=sample_texts.get(sample_choice, ""),
        height=150,
        placeholder="Enter or paste text that may contain PII...",
        help="The scanner will analyze this text for various types of PII"
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_context = st.checkbox("Include Context", value=True)
            context_window = st.number_input(
                "Context Window Size", 
                min_value=10, 
                max_value=200, 
                value=50
            )
        
        with col2:
            entity_filter = st.multiselect(
                "Entity Types to Detect:",
                options=[
                    "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", 
                    "CREDIT_CARD", "PERSON", "LOCATION", "IP_ADDRESS"
                ],
                default=["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "CREDIT_CARD", "PERSON"],
                help="Select which types of PII to detect"
            )
    
    # Scan button
    if st.button("🔍 Scan for PII", type="primary", use_container_width=True):
        if not text_input.strip():
            st.warning("Please enter some text to scan")
            return
        
        # Show spinner while processing
        with st.spinner("Scanning for PII..."):
            try:
                # Configure scan options
                options = ScanOptions(
                    confidence_threshold=confidence_threshold,
                    entity_types=entity_filter,
                    include_context=include_context,
                    context_window=context_window
                )
                
                # Perform scan
                result = scanner.scan_text(text_input, options)
                
                # Display results
                if result.matches:
                    _display_scan_results(result, text_input)
                else:
                    st.success("✅ No PII detected in the text!")
                    
            except Exception as e:
                st.error(f"Error during scanning: {str(e)}")

def _display_scan_results(result, original_text):
    """Display scan results in organized format"""
    
    st.success(f"🚨 Found {result.total_entities} PII entities")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    summary = result.get_summary()
    
    with col1:
        st.metric("Total PII", result.total_entities)
    with col2:
        st.metric("Entity Types", len(summary["entity_counts"]))
    with col3:
        st.metric("Avg Confidence", f"{summary['average_confidence']:.1%}")
    with col4:
        high_conf = summary["confidence_distribution"]["high"]
        st.metric("High Confidence", high_conf)
    
    # Detailed results table
    st.subheader("Detailed Results")
    
    # Prepare data for table
    table_data = []
    for match in result.matches:
        table_data.append({
            "Entity Type": match.entity_type,
            "Original Text": match.text,
            "Anonymized": match.anonymized_text,
            "Confidence": f"{match.confidence:.1%}",
            "Position": f"{match.start}-{match.end}",
            "Context": match.context[:100] + "..." if len(match.context) > 100 else match.context
        })
    
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
    
    # Entity distribution chart
    if len(summary["entity_counts"]) > 1:
        st.subheader("PII Distribution")
        entity_df = pd.DataFrame([
            {"Entity Type": k, "Count": v} 
            for k, v in summary["entity_counts"].items()
        ])
        st.bar_chart(entity_df.set_index("Entity Type"))
    
    # Show anonymized text preview
    with st.expander("View Anonymized Text"):
        try:
            anonymized = scanner.anonymize_text(original_text)
            st.text_area("Anonymized version:", value=anonymized, height=150, disabled=True)
        except Exception as e:
            st.error(f"Error creating anonymized version: {e}")