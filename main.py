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
            quality = st.slider("Image Quality", 10, 95, 70, 
                               help="Lower quality = smaller QR code")
        with col2:
            max_dimension = st.slider("Max Dimension (px)", 200, 2000, 600, step=100,
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
        encoded_size_kb = len(data_url) / 1024
        encoded_size_bytes = len(data_url)
        st.info(f"📊 Original: {file_size_mb:.2f} MB | Encoded size: {encoded_size_kb:.2f} KB ({encoded_size_bytes:,} bytes)")
        
        # QR code settings
        st.subheader("🔲 QR Code Settings")
        col3, col4 = st.columns(2)
        
        with col3:
            box_size = st.slider("QR Box Size", 5, 20, 10,
                                help="Size of each box in pixels (larger = bigger QR)")
        with col4:
            border = st.slider("Border Size", 1, 10, 4,
                              help="Border thickness around QR code")
        
        # QR Version 40 with Error Correction L can hold approximately 2,953 bytes
        max_qr_capacity_bytes = 2953
        
        # Check capacity warnings
        if encoded_size_bytes > max_qr_capacity_bytes:
            st.error(f"🚫 Data too large for QR code! Size: {encoded_size_bytes:,} bytes. Maximum: {max_qr_capacity_bytes:,} bytes (~2.88 KB)")
            st.warning("**You must reduce the image size:**")
            st.markdown("""
            - Reduce **Image Quality** to 30-50
            - Reduce **Max Dimension** to 300-500px
            - Or use a smaller/simpler image
            """)
        elif encoded_size_bytes > (max_qr_capacity_bytes * 0.8):
            st.warning(f"⚠️ Approaching QR code capacity limit! ({encoded_size_bytes:,} / {max_qr_capacity_bytes:,} bytes)")
        
        # Generate QR code button
        if st.button("Generate QR Code", type="primary"):
            # Pre-check data size
            if encoded_size_bytes > max_qr_capacity_bytes:
                st.error(f"❌ Cannot generate QR code: Data size ({encoded_size_bytes:,} bytes) exceeds maximum QR code capacity ({max_qr_capacity_bytes:,} bytes)!")
                st.info("Please reduce image quality or dimensions using the sliders above.")
            else:
                with st.spinner("Generating QR code..."):
                    try:
                        # Create QR code - Use None for version to auto-select, but limit with error handling
                        qr = qrcode.QRCode(
                            version=None,  # Auto-determine based on data size
                            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Lowest error correction = max data
                            box_size=box_size,
                            border=border,
                        )
                        qr.add_data(data_url)
                        qr.make(fit=True)
                        
                        # Check if version exceeds maximum
                        if qr.version > 40:
                            st.error(f"❌ Data requires QR version {qr.version}, but maximum is 40!")
                            st.warning("The image data is too large. Please:")
                            st.markdown("""
                            - Reduce **Image Quality** to 40 or lower
                            - Reduce **Max Dimension** to 400-500px
                            - Use a simpler image
                            """)
                        else:
                            # Create QR image
                            qr_pil_img = qr.make_image(fill_color="black", back_color="white")
                            
                            # Convert to proper PIL Image
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
                            
                            # Save QR code to bytes for download
                            qr_buffer = BytesIO()
                            
                            # Ensure we have a proper PIL Image object
                            if not isinstance(qr_img, Image.Image):
                                qr_img = qr_img.convert('RGB')
                            
                            qr_img.save(qr_buffer, format="PNG")
                            qr_bytes = qr_buffer.getvalue()
                            
                            qr_size_kb = len(qr_bytes) / 1024
                            st.info(f"📁 QR Code file size: {qr_size_kb:.2f} KB")
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download QR Code",
                                data=qr_bytes,
                                file_name=f"image_qr_code_v{qr_version}.png",
                                mime="image/png"
                            )
                            
                            st.success("💡 Tip: Scan this QR code with your phone camera or QR scanner app to view the image!")
                            
                            # Scanning difficulty warning
                            if qr_version >= 30:
                                st.warning(f"⚠️ This is a Version {qr_version} QR code with high data density. It may be difficult to scan. Use a high-quality scanner app and ensure good lighting.")
                            elif qr_version >= 20:
                                st.info(f"ℹ️ Version {qr_version} QR code - should scan well with most modern smartphone cameras.")
                        
                    except Exception as e:
                        error_msg = str(e)
                        st.error(f"❌ Error generating QR code: {error_msg}")
                        
                        if "version" in error_msg.lower() or "invalid" in error_msg.lower():
                            st.warning("🔴 The data is too large for QR code encoding. Try:")
                            st.markdown("""
                            - Reduce **Image Quality** to 30-50
                            - Reduce **Max Dimension** to 300-500px
                            - Use a much simpler/smaller image
                            """)
                        elif "too much data" in error_msg.lower() or "data too long" in error_msg.lower():
                            st.warning("🔴 The image data exceeds QR code capacity. Try:")
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
    2. **Adjust compression settings** to fit within QR code capacity (~2,953 bytes)
    3. **Customize QR code appearance** (box size, border)
    4. Click **Generate QR Code** button
    5. **Download** the generated QR code
    6. **Scan** the QR code to view your embedded image
    
    ### Important Notes:
    - **QR Code Capacity**: Maximum ~2,953 bytes (2.88 KB) for Version 40 with Low error correction
    - **Recommended Settings**: Quality 40-70, Max Dimension 400-800px
    - **Best Results**: Keep encoded size under 2 KB for reliable scanning
    - **Auto-sizing**: QR version automatically adjusts from 1-40 based on data size
    - **No Internet Required**: Image data is embedded directly in the QR code
    
    ### Optimal Settings by Image Type:
    - **Simple logos/icons**: Quality 60-80, Dimension 400-600px
    - **Photos**: Quality 30-50, Dimension 300-500px
    - **Screenshots**: Quality 40-60, Dimension 400-600px
    
    ### Troubleshooting:
    - **"Invalid version" error**: Data too large, reduce quality/dimensions significantly
    - **Scanning issues**: Increase box size to 12-15, ensure good lighting
    - **File too large**: Start with Quality 40 and Dimension 400px
    """)

# Technical info
with st.expander("🔧 Technical Information"):
    st.markdown("""
    ### QR Code Specifications:
    - **QR Versions**: 1-40 (auto-selected based on data)
    - **Version 40**: 177×177 modules, max ~2,953 bytes capacity
    - **Error Correction**: Level L (Low) - 7% restoration, maximum data capacity
    - **Encoding**: Base64 + JPEG compression
    
    ### Data Capacity by Version (Error Correction L):
    - **Version 10**: 652 bytes
    - **Version 20**: 1,273 bytes
    - **Version 30**: 2,071 bytes
    - **Version 40**: 2,953 bytes (MAXIMUM)
    
    ### File Support:
    - **Upload Limit**: 100MB
    - **Supported Formats**: PNG, JPG, JPEG, GIF, WEBP
    - **Output Format**: PNG QR code
    
    **Note**: Versions above 40 don't exist in the QR code standard. The app auto-selects 
    the smallest version that can fit your data.
    """)

# Alternative suggestion
with st.expander("💡 Alternative for Larger Images"):
    st.markdown("""
    If your image exceeds 2,953 bytes even after compression, consider:
    
    ### Cloud Storage Method:
    1. Upload image to **Google Drive, Imgur, or Dropbox**
    2. Generate a **short URL** (bit.ly, tinyurl.com)
    3. Create QR code linking to that URL (only ~50 bytes)
    
    ### Benefits:
    - ✅ Much smaller QR code (easier to scan)
    - ✅ Can share full-resolution images
    - ✅ Can update image without changing QR code
    
    ### This Embedded Method:
    - ✅ No internet required to view
    - ✅ Image never expires
    - ✅ Complete privacy (no cloud storage)
    - ❌ Limited to ~2KB images
    """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit • QR Code Versions 1-40 Supported")
