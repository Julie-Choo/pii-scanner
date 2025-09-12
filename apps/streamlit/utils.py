# apps/streamlit/utils.py
"""
Streamlit utilities and helpers
"""

import streamlit as st
from pii_scanner import get_scanner, PIIScanner

def setup_streamlit_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="PII Scanner",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1rem;
            color: #1f77b4;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .success-alert {
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border-left: 5px solid #28a745;
            background-color: #d4edda;
        }
        
        .warning-alert {
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            border-left: 5px solid #ffc107;
            background-color: #fff3cd;
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_app_scanner() -> PIIScanner:
    """Get cached scanner instance for Streamlit app"""
    try:
        return get_scanner()
    except Exception as e:
        st.error(f"Failed to initialize PII scanner: {e}")
        return None

def format_confidence(confidence: float) -> str:
    """Format confidence score with color coding"""
    if confidence >= 0.8:
        return f"🟢 {confidence:.1%}"
    elif confidence >= 0.6:
        return f"🟡 {confidence:.1%}"
    else:
        return f"🔴 {confidence:.1%}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def show_scanner_status(scanner: PIIScanner):
    """Show scanner status in sidebar"""
    if scanner and scanner.is_ready():
        st.sidebar.success("✅ Scanner Ready")
        
        # Show supported entities count
        try:
            entities = scanner.get_supported_entities()
            st.sidebar.info(f"📋 {len(entities)} entity types supported")
        except:
            pass
    else:
        st.sidebar.error("❌ Scanner Not Ready")
        st.sidebar.write("Please check your installation:")
        st.sidebar.code("pip install presidio-analyzer presidio-anonymizer spacy")
        st.sidebar.code("python -m spacy download en_core_web_sm")