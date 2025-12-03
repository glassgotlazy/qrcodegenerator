import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, RoundedModuleDrawer, SquareModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
import base64
from io import BytesIO
import validators

# ENHANCED PAGE CONFIGURATION FOR SEO
st.set_page_config(
    page_title="Free QR Code Generator - Create Custom QR Codes Online | URL, Image, vCard",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/qr-generator',
        'Report a bug': 'https://github.com/yourusername/qr-generator/issues',
        'About': """
        # Ultimate QR Code Generator
        Create beautiful, customized QR codes for free!
        
        **Features:**
        - Generate QR codes for URLs, images, files, text, and vCards
        - 10+ beautiful color themes
        - Custom logo support
        - Multiple styles (Square, Circle, Rounded, Gapped)
        - Error correction levels
        - High-quality PNG downloads
        
        Made with ❤️ using Streamlit
        """
    }
)

# SEO Meta Tags using HTML
st.markdown("""
<meta name="description" content="Free online QR code generator. Create custom QR codes for URLs, images, PDFs, text, and vCards. Choose from 10+ color themes, add logos, and download high-quality PNG files. No registration required.">
<meta name="keywords" content="QR code generator, free QR code, custom QR code, QR code maker, URL QR code, image QR code, vCard QR code, QR code with logo, colored QR code, online QR generator">
<meta name="author" content="Your Name">
<meta name="robots" content="index, follow">
<meta property="og:title" content="Free QR Code Generator - Create Custom QR Codes Online">
<meta property="og:description" content="Generate beautiful, customized QR codes for URLs, images, files, text, and vCards. 10+ color themes, logo support, and instant downloads.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://your-app-name.streamlit.app">
<meta property="og:image" content="https://your-app-name.streamlit.app/preview-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Free QR Code Generator">
<meta name="twitter:description" content="Create stunning custom QR codes instantly. Free, easy, and beautiful.">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="https://your-app-name.streamlit.app">
""", unsafe_allow_html=True)

# Custom CSS for appealing styling (keeping your existing CSS)
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Enhanced background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Download button */
    .stDownloadButton>button {
        width: 100%;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 0.7rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        color: #495057;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Success animation */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        animation: slideIn 0.5s ease;
    }
    
    /* SEO-friendly headings */
    h1, h2, h3 {
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# SEO-friendly structured content
st.markdown('<h1 class="main-title">🎨 Free QR Code Generator Online</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Create stunning, customized QR codes instantly - No registration required!</p>', unsafe_allow_html=True)

# Add SEO-friendly content section
with st.expander("ℹ️ What is a QR Code Generator?", expanded=False):
    st.markdown("""
    ## About This Free QR Code Generator
    
    A **QR code (Quick Response code)** is a two-dimensional barcode that can store various types of information. 
    Our free online QR code generator helps you create customized, high-quality QR codes for:
    
    - **Website URLs** - Direct users to any webpage instantly
    - **Images** - Embed photos in scannable QR codes
    - **PDF Files** - Share documents via QR codes
    - **Plain Text** - Encode messages, WiFi passwords, or any text
    - **Contact Information (vCard)** - Digital business cards that save automatically
    
    ### Why Use Our QR Code Generator?
    
    ✅ **100% Free** - No hidden fees or subscriptions  
    ✅ **No Registration** - Start creating immediately  
    ✅ **Customizable** - 10+ color themes and 4 different styles  
    ✅ **Logo Support** - Add your brand logo to QR codes  
    ✅ **High Quality** - Download as PNG for printing  
    ✅ **Privacy First** - All processing happens in your browser  
    
    ### How to Create a QR Code:
    
    1. Choose your QR code type (URL, Image, File, Text, or vCard)
    2. Enter your data or upload your file
    3. Customize colors, style, and add a logo (optional)
    4. Click "Generate" and download your QR code
    5. Print or share your custom QR code!
    
    Perfect for businesses, restaurants, events, marketing materials, product packaging, and personal use.
    """)

# [REST OF YOUR EXISTING CODE CONTINUES HERE...]
# (Keep all your existing code for color presets, sidebar, tabs, functions, etc.)
