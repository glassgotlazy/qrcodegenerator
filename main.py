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

# Custom CSS for appealing styling
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
    
    /* Color preset buttons */
    .color-preset {
        display: inline-block;
        width: 50px;
        height: 50px;
        border-radius: 10px;
        margin: 5px;
        cursor: pointer;
        transition: transform 0.2s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .color-preset:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
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
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🎨 Ultimate QR Code Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Create stunning, customized QR codes for anything!</p>', unsafe_allow_html=True)

# Color presets - appealing combinations
COLOR_PRESETS = {
    "Classic": ("#000000", "#FFFFFF"),
    "Ocean Blue": ("#0066CC", "#E6F2FF"),
    "Forest Green": ("#1B5E20", "#E8F5E9"),
    "Royal Purple": ("#6A1B9A", "#F3E5F5"),
    "Sunset Orange": ("#E65100", "#FFF3E0"),
    "Cherry Red": ("#C62828", "#FFEBEE"),
    "Deep Teal": ("#00796B", "#E0F2F1"),
    "Navy Gold": ("#1A237E", "#FFF9C4"),
    "Elegant Black": ("#212121", "#F5F5F5"),
    "Vibrant Magenta": ("#AD1457", "#FCE4EC")
}

# Sidebar for customization
with st.sidebar:
    st.header("🎨 Customization Options")
    
    # Color Presets
    st.subheader("🌈 Color Themes")
    preset_choice = st.selectbox(
        "Quick Themes",
        list(COLOR_PRESETS.keys()),
        help="Choose a pre-designed color scheme"
    )
    
    if preset_choice:
        preset_fg, preset_bg = COLOR_PRESETS[preset_choice]
    else:
        preset_fg, preset_bg = "#000000", "#FFFFFF"
    
    # Custom colors
    st.subheader("Custom Colors")
    col1, col2 = st.columns(2)
    with col1:
        fg_color = st.color_picker("Foreground", preset_fg, help="Main QR code color")
    with col2:
        bg_color = st.color_picker("Background", preset_bg, help="Background color")
    
    # QR Code Style
    st.subheader("📐 Style")
    qr_style = st.selectbox(
        "Module Shape",
        ["Square", "Rounded", "Circle", "Gapped Square"],
        help="Choose the shape of QR code modules"
    )
    
    # Size settings
    st.subheader("📏 Size Settings")
    box_size = st.slider("Module Size", 5, 30, 10, help="Size of each QR module in pixels")
    border = st.slider("Border Width", 1, 10, 4, help="Border thickness around QR code")
    
    # Error correction
    st.subheader("🛡️ Error Correction")
    error_correction = st.select_slider(
        "Protection Level",
        options=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
        value="M (15%)",
        help="Higher = more damage resistance but larger QR code"
    )
    
    # Logo upload
    st.subheader("🖼️ Center Logo (Optional)")
    logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'], help="Add your brand logo")
    if logo_file:
        st.image(logo_file, caption="Logo Preview", width=100)

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

# Function to generate QR code with proper image handling
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
        
        # Convert to PIL Image and then to bytes for Streamlit
        # This fixes the display error
        if hasattr(qr_img, '_img'):
            pil_image = qr_img._img
        else:
            pil_image = qr_img
        
        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert to bytes
        img_buffer = BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        return img_bytes, qr.version, pil_image
    except Exception as e:
        return None, str(e), None

# Main content - Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔗 URL/Link", "📸 Image", "📄 File/PDF", "✍️ Text", "📱 Contact"])

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
        generate_btn_url = st.button("🎨 Generate", key="gen_url", type="primary")
    
    if generate_btn_url and url_input:
        with st.spinner("✨ Creating your QR code..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                logo_path = "temp_logo.png"
                logo_img.save(logo_path)
            
            img_bytes, version, pil_img = generate_qr(
                url_input,
                style_map[qr_style],
                fg_color,
                bg_color,
                box_size,
                border,
                error_map[error_correction],
                logo_path
            )
            
            if img_bytes:
                st.markdown('<div class="success-box">✨ QR Code Generated Successfully!</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(img_bytes, caption=f"QR Code (Version {version})", use_container_width=True)
                
                with col2:
                    st.metric("📊 QR Version", version)
                    st.metric("📐 Size", f"{17 + 4*version}×{17 + 4*version}")
                    
                    st.download_button(
                        "⬇️ Download PNG",
                        img_bytes,
                        "qr_code_url.png",
                        "image/png",
                        use_container_width=True
                    )
            else:
                st.error(f"❌ Error: {version}")

# TAB 2: Image
with tab2:
    st.markdown("### 📸 Generate QR for Image")
    
    uploaded_image = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg', 'gif', 'webp'], key="img_upload")
    
    if uploaded_image:
        file_size_mb = uploaded_image.size / (1024 * 1024)
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_image, caption=f"Original ({file_size_mb:.2f} MB)", use_container_width=True)
        
        with col2:
            st.subheader("⚙️ Compression")
            quality = st.slider("JPEG Quality", 10, 95, 50, help="Lower = smaller size")
            max_dim = st.slider("Max Dimension", 200, 1000, 400, step=50, help="Resize to fit")
        
        generate_btn_img = st.button("🎨 Generate", key="gen_img", type="primary", use_container_width=True)
        
        if generate_btn_img:
            with st.spinner("🔄 Processing image..."):
                # Process image
                img = Image.open(uploaded_image)
                
                # Resize
                w, h = img.size
                if w > max_dim or h > max_dim:
                    ratio = min(max_dim/w, max_dim/h)
                    new_w, new_h = int(w*ratio), int(h*ratio)
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    st.info(f"🔄 Resized to {new_w}×{new_h}")
                
                # Convert to base64
                if img.mode == 'RGBA':
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                
                buf = BytesIO()
                img.save(buf, format="JPEG", optimize=True, quality=quality)
                img_bytes_data = buf.getvalue()
                img_b64 = base64.b64encode(img_bytes_data).decode()
                data_url = f'data:image/jpeg;base64,{img_b64}'
                
                encoded_kb = len(data_url) / 1024
                
                if encoded_kb > 2.9:
                    st.error(f"❌ Too large: {encoded_kb:.2f} KB. Max: 2.9 KB. Reduce quality/size!")
                else:
                    st.success(f"✅ Encoded: {encoded_kb:.2f} KB")
                    
                    logo_path = None
                    if logo_file:
                        logo_img = Image.open(logo_file)
                        logo_path = "temp_logo.png"
                        logo_img.save(logo_path)
                    
                    img_bytes, version, pil_img = generate_qr(
                        data_url,
                        style_map[qr_style],
                        fg_color,
                        bg_color,
                        box_size,
                        border,
                        error_map[error_correction],
                        logo_path
                    )
                    
                    if img_bytes:
                        st.markdown('<div class="success-box">✨ Image QR Code Created!</div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.image(img_bytes, use_container_width=True)
                        with col2:
                            st.download_button(
                                "⬇️ Download",
                                img_bytes,
                                "qr_code_image.png",
                                "image/png",
                                use_container_width=True
                            )
                    else:
                        st.error(f"❌ Error: {version}")

# TAB 3: File/PDF
with tab3:
    st.markdown("### 📄 Generate QR for File")
    st.info("⚠️ Keep files small (<100KB) for scannable QR codes")
    
    uploaded_file = st.file_uploader("Upload File", type=['pdf', 'txt', 'doc', 'docx', 'xlsx', 'csv'], key="file_upload")
    
    if uploaded_file:
        file_size_kb = uploaded_file.size / 1024
        st.write(f"📁 **{uploaded_file.name}** ({file_size_kb:.2f} KB)")
        
        if file_size_kb > 100:
            st.warning("⚠️ Large file - QR may be difficult to scan")
        
        generate_btn_file = st.button("🎨 Generate", key="gen_file", type="primary", use_container_width=True)
        
        if generate_btn_file:
            with st.spinner("📦 Encoding file..."):
                file_bytes_data = uploaded_file.read()
                file_b64 = base64.b64encode(file_bytes_data).decode()
                data_url = f'data:application/octet-stream;base64,{file_b64}'
                
                encoded_kb = len(data_url) / 1024
                
                if encoded_kb > 2.9:
                    st.error(f"❌ File too large: {encoded_kb:.2f} KB. Max: 2.9 KB")
                else:
                    st.success(f"✅ Encoded: {encoded_kb:.2f} KB")
                    
                    logo_path = None
                    if logo_file:
                        logo_img = Image.open(logo_file)
                        logo_path = "temp_logo.png"
                        logo_img.save(logo_path)
                    
                    img_bytes, version, pil_img = generate_qr(
                        data_url,
                        style_map[qr_style],
                        fg_color,
                        bg_color,
                        box_size,
                        border,
                        error_map[error_correction],
                        logo_path
                    )
                    
                    if img_bytes:
                        st.markdown('<div class="success-box">✨ File QR Code Created!</div>', unsafe_allow_html=True)
                        st.image(img_bytes, use_container_width=True)
                        
                        st.download_button(
                            "⬇️ Download QR",
                            img_bytes,
                            "qr_code_file.png",
                            "image/png",
                            use_container_width=True
                        )
                    else:
                        st.error(f"❌ Error: {version}")

# TAB 4: Text
with tab4:
    st.markdown("### ✍️ Generate QR for Text")
    
    text_input = st.text_area(
        "Enter Your Text",
        placeholder="Type your message, WiFi password, or any text...",
        height=200,
        help="Any text content you want to encode"
    )
    
    if text_input:
        st.caption(f"📝 {len(text_input)} characters")
    
    generate_btn_text = st.button("🎨 Generate", key="gen_text", type="primary", use_container_width=True)
    
    if generate_btn_text and text_input:
        with st.spinner("✨ Creating QR code..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                logo_path = "temp_logo.png"
                logo_img.save(logo_path)
            
            img_bytes, version, pil_img = generate_qr(
                text_input,
                style_map[qr_style],
                fg_color,
                bg_color,
                box_size,
                border,
                error_map[error_correction],
                logo_path
            )
            
            if img_bytes:
                st.markdown('<div class="success-box">✨ Text QR Code Created!</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(img_bytes, use_container_width=True)
                with col2:
                    st.download_button(
                        "⬇️ Download",
                        img_bytes,
                        "qr_code_text.png",
                        "image/png",
                        use_container_width=True
                    )
            else:
                st.error(f"❌ Error: {version}")

# TAB 5: Contact/vCard
with tab5:
    st.markdown("### 📱 Generate Contact QR (vCard)")
    st.info("📲 Create a scannable business card!")
    
    with st.form("vcard_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="John")
            email = st.text_input("Email", placeholder="john@example.com")
            company = st.text_input("Company", placeholder="Tech Corp")
        
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Doe")
            phone = st.text_input("Phone", placeholder="+1234567890")
            website = st.text_input("Website", placeholder="https://example.com")
        
        address = st.text_input("Address", placeholder="123 Main St, City, Country")
        notes = st.text_area("Notes", placeholder="Additional info...", height=80)
        
        submit_vcard = st.form_submit_button("🎨 Generate vCard QR", type="primary", use_container_width=True)
    
    if submit_vcard and first_name and last_name:
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
        
        with st.spinner("📇 Creating vCard..."):
            logo_path = None
            if logo_file:
                logo_img = Image.open(logo_file)
                logo_path = "temp_logo.png"
                logo_img.save(logo_path)
            
            img_bytes, version, pil_img = generate_qr(
                vcard,
                style_map[qr_style],
                fg_color,
                bg_color,
                box_size,
                border,
                error_map[error_correction],
                logo_path
            )
            
            if img_bytes:
                st.markdown('<div class="success-box">✨ vCard QR Code Created!</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(img_bytes, use_container_width=True)
                    st.caption("📲 Scan to save contact instantly!")
                
                with col2:
                    st.download_button(
                        "⬇️ Download",
                        img_bytes,
                        f"vcard_{first_name}_{last_name}.png",
                        "image/png",
                        use_container_width=True
                    )
            else:
                st.error(f"❌ Error: {version}")
    elif submit_vcard:
        st.warning("⚠️ Please enter at least First Name and Last Name")

# Footer
st.markdown("---")
with st.expander("📚 User Guide & Tips"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎨 Features
        - **5 QR Types**: URL, Image, File, Text, vCard
        - **10 Color Themes**: Pre-designed appealing schemes
        - **4 Styles**: Square, Rounded, Circle, Gapped
        - **Logo Support**: Add your brand
        - **Error Correction**: 4 protection levels
        
        ### 💡 Best Practices
        - **URLs**: Perfect for menus, social media, websites
        - **Images**: Keep under 2.9KB (low quality/small size)
        - **Files**: Small documents only (<100KB)
        - **Text**: WiFi passwords, messages, notes
        - **vCard**: Digital business cards
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Pro Tips
        - Higher error correction = better scanning
        - Use high contrast colors (dark on light)
        - Test QR codes before printing
        - For logos, use Q or H error correction
        - Rounded/Circle styles look modern
        
        ### 🌈 Color Combinations
        - **Professional**: Classic, Elegant Black
        - **Creative**: Vibrant Magenta, Sunset Orange
        - **Trustworthy**: Ocean Blue, Navy Gold
        - **Natural**: Forest Green, Deep Teal
        - **Elegant**: Royal Purple, Cherry Red
        """)

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    border-radius: 10px; color: white; font-weight: 600;">
        🎨 Made with ❤️ using Streamlit | Beautiful, Fast, & Reliable QR Code Generator
    </div>
    """,
    unsafe_allow_html=True
)
