import streamlit as st
import qrcode
from PIL import Image
import base64
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Image to QR Code", page_icon="📸", layout="centered")

st.title("📸 Image to QR Code Generator")
st.write("Upload an image and generate a QR code that contains it!")

# File uploader
uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg', 'gif'])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode()
    
    # Create data URL
    data_url = f'image/png;base64,{img_base64}'
    
    # File size warning
    file_size_kb = len(img_base64) / 1024
    st.info(f"📊 Encoded size: {file_size_kb:.2f} KB")
    
    if file_size_kb > 1000:
        st.warning("⚠️ Large images may create complex QR codes that are difficult to scan. Consider resizing the image.")
    
    # Generate QR code button
    if st.button("Generate QR Code", type="primary"):
        with st.spinner("Generating QR code..."):
            try:
                # Create QR code with higher error correction for better scanning
                qr = qrcode.QRCode(
                    version=None,  # Auto-determine size
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(data_url)
                qr.make(fit=True)
                
                # Create QR image
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                # Display QR code
                st.success("✅ QR Code generated successfully!")
                st.image(qr_img, caption="Generated QR Code")
                
                # Save QR code to bytes for download
                qr_buffer = BytesIO()
                qr_img.save(qr_buffer, format="PNG")
                qr_buffer.seek(0)
                
                # Download button
                st.download_button(
                    label="⬇️ Download QR Code",
                    data=qr_buffer,
                    file_name="image_qr_code.png",
                    mime="image/png"
                )
                
                st.info("💡 Tip: Scan this QR code with your phone camera to view the image!")
                
            except Exception as e:
                st.error(f"❌ Error generating QR code: {str(e)}")
                st.info("Try using a smaller image (recommended: less than 100 KB)")

else:
    st.info("👆 Please upload an image to get started")

# Instructions
with st.expander("ℹ️ How to use"):
    st.markdown("""
    1. **Upload** an image file (PNG, JPG, JPEG, or GIF)
    2. Click **Generate QR Code** button
    3. **Download** the generated QR code
    4. **Scan** the QR code with any QR scanner to view your image
    
    **Note:** 
    - Smaller images work best (under 100 KB recommended)
    - Large images create complex QR codes that may be hard to scan
    - The image data is encoded directly in the QR code (no hosting needed!)
    """)

# Footer
st.markdown("---")
st.caption("Built with Streamlit • Free and Open Source")
