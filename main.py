import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, RoundedModuleDrawer, SquareModuleDrawer, GappedSquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
import base64
from io import BytesIO
import validators

# Page configuration
st.set_page_config(
    page_title="Ultimate QR Code Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for cool styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Download button */
    .stDownloadButton>button {
        width: 100%;
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 10px;
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
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🎨 Ultimate QR Code Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Create stunning, customized QR codes for anything!</p>', unsafe_allow_html=True)

# Sidebar for customization
with st.sidebar:
    st.header("🎨 Customization Options")
    
    # QR Code Style
    st.subheader("Style")
    qr_style = st.selectbox(
        "Module Style",
        ["Square", "Circle", "Rounded", "Gapped Square"],
        help="Choose the shape of QR code modules"
    )
    
    # Color customization
    st.subheader("Colors")
    col1, col2 = st.columns(2)
    with col1:
        fg_color = st.color_picker("Foreground", "#000000", help="Main QR code color")
    with col2:
        bg_color = st.color_picker("Background", "#FFFFFF", help="Background color")
    
    # Size settings
    st.subheader("Size")
    box_size = st.slider("Box Size", 5, 30, 10, help="Size of each QR module")
    border = st.slider("Border", 1, 10, 4, help="Border thickness")
    
    # Error correction
    st.subheader("Error Correction")
    error_correction = st.select_slider(
        "Level",
        options=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
        value="M (15%)",
        help="Higher = more damage resistance but larger QR code"
    )
    
    # Logo upload
    st.subheader("Logo (Optional)")
    logo_file = st.file_uploader("Add Logo to Center", type=['png', 'jpg', 'jpeg'], help="Will be resized automatically")

# Map error correction
error_map = {
    "L (7%)": qrcode.constants.ERROR_CORRECT_L,
    "M (15%)": qrcode.constants.ERROR_CORRECT_M,
    "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
    "H (30%)": qrcode.constants.ERROR_CORRECT_H
}

# Map styles to drawers
style_map = {
    "Square": SquareModuleDrawer(),
    "Circle": CircleModuleDrawer(),
    "Rounded": RoundedModuleDrawer(),
    "Gapped Square": GappedSquareModuleDrawer()
}

# Main content - Tabs for different QR types
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔗 URL/Link", "📸 Image", "📄 File/PDF", "✍️ Text", "📱 Contact/vCard"])

# Function to generate QR code
def generate_qr(data, style, fg, bg, box, bord, err_corr, logo=None):
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=err_corr,
            box_size=box,
            border=bord,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Convert hex colors to RGB
        fg_rgb = tuple(int(fg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        bg_rgb = tuple(int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        # Create styled QR code
        if logo:
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=style,
                color_mask=SolidFillColorMask(front_color=fg_rgb, back_color=bg_rgb),
                embeded_image_path=logo
            )
        else:
            qr_img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=style,
                color_mask=SolidFillColorMask(front_color=fg_rgb, back_color=bg_rgb)
            )
        
        return qr_img, qr.version
    except Exception as e:
        return None, str(e)

# TAB 1: URL/Link
with tab1:
    st.markdown("### 🔗 Generate QR for URL or Link")
    
    url_input = st.text_input(
        "Enter URL",
        placeholder="https://example.com",
        help="Enter any website URL or deep link"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if url_input:
            if validators.url(url_input):
                st.success("✅ Valid URL")
            else:
                st.warning("⚠️ URL may be invalid - QR will still be generated")
    
    with col2:
        generate_btn_url = st.button("🎨 Generate QR", key="gen_url", type="primary")
    
    if generate_btn_url and url_input:
        with st.spinner("Creating your stunning QR code..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                logo_path = "temp_logo.png"
                logo_img.save(logo_path)
            
            qr_img, version = generate_qr(
                url_input,
                style_map[qr_style],
                fg_color,
                bg_color,
                box_size,
                border,
                error_map[error_correction],
                logo_path
            )
            
            if qr_img:
                st.markdown('<div class="success-box">✨ QR Code Generated Successfully!</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(qr_img, caption=f"QR Code (Version {version})", use_container_width=True)
                
                with col2:
                    st.metric("QR Version", version)
                    st.metric("Modules", f"{17 + 4*version}×{17 + 4*version}")
                    
                    # Save and download
                    buf = BytesIO()
                    qr_img.save(buf, format="PNG")
                    st.download_button(
                        "⬇️ Download QR Code",
                        buf.getvalue(),
                        "qr_code_url.png",
                        "image/png"
                    )
            else:
                st.error(f"❌ Error: {version}")

# TAB 2: Image
with tab2:
    st.markdown("### 📸 Generate QR for Image")
    
    uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg', 'gif', 'webp'], key="img_upload")
    
    if uploaded_image:
        file_size_mb = uploaded_image.size / (1024 * 1024)
        st.image(uploaded_image, caption=f"Uploaded Image ({file_size_mb:.2f} MB)", use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            quality = st.slider("JPEG Quality", 10, 95, 50, help="Lower = smaller size")
        with col2:
            max_dim = st.slider("Max Dimension (px)", 200, 1000, 400, step=50)
        
        generate_btn_img = st.button("🎨 Generate QR", key="gen_img", type="primary")
        
        if generate_btn_img:
            with st.spinner("Processing image and creating QR code..."):
                # Process image
                img = Image.open(uploaded_image)
                
                # Resize
                w, h = img.size
                if w > max_dim or h > max_dim:
                    if w > h:
                        new_w, new_h = max_dim, int((max_dim / w) * h)
                    else:
                        new_h, new_w = max_dim, int((max_dim / h) * w)
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Convert to base64
                if img.mode == 'RGBA':
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                
                buf = BytesIO()
                img.save(buf, format="JPEG", optimize=True, quality=quality)
                img_bytes = buf.getvalue()
                img_b64 = base64.b64encode(img_bytes).decode()
                data_url = f'data:image/jpeg;base64,{img_b64}'
                
                encoded_kb = len(data_url) / 1024
                
                if encoded_kb > 2.9:
                    st.error(f"❌ Encoded size too large: {encoded_kb:.2f} KB. Reduce quality or dimensions!")
                else:
                    st.info(f"📊 Encoded size: {encoded_kb:.2f} KB")
                    
                    logo_path = None
                    if logo_file:
                        logo_img = Image.open(logo_file)
                        logo_path = "temp_logo.png"
                        logo_img.save(logo_path)
                    
                    qr_img, version = generate_qr(
                        data_url,
                        style_map[qr_style],
                        fg_color,
                        bg_color,
                        box_size,
                        border,
                        error_map[error_correction],
                        logo_path
                    )
                    
                    if qr_img:
                        st.markdown('<div class="success-box">✨ Image QR Code Generated!</div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.image(qr_img, use_container_width=True)
                        with col2:
                            buf = BytesIO()
                            qr_img.save(buf, format="PNG")
                            st.download_button(
                                "⬇️ Download QR",
                                buf.getvalue(),
                                "qr_code_image.png",
                                "image/png"
                            )
                    else:
                        st.error(f"❌ Error: {version}")

# TAB 3: File/PDF
with tab3:
    st.markdown("### 📄 Generate QR for File")
    st.info("⚠️ Files are base64 encoded. Keep files small (<100KB) for scannable QR codes.")
    
    uploaded_file = st.file_uploader("Upload File", type=['pdf', 'txt', 'doc', 'docx', 'xlsx', 'csv'], key="file_upload")
    
    if uploaded_file:
        file_size_kb = uploaded_file.size / 1024
        st.write(f"📁 **File:** {uploaded_file.name} ({file_size_kb:.2f} KB)")
        
        if file_size_kb > 100:
            st.warning("⚠️ File is large. QR code may be difficult to scan.")
        
        generate_btn_file = st.button("🎨 Generate QR", key="gen_file", type="primary")
        
        if generate_btn_file:
            with st.spinner("Encoding file..."):
                file_bytes = uploaded_file.read()
                file_b64 = base64.b64encode(file_bytes).decode()
                data_url = f'data:application/octet-stream;base64,{file_b64}'
                
                encoded_kb = len(data_url) / 1024
                
                if encoded_kb > 2.9:
                    st.error(f"❌ File too large after encoding: {encoded_kb:.2f} KB")
                else:
                    st.success(f"✅ Encoded size: {encoded_kb:.2f} KB")
                    
                    logo_path = None
                    if logo_file:
                        logo_img = Image.open(logo_file)
                        logo_path = "temp_logo.png"
                        logo_img.save(logo_path)
                    
                    qr_img, version = generate_qr(
                        data_url,
                        style_map[qr_style],
                        fg_color,
                        bg_color,
                        box_size,
                        border,
                        error_map[error_correction],
                        logo_path
                    )
                    
                    if qr_img:
                        st.markdown('<div class="success-box">✨ File QR Code Generated!</div>', unsafe_allow_html=True)
                        st.image(qr_img, use_container_width=True)
                        
                        buf = BytesIO()
                        qr_img.save(buf, format="PNG")
                        st.download_button(
                            "⬇️ Download QR",
                            buf.getvalue(),
                            "qr_code_file.png",
                            "image/png"
                        )
                    else:
                        st.error(f"❌ Error: {version}")

# TAB 4: Text
with tab4:
    st.markdown("### ✍️ Generate QR for Text")
    
    text_input = st.text_area(
        "Enter Text",
        placeholder="Type your message here...",
        height=150,
        help="Any text, message, or data"
    )
    
    if text_input:
        char_count = len(text_input)
        st.caption(f"Characters: {char_count}")
    
    generate_btn_text = st.button("🎨 Generate QR", key="gen_text", type="primary")
    
    if generate_btn_text and text_input:
        with st.spinner("Creating QR code..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                logo_path = "temp_logo.png"
                logo_img.save(logo_path)
            
            qr_img, version = generate_qr(
                text_input,
                style_map[qr_style],
                fg_color,
                bg_color,
                box_size,
                border,
                error_map[error_correction],
                logo_path
            )
            
            if qr_img:
                st.markdown('<div class="success-box">✨ Text QR Code Generated!</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(qr_img, use_container_width=True)
                with col2:
                    buf = BytesIO()
                    qr_img.save(buf, format="PNG")
                    st.download_button(
                        "⬇️ Download QR",
                        buf.getvalue(),
                        "qr_code_text.png",
                        "image/png"
                    )
            else:
                st.error(f"❌ Error: {version}")

# TAB 5: Contact/vCard
with tab5:
    st.markdown("### 📱 Generate vCard QR Code")
    st.info("Create a QR code that saves contact information to phone")
    
    with st.form("vcard_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
        
        with col2:
            phone = st.text_input("Phone Number")
            company = st.text_input("Company/Organization")
            website = st.text_input("Website")
        
        address = st.text_input("Address")
        notes = st.text_area("Notes", height=100)
        
        submit_vcard = st.form_submit_button("🎨 Generate vCard QR", type="primary")
    
    if submit_vcard:
        # Create vCard format
        vcard = f"""BEGIN:VCARD
VERSION:3.0
N:{last_name};{first_name};;;
FN:{first_name} {last_name}
ORG:{company}
TEL:{phone}
EMAIL:{email}
URL:{website}
ADR:;;{address};;;;
NOTE:{notes}
END:VCARD"""
        
        with st.spinner("Creating vCard QR code..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                logo_path = "temp_logo.png"
                logo_img.save(logo_path)
            
            qr_img, version = generate_qr(
                vcard,
                style_map[qr_style],
                fg_color,
                bg_color,
                box_size,
                border,
                error_map[error_correction],
                logo_path
            )
            
            if qr_img:
                st.markdown('<div class="success-box">✨ vCard QR Code Generated!</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(qr_img, use_container_width=True)
                    st.caption("Scan this to save contact to your phone!")
                
                with col2:
                    buf = BytesIO()
                    qr_img.save(buf, format="PNG")
                    st.download_button(
                        "⬇️ Download vCard QR",
                        buf.getvalue(),
                        f"vcard_{first_name}_{last_name}.png",
                        "image/png"
                    )
            else:
                st.error(f"❌ Error: {version}")

# Footer with instructions
st.markdown("---")
with st.expander("📚 How to Use"):
    st.markdown("""
    ### Features:
    - **5 QR Code Types**: URL, Image, File, Text, and vCard
    - **Custom Styling**: Choose from 4 different module styles
    - **Color Customization**: Pick any foreground and background colors
    - **Logo Support**: Add your brand logo to the center
    - **Error Correction**: Adjust damage resistance level
    - **High Quality**: Download in PNG format
    
    ### Tips:
    - **URLs**: Perfect for websites, social media, menus, etc.
    - **Images**: Keep under 2.9KB encoded (reduce quality/size)
    - **Files**: Best for small documents (<100KB)
    - **Text**: Great for messages, WiFi passwords, etc.
    - **vCard**: Share contact info that saves automatically
    
    ### Best Practices:
    - Higher error correction = better damage resistance but larger QR
    - For logos, use high error correction (Q or H)
    - Test QR codes before printing in large quantities
    - Use high contrast colors for better scanning
    """)

st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #6c757d;">🎨 Made with ❤️ using Streamlit | Designed for maximum flexibility & style</div>',
    unsafe_allow_html=True
)
