import streamlit as st
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile
import os

# --- Configure Gemini ---
genai.configure(api_key="AIzaSyCdrOAxmJAQFAjAuJmupJeRBQuMR8IEn0c")  # Replace with your inbuilt Gemini API key

# --- Streamlit Page Config ---
st.set_page_config(page_title="LinkedIn Content Generator", layout="centered")
st.title("🚀 LinkedIn Content Generator")

st.markdown("Generate polished LinkedIn posts in seconds using AI. Just provide a few details and download your ready-to-post content!")

# --- Sidebar Settings ---
with st.sidebar:
    st.header("🛠️ Settings")
    content_format = st.selectbox("Select Format", ["Storytelling", "Listicle", "Announcement", "Event Invite", "Product Launch"])
    tone = st.radio("Select Tone", ["Professional", "Casual", "Witty", "Inspirational", "Empathetic"])

# --- User Inputs ---
topic = st.text_input("🔖 Topic", placeholder="E.g., Launching our new product")
description = st.text_area("📝 Description", placeholder="Enter a few lines about your post...")

hashtags = st.text_input("🏷️ Hashtags", placeholder="E.g., #AI #Innovation #Leadership")

media_type = st.selectbox("🖼️ Media Type", ["None", "Image", "Video"])

# --- Generate Button ---
if st.button("Generate LinkedIn Content"):
    if not topic or not description:
        st.warning("Please fill in the Topic and Description.")
    else:
        with st.spinner("Generating content..."):
            prompt = f"""
            Act as a LinkedIn content writer.
            Write a {tone.lower()} LinkedIn post in a {content_format.lower()} format.
            Topic: {topic}
            Description: {description}
            Include hashtags: {hashtags}
            Media Type: {media_type}
            """

            model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
            response = model.generate_content(prompt)

            post_text = response.text.strip()
            st.success("✅ Content Generated")
            st.text_area("🧾 LinkedIn Post Preview", value=post_text, height=300)

            # Save to session
            st.session_state['generated_content'] = post_text
            st.session_state['prompt'] = prompt

# --- Regenerate Button ---
if 'generated_content' in st.session_state:
    if st.button("🔁 Regenerate with New Tone/Format"):
        with st.spinner("Regenerating content..."):
            prompt = st.session_state['prompt']
            prompt = prompt.split("Write a")[0] + f"Write a {tone.lower()} LinkedIn post in a {content_format.lower()} format.\n" + "\n".join(prompt.split("\n")[2:])
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            new_post_text = response.text.strip()
            st.session_state['generated_content'] = new_post_text
            st.text_area("🧾 Regenerated Post Preview", value=new_post_text, height=300)

# --- Download PDF Button ---
if 'generated_content' in st.session_state:
    def create_pdf(text):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        c = canvas.Canvas(temp_file.name, pagesize=letter)
        width, height = letter
        text_object = c.beginText(40, height - 40)
        text_object.setFont("Helvetica", 12)

        for line in text.splitlines():
            text_object.textLine(line)

        c.drawText(text_object)
        c.save()
        return temp_file.name

    if st.button("📄 Download as PDF"):
        pdf_file_path = create_pdf(st.session_state['generated_content'])
        with open(pdf_file_path, "rb") as f:
            st.download_button("Download PDF", data=f, file_name="linkedin_post.pdf", mime="application/pdf")
        os.remove(pdf_file_path)
