import gradio as gr
import os
from groq import Groq
import tempfile
import requests
import urllib.parse

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

def validate_url_file(url):
    """Validate file from URL based on extension and size."""
    if not url or url.strip() == "":
        return False, "No URL provided"
    
    try:
        # Check if the URL is valid
        parsed_url = urllib.parse.urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return False, "Invalid URL format"
        
        if parsed_url.scheme not in ['http', 'https']:
            return False, "URL must start with http:// or https://"
            
        # Check file extension from URL
        valid_extensions = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.flac', '.ogg', '.aac']
        file_extension = os.path.splitext(parsed_url.path)[1].lower()
        
        if file_extension not in valid_extensions:
            return False, f"Invalid file type in URL. Supported formats: {', '.join(valid_extensions)}"
            
        # Check file size with a HEAD request
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code != 200:
            return False, f"Could not access URL (HTTP {response.status_code})"
            
        content_length = response.headers.get('content-length')
        if content_length:
            file_size_mb = int(content_length) / (1024 * 1024)
            if file_size_mb > 25:
                return False, f"File size ({file_size_mb:.1f}MB) exceeds 25MB limit"
                
        return True, "File is valid"
        
    except requests.exceptions.RequestException as e:
        return False, f"Error accessing URL: {str(e)}"
    except Exception as e:
        return False, f"Error validating URL: {str(e)}"

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

def transcribe_audio_from_url(audio_url, api_key, request: gr.Request = None):
    """Transcribe audio/video files from a URL into text using Groq's Whisper model.
    
    This tool converts spoken content from audio and video files into written text.
    It supports multiple audio formats and handles files up to 25MB in size.
    
    Parameters:
        audio_url: URL to an audio or video file to transcribe (http or https). 
                  Supported formats: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM, FLAC, OGG, AAC.
                  Maximum size: 25MB.
        api_key: Your Groq API key, required for authentication.
                You can obtain this from https://console.groq.com/
    
    Returns:
        A text transcript of the spoken content in the audio file.
        
    Example:
        Provide a URL to a podcast episode to get a complete text transcript.
    """
    try:
        # First check for environment variable, then use provided API key
        actual_api_key = os.environ.get("GROQ_API_KEY")

        if not actual_api_key and request is not None:
            # If request is provided, check for API key in headers
            actual_api_key = request.headers.get("GROQ_API_KEY")
        
        if not actual_api_key:
            actual_api_key = api_key
        
        # Validate API key
        if not actual_api_key:
            return "Error: Please provide your Groq API key or set the GROQ_API_KEY environment variable"
        
        if not audio_url or audio_url.strip() == "":
            return "Error: Please provide a URL to an audio or video file"
        
        # Validate file from URL
        is_valid, message = validate_url_file(audio_url)
        if not is_valid:
            return f"Error: {message}"
        
        # Initialize Groq client
        client = Groq(api_key=actual_api_key)
        
        # Download the file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            response = requests.get(audio_url, stream=True, timeout=30)
            response.raise_for_status()
            
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            
            temp_file_path = temp_file.name
        
        try:
            # Read the downloaded file
            with open(temp_file_path, "rb") as file:
                # Get the original filename from the URL
                filename = os.path.basename(urllib.parse.urlparse(audio_url).path)
                if not filename:
                    filename = "audio_from_url"
                
                # Create transcription
                transcription = client.audio.transcriptions.create(
                    file=(filename, file.read()),
                    model="whisper-large-v3-turbo"
                )
            
            return transcription.text
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except requests.exceptions.RequestException as e:
        return f"Error downloading file: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create the Gradio interface with custom layout
with gr.Blocks(title="Audio/Video Transcription with Groq", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎵 Audio/Video Transcription with Groq Whisper")
    gr.Markdown("Upload an audio/video file or provide a URL and get an AI-generated transcript using Groq's Whisper model.")
    
    # API Key input - shared between tabs
    api_key_note = "API key will be used from environment variable if set" if os.environ.get("GROQ_API_KEY") else ""
    api_key_input = gr.Textbox(
        label="Groq API Key",
        placeholder="Enter your Groq API key here or set GROQ_API_KEY environment variable",
        type="password",
        lines=1,
        info=api_key_note
    )
    
    with gr.Tabs():
        # Tab 1: File Upload
        with gr.TabItem("Upload File"):
            with gr.Row():
                # Left column - Input controls
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Upload Audio/Video")
                    
                    audio_input = gr.File(
                        label="Upload Audio/Video File",
                        file_types=[".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".flac", ".ogg", ".aac"],
                        file_count="single"
                    )
                    
                    upload_transcribe_btn = gr.Button(
                        "🎯 Transcribe Uploaded File",
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
                    
                    upload_transcript_output = gr.Textbox(
                        label="Generated Transcript",
                        placeholder="Your transcript will appear here...",
                        lines=20,
                        max_lines=30,
                        show_copy_button=True,
                        interactive=False
                    )
        
        # Tab 2: URL Input
        with gr.TabItem("Audio URL"):
            with gr.Row():
                # Left column - Input controls
                with gr.Column(scale=1):
                    gr.Markdown("### 🔗 Audio/Video URL")
                    
                    url_input = gr.Textbox(
                        label="URL to Audio/Video File",
                        placeholder="Enter the http/https URL to an audio or video file",
                        lines=2
                    )
                    
                    url_transcribe_btn = gr.Button(
                        "🎯 Transcribe from URL",
                        variant="primary",
                        size="lg"
                    )
                    
                    gr.Markdown("### ℹ️ URL Requirements")
                    gr.Markdown("""
                    - **URL format**: Must start with http:// or https://
                    - **Max file size**: 25MB
                    - **Supported formats**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM, FLAC, OGG, AAC
                    - **Direct link**: URL must point directly to the audio/video file
                    """)
                
                # Right column - Output
                with gr.Column(scale=1):
                    gr.Markdown("### 📝 Transcript")
                    
                    url_transcript_output = gr.Textbox(
                        label="Generated Transcript",
                        placeholder="Your transcript will appear here...",
                        lines=20,
                        max_lines=30,
                        show_copy_button=True,
                        interactive=False
                    )
    
    # Connect the buttons to their respective transcription functions
    upload_transcribe_btn.click(
        fn=transcribe_audio,
        inputs=[audio_input, api_key_input],
        outputs=upload_transcript_output,
        show_progress=True
    )
    
    url_transcribe_btn.click(
        fn=transcribe_audio_from_url,
        inputs=[url_input, api_key_input],
        outputs=url_transcript_output,
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
    demo.launch()