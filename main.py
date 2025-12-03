import streamlit as st
import qrcode
from PIL import Image
import base64
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Image to QR Code", page_icon="📸", layout="centered")

st.title("📸 Image to QR Code Generator")
st.write("Upload an image and generate a QR code that contains it!")

# File uploader with 100MB limit
uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg', 'gif', 'webp'], 
                                  help="Maximum file size: 100MB")

if uploaded_file is not None:
    # Check file size (100MB = 104857600 bytes)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    
    if file_size_mb > 100:
        st.error(f"❌ File too large! Size: {file_size_mb:.2f} MB. Maximum allowed: 100 MB")
    else:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded Image ({file_size_mb:.2f} MB)", use_container_width=True)
        
        # Compression options
        st.subheader("⚙️ Compression Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            quality = st.slider("Image Quality", 10, 95, 85, 
                               help="Lower quality = smaller QR code")
        with col2:
            max_dimension = st.slider("Max Dimension (px)", 200, 2000, 800, step=100,
                                     help="Resize image to fit within this dimension")
        
        # Resize image if needed
        img_width, img_height = image.size
        if img_width > max_dimension or img_height > max_dimension:
            if img_width > img_height:
                new_width = max_dimension
                new_height = int((max_dimension / img_width) * img_height)
            else:
                new_height = max_dimension
                new_width = int((max_dimension / img_height) * img_width)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            st.info(f"🔄 Image resized to {new_width}x{new_height} pixels")
        
        # Convert image to base64
        buffered = BytesIO()
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        
        # Save with compression
        image.save(buffered, format="JPEG", optimize=True, quality=quality)
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode()
        
        # Create data URL
        data_url = f'data:image/jpeg;base64,{img_base64}'
        
        # File size info
        encoded_size_kb = len(img_base64) / 1024
        st.info(f"📊 Original: {file_size_mb:.2f} MB | Encoded size: {encoded_size_kb:.2f} KB")
        
        # QR code settings
        st.subheader("🔲 QR Code Settings")
        col3, col4 = st.columns(2)
        
        with col3:
            box_size = st.slider("QR Box Size", 5, 20, 10,
                                help="Size of each box in pixels (larger = bigger QR)")
        with col4:
            border = st.slider("Border Size", 1, 10, 4,
                              help="Border thickness around QR code")
        
        # Updated capacity warning for 10MB limit
        if encoded_size_kb > 10000:
            st.error(f"⚠️ The encoded data is {encoded_size_kb:.2f} KB. Maximum limit is 10,000 KB (10 MB). "
                      "Please reduce quality or image dimensions.")
        elif encoded_size_kb > 5000:
            st.warning(f"⚠️ Large encoded size: {encoded_size_kb:.2f} KB. Very large QR codes may be extremely difficult to scan. "
                      "Consider reducing quality or dimensions for practical use.")
        
        # Generate QR code button
        if st.button("Generate QR Code", type="primary"):
            # Check if data exceeds 10MB limit
            if encoded_size_kb > 10000:
                st.error("❌ Cannot generate QR code: Data exceeds 10,000 KB limit!")
                st.warning("Try:")
                st.markdown("""
                - Reduce **Image Quality** to 50 or lower
                - Reduce **Max Dimension** to 400px or lower
                - Use a simpler/smaller image
                """)
            else:
                with st.spinner("Generating high-capacity QR code..."):
                    try:
                        # Create QR code with maximum capacity settings
                        qr = qrcode.QRCode(
                            version=40,  # Maximum version for largest capacity (177x177 modules)
                            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Lowest error correction = max data
                            box_size=box_size,
                            border=border,
                        )
                        qr.add_data(data_url)
                        qr.make(fit=True)
                        
                        # Create QR image - FIX: Convert to PIL Image properly
                        qr_pil_img = qr.make_image(fill_color="black", back_color="white")
                        
                        # Convert PIL.Image.Image to actual PIL Image if needed
                        if hasattr(qr_pil_img, '_img'):
                            qr_img = qr_pil_img._img
                        else:
                            qr_img = qr_pil_img
                        
                        # Get actual QR version used
                        qr_version = qr.version
                        qr_modules = 17 + (4 * qr_version)
                        
                        # Display QR code
                        st.success(f"✅ QR Code generated successfully! (Version {qr_version}, {qr_modules}x{qr_modules} modules)")
                        st.image(qr_img, caption="Generated QR Code", width=600)
                        
                        # Save QR code to bytes for download - FIX: Use BytesIO properly
                        qr_buffer = BytesIO()
                        
                        # Ensure we have a proper PIL Image object
                        if not isinstance(qr_img, Image.Image):
                            qr_img = qr_img.convert('RGB')
                        
                        qr_img.save(qr_buffer, format="PNG")
                        qr_bytes = qr_buffer.getvalue()
                        
                        qr_size_kb = len(qr_bytes) / 1024
                        st.info(f"📁 QR Code file size: {qr_size_kb:.2f} KB")
                        
                        # Download button - FIX: Pass bytes directly
                        st.download_button(
                            label="⬇️ Download QR Code",
                            data=qr_bytes,
                            file_name=f"image_qr_code_v{qr_version}.png",
                            mime="image/png"
                        )
                        
                        st.success("💡 Tip: Scan this QR code with your phone camera or QR scanner app to view the image!")
                        
                        # Scanning difficulty warning
                        if encoded_size_kb > 2.5:
                            st.warning("⚠️ This QR code contains a lot of data and may be very difficult to scan with standard QR readers. "
                                      "You may need a high-resolution printer and specialized QR scanner app.")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating QR code: {str(e)}")
                        if "too much data" in str(e).lower() or "data too long" in str(e).lower():
                            st.warning("🔴 The image data is too large for QR code encoding. Try:")
                            st.markdown("""
                            - Reduce **Image Quality** to 40-60
                            - Reduce **Max Dimension** to 400-600px
                            - Use a simpler image with fewer details
                            """)
                        else:
                            st.info("Try adjusting compression settings or using a smaller/simpler image")

else:
    st.info("👆 Please upload an image to get started (max 100MB)")

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    ### Steps:
    1. **Upload** an image file (PNG, JPG, JPEG, GIF, or WEBP) - up to 100MB
    2. **Adjust compression settings** to fit data within 10MB encoded limit
    3. **Customize QR code appearance** (box size, border)
    4. Click **Generate QR Code** button
    5. **Download** the generated QR code
    6. **Scan** the QR code to view your embedded image
    
    ### Important Notes:
    - **New Limit**: Maximum 10,000 KB (10 MB) of encoded data
    - **Recommended Settings**: Quality 60-80, Max Dimension 600-1000px
    - **Large Images**: Will be compressed and resized automatically
    - **High-Definition Output**: Uses Version 40 QR codes (177×177 modules) for maximum capacity
    - **No Internet Required**: Image data is embedded directly in the QR code
    
    ### Practical Considerations:
    - QR codes with >3KB of data become very dense and hard to scan
    - For best results, keep encoded size under 5MB
    - Use high-resolution display/print for large QR codes
    - Test scanning with your specific device before final use
    
    ### Troubleshooting:
    - If QR generation fails, reduce quality or dimensions
    - Very complex QR codes require specialized scanners
    - For box size, use 10-15 for best balance
    """)

# Technical info
with st.expander("🔧 Technical Information"):
    st.markdown("""
    - **QR Version 40**: 177×177 modules, maximum practical capacity
    - **Error Correction**: Level L (Low) for maximum data storage
    - **Encoding**: Base64 + JPEG compression
    - **Supported Formats**: PNG, JPG, JPEG, GIF, WEBP
    - **Upload Limit**: 100MB
    - **Encoded Data Limit**: 10,000 KB (10 MB)
    
    **Note**: While we allow up to 10MB of encoded data, QR codes with more than 3-5KB 
    may be impractical to scan with standard smartphone cameras. Consider using alternative 
    methods like cloud storage with a QR code link for very large images.
    """)

# Alternative suggestion
with st.expander("💡 Alternative for Very Large Images"):
    st.markdown("""
    If your image is too large for practical QR code scanning, consider these alternatives:
    
    1. **Upload to cloud storage** (Google Drive, Dropbox, etc.)
    2. **Generate a short URL** to the image
    3. **Create a QR code** linking to that URL (much smaller and easier to scan)
    
    This approach works better for images larger than 200-300 KB.
    """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit • Enhanced for High-Capacity QR Codes (10MB Limit)")
