# apps/streamlit/components/file_scanner.py
"""
File scanning UI component
"""

import streamlit as st
import pandas as pd
import tempfile
import os
from pii_scanner import ScanOptions, FileInfo
from pii_scanner.file_handlers import FileHandlerFactory

def render_file_scanner(scanner, confidence_threshold):
    """Render file scanning interface"""
    
    st.header("📁 File PII Scanner")
    st.write("Upload and scan files for personally identifiable information")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose files to scan:",
        type=['txt', 'csv', 'json', 'log', 'md'],
        accept_multiple_files=True,
        help="Supported formats: TXT, CSV, JSON, LOG, MD"
    )
    
    if not uploaded_files:
        # Show supported formats
        st.info("📋 **Supported File Formats:**")
        col1, col2 = st.columns(2)
        with col1:
            st.write("• **Text files:** .txt, .log, .md")
            st.write("• **Data files:** .csv, .json")
        with col2:
            st.write("• **Code files:** .py, .js, .html")
            st.write("• **Configuration:** .yaml, .xml")
        return
    
    # Scan configuration
    with st.expander("Scan Configuration"):
        col1, col2 = st.columns(2)
        
        with col1:
            include_context = st.checkbox("Include Context", value=True)
            entity_types = st.multiselect(
                "Entity Types:",
                ["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "CREDIT_CARD", "PERSON"],
                default=["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "CREDIT_CARD", "PERSON"]
            )
        
        with col2:
            context_window = st.number_input("Context Window", min_value=10, max_value=200, value=50)
            max_file_size = st.number_input("Max File Size (MB)", min_value=1, max_value=100, value=10)
    
    # Display uploaded files info
    st.subheader("Uploaded Files")
    for i, uploaded_file in enumerate(uploaded_files):
        with st.expander(f"📄 {uploaded_file.name} ({uploaded_file.size:,} bytes)"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Name:** {uploaded_file.name}")
                st.write(f"**Size:** {uploaded_file.size:,} bytes")
            with col2:
                st.write(f"**Type:** {uploaded_file.type}")
                # Show file preview for small text files
                if uploaded_file.size < 1000 and uploaded_file.name.endswith(('.txt', '.log')):
                    content = str(uploaded_file.read(500), 'utf-8', errors='ignore')
                    st.text_area("Preview:", content[:200] + "..." if len(content) > 200 else content, height=100, disabled=True)
                    uploaded_file.seek(0)  # Reset file pointer
    
    # Scan button
    if st.button("🔍 Scan All Files", type="primary", use_container_width=True):
        _scan_uploaded_files(uploaded_files, scanner, confidence_threshold, 
                            entity_types, include_context, context_window, max_file_size)

def _scan_uploaded_files(uploaded_files, scanner, confidence_threshold, 
                        entity_types, include_context, context_window, max_file_size):
    """Scan uploaded files and display results"""
    
    # Create file handler factory
    file_factory = FileHandlerFactory(scanner)
    
    # Configure scan options
    options = ScanOptions(
        confidence_threshold=confidence_threshold,
        entity_types=entity_types,
        include_context=include_context,
        context_window=context_window
    )
    
    all_results = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Scanning {uploaded_file.name}...")
        
        # Check file size
        if uploaded_file.size > max_file_size * 1024 * 1024:
            st.warning(f"Skipping {uploaded_file.name}: File too large ({uploaded_file.size:,} bytes)")
            continue
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Create file info
            file_info = FileInfo.from_path(tmp_path)
            file_info.name = uploaded_file.name  # Use original name
            
            # Get appropriate handler
            try:
                handler = file_factory.get_handler(file_info)
                result = handler.scan_file(file_info, options)
                
                if result.matches:
                    all_results[uploaded_file.name] = result
                
            except Exception as handler_error:
                st.error(f"Error scanning {uploaded_file.name}: {handler_error}")
        
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass
        
        # Update progress
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Display results
    _display_file_scan_results(all_results)

def _display_file_scan_results(results):
    """Display file scanning results"""
    
    if not results:
        st.success("✅ No PII detected in any uploaded files!")
        return
    
    # Overall summary
    total_files = len(results)
    total_entities = sum(len(result.matches) for result in results.values())
    
    st.success(f"🚨 Found PII in {total_files} files ({total_entities} total entities)")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Files with PII", total_files)
    with col2:
        st.metric("Total Entities", total_entities)
    with col3:
        avg_per_file = total_entities / total_files if total_files > 0 else 0
        st.metric("Avg per File", f"{avg_per_file:.1f}")
    
    # Results by file
    st.subheader("Results by File")
    
    for file_name, result in results.items():
        with st.expander(f"📄 {file_name} ({len(result.matches)} entities found)"):
            
            # File summary
            summary = result.get_summary()
            st.write(f"**Processing Time:** {summary['processing_time_ms']:.1f}ms")
            st.write(f"**Entity Types Found:** {', '.join(summary['entity_counts'].keys())}")
            
            # Detailed results table
            if result.matches:
                table_data = []
                for match in result.matches:
                    table_data.append({
                        "Entity Type": match.entity_type,
                        "Text": match.text,
                        "Anonymized": match.anonymized_text,
                        "Confidence": f"{match.confidence:.1%}",
                        "Location": match.location,
                        "Context": match.context[:100] + "..." if len(match.context) > 100 else match.context
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True)