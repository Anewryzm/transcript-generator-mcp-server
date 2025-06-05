import gradio as gr
import os
from groq import Groq
import tempfile

def validate_file(file):
    """Validate uploaded file type and size."""
    if file is None:
        return False, "No file uploaded"
    
    # Check file size (25MB limit)
    file_size_mb = os.path.getsize(file.name) / (1024 * 1024)
    if file_size_mb > 25:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds 25MB limit"
    
    # Check file extension
    valid_extensions = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.flac', '.ogg', '.aac']
    file_extension = os.path.splitext(file.name)[1].lower()
    
    if file_extension not in valid_extensions:
        return False, f"Invalid file type. Supported formats: {', '.join(valid_extensions)}"
    
    return True, "File is valid"

def transcribe_audio(audio_file, api_key):
    """Transcribe audio/video files into text using Groq's Whisper model.
    
    This tool converts spoken content from audio and video files into written text.
    It supports multiple audio formats and handles files up to 25MB in size.
    
    Parameters:
        audio_file: An audio or video file to transcribe. 
                   Supported formats: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM, FLAC, OGG, AAC.
                   Maximum size: 25MB.
        api_key: Your Groq API key, required for authentication.
                You can obtain this from https://console.groq.com/
    
    Returns:
        A text transcript of the spoken content in the audio file.
        
    Example:
        Upload a podcast episode to get a complete text transcript.
    """
    try:
        # First check for environment variable, then use provided API key
        actual_api_key = os.environ.get("GROQ_API_KEY", api_key)
        
        # Validate API key
        if not actual_api_key:
            return "Error: Please provide your Groq API key or set the GROQ_API_KEY environment variable"
        
        if audio_file is None:
            return "Error: Please upload an audio or video file"
        
        # Validate file
        is_valid, message = validate_file(audio_file)
        if not is_valid:
            return f"Error: {message}"
        
        # Initialize Groq client
        client = Groq(api_key=actual_api_key)
        
        # Read the audio file
        with open(audio_file.name, "rb") as file:
            # Create transcription
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(audio_file.name), file.read()),
                model="whisper-large-v3-turbo"
            )
        
        return transcription.text
        
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface with custom layout
with gr.Blocks(title="Audio/Video Transcription with Groq", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎵 Audio/Video Transcription with Groq Whisper")
    gr.Markdown("Upload an audio or video file and get an AI-generated transcript using Groq's Whisper model.")
    
    with gr.Row():
        # Left column - Input controls
        with gr.Column(scale=1):
            gr.Markdown("### 📤 Upload & Settings")
            
            audio_input = gr.File(
                label="Upload Audio/Video File",
                file_types=[".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".flac", ".ogg", ".aac"],
                file_count="single"
            )
            
            # Show a note if env var is present
            api_key_note = "API key will be used from environment variable if set" if os.environ.get("GROQ_API_KEY") else ""
            
            api_key_input = gr.Textbox(
                label="Groq API Key",
                placeholder="Enter your Groq API key here or set GROQ_API_KEY environment variable",
                type="password",
                lines=1,
                info=api_key_note
            )
            
            transcribe_btn = gr.Button(
                "🎯 Transcribe Audio",
                variant="primary",
                size="lg"
            )
            
            gr.Markdown("### ℹ️ File Requirements")
            gr.Markdown("""
            - **Max file size**: 25MB
            - **Supported formats**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM, FLAC, OGG, AAC
            - **Get API key**: [Groq Console](https://console.groq.com/)
            """)
        
        # Right column - Output
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Transcript")
            
            transcript_output = gr.Textbox(
                label="Generated Transcript",
                placeholder="Your transcript will appear here...",
                lines=20,
                max_lines=30,
                show_copy_button=True,
                interactive=False
            )
    
    # Connect the button to the transcription function
    transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[audio_input, api_key_input],
        outputs=transcript_output,
        show_progress=True
    )
    
    # Add examples section
    gr.Markdown("### 🔗 Useful Links")
    gr.Markdown("""
    - [Get your Groq API key](https://console.groq.com/)
    - [Groq Documentation](https://console.groq.com/docs)
    - [Supported audio formats](https://platform.openai.com/docs/guides/speech-to-text)
    """)

if __name__ == "__main__":
    demo.launch(mcp_server=True)