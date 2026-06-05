import os
import tempfile

# 1. FFmpeg Path Configuration (Must be at the very top before importing whisper)
ffmpeg_path = r"C:\Users\Admin\Downloads\ffmpeg-8.1.1-essentials_build\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

import streamlit as st
import whisper

# 2. Streamlit Page Setup
st.set_page_config(page_title="AI Meeting Notes Generator")
st.title("🎤 AI Meeting Notes Generator")

# 3. Load Whisper Model (Cached so it only loads once)
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

# 4. Extract Important Points Function
def extract_points(text):
    sentences = (
        text.replace("!", ".")
            .replace("?", ".")
            .replace("\n", " ")
            .split(".")
    )
    
    points = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 25:
            points.append(sentence)
            
    # Return top 7 points
    return points[:7]

# 5. Upload Audio Interface
audio_file = st.file_uploader(
    "Upload Meeting Audio", 
    type=["mp3", "wav", "m4a"]
)

if audio_file is not None:
    st.audio(audio_file)
    
    # Get the file extension
    suffix = "." + audio_file.name.split(".")[-1]
    
    # Create a temporary file safely
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(audio_file.read())
        temp_audio_path = temp_audio.name
        
    try:
        with st.spinner("Transcribing Audio..."):
            result = model.transcribe(temp_audio_path)
            transcript = result["text"]
            
        st.subheader("📄 Transcript")
        st.write(transcript)
        
        st.subheader("✅ Important Meeting Notes")
        points = extract_points(transcript)
        
        notes_text = ""
        for point in points:
            st.write("• " + point)
            notes_text += "• " + point + "\n"
            
        st.download_button(
            label="📥 Download Meeting Notes",
            data=notes_text,
            file_name="meeting_notes.txt",
            mime="text/plain"
        )
        st.success("Meeting Notes Generated Successfully!")
        
    except Exception as e:
        st.error(f"Error during processing: {e}")
        
    finally:
        # Always clean up the temporary file from your storage
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)