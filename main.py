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
        
        # QR capacity warning
        if encoded_size_kb > 2.5:
            st.warning(f"⚠️ The encoded data is {encoded_size_kb:.2f} KB. QR codes have a maximum capacity of ~3KB. "
                      "Large QR codes may be difficult to scan. Try reducing quality or image dimensions.")
        
        # Generate QR code button
        if st.button("Generate QR Code", type="primary"):
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
                    
                    # Create QR image
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    # Get actual QR version used
                    qr_version = qr.version
                    qr_modules = 17 + (4 * qr_version)
                    
                    # Display QR code
                    st.success(f"✅ QR Code generated successfully! (Version {qr_version}, {qr_modules}x{qr_modules} modules)")
                    st.image(qr_img, caption="Generated QR Code", width=600)
                    
                    # Save QR code to bytes for download
                    qr_buffer = BytesIO()
                    qr_img.save(qr_buffer, format="PNG")
                    qr_buffer.seek(0)
                    
                    qr_size_kb = len(qr_buffer.getvalue()) / 1024
                    st.info(f"📁 QR Code file size: {qr_size_kb:.2f} KB")
                    
                    # Download button
                    st.download_button(
                        label="⬇️ Download QR Code",
                        data=qr_buffer,
                        file_name=f"image_qr_code_v{qr_version}.png",
                        mime="image/png"
                    )
                    
                    st.success("💡 Tip: Scan this QR code with your phone camera or QR scanner app to view the image!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating QR code: {str(e)}")
                    if "too much data" in str(e).lower() or "data too long" in str(e).lower():
                        st.warning("🔴 The image data exceeds QR code capacity (~3KB max). Try:")
                        st.markdown("""
                        - Reduce **Image Quality** to 60 or lower
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
    2. **Adjust compression settings** to fit data within QR code capacity (~3KB)
    3. **Customize QR code appearance** (box size, border)
    4. Click **Generate QR Code** button
    5. **Download** the generated QR code
    6. **Scan** the QR code to view your embedded image
    
    ### Important Notes:
    - **QR Code Capacity**: Maximum ~3KB of binary data (2,953 bytes)
    - **Recommended Settings**: Quality 70-85, Max Dimension 600-800px
    - **Large Images**: Will be compressed and resized automatically
    - **High-Definition Output**: Uses Version 40 QR codes (177×177 modules) for maximum capacity
    - **No Internet Required**: Image data is embedded directly in the QR code
    
    ### Troubleshooting:
    - If QR generation fails, reduce quality or dimensions
    - Very complex QR codes may be hard to scan - test with your device
    - For best scanning, use box size 10-15 and border 4
    """)

# Technical info
with st.expander("🔧 Technical Information"):
    st.markdown("""
    - **QR Version 40**: 177×177 modules, up to 2,953 bytes capacity
    - **Error Correction**: Level L (Low) for maximum data storage
    - **Encoding**: Base64 + JPEG compression
    - **Supported Formats**: PNG, JPG, JPEG, GIF, WEBP
    - **File Size Limit**: 100MB upload, ~3KB after encoding
    """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit • Enhanced for High-Capacity QR Codes")
