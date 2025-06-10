---
title: Transcript Generator
author: Enrique Cardoza
emoji: 💻
sdk: gradio
sdk_version: 5.33.0
app_file: app.py
pinned: false
tags:
  - mcp-server-track
  - speech-to-text
  - whisper
  - groq
  - transcript
  - api
  - stt
demo_video: https://youtu.be/0wBCbXzK8TE
---

# Transcript Generator

A powerful MCP (Model Context Protocol) server that transcribes audio and video files into text using Groq's Whisper model. This tool enables AI assistants to process audio content, making multimedia data accessible for analysis and understanding.

## 📹 Demo Video

[![Transcript Generator Demo](https://img.youtube.com/vi/0wBCbXzK8TE/0.jpg)](https://youtu.be/0wBCbXzK8TE)

There are three ways to use this project:
1. **Directly on the Hugging Face space** - Upload your audio/video files and hit the transcript button
2. **Using your favorite client** like Cursor, Windsurf or any other IDE that supports MCP
3. **Using a custom agent** - Set up the MCP server with its available tools in your own application

## 🔍 Project Description

Transcript Generator is an AI-powered transcription service built for the Gradio Agents & MCP Hackathon 2025. It leverages Groq's implementation of the Whisper Large V3 Turbo model to accurately convert spoken content from audio and video files into written text.

The service supports:
- File uploads (up to 25MB)
- Direct URL transcription
- Various audio/video formats
- Integration with MCP clients

## 🛠️ Available MCP Tools

### 1. `transcript_generator_transcribe_audio`

Transcribes audio/video files uploaded directly to the service (runs in local).

**Parameters:**
- `audio_file` (string): Path to an audio or video file to transcribe
- `api_key` (string): Your Groq API key, required for authentication

**Returns:** A text transcript of the spoken content in the audio file

### 2. `transcript_generator_transcribe_audio_from_url`

Transcribes audio/video files from a URL.

**Parameters:**
- `audio_url` (string): URL to an audio or video file to transcribe (http or https)
- `api_key` (string): Your Groq API key, required for authentication

**Returns:** A text transcript of the spoken content in the audio file

## 📋 Supported File Formats

- **Audio formats:** MP3, MPGA, M4A, WAV, FLAC, OGG, AAC
- **Video formats:** MP4, MPEG, WebM
- **Maximum file size:** 25MB

## 🔌 MCP Integration

### SSE Configuration (Cursor, Windsurf, Cline)

To add this MCP to clients that support SSE, add the following to your MCP config:

```json
{
  "mcpServers": {
    "gradio": {
      "url": "https://agents-mcp-hackathon-transcript-generator.hf.space/gradio_api/mcp/sse"
    }
  }
}
```

### Stdio Configuration (Node.js required)

For clients that only support stdio:

```json
{
  "mcpServers": {
    "gradio": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://agents-mcp-hackathon-transcript-generator.hf.space/gradio_api/mcp/sse",
        "--transport",
        "sse-only"
      ]
    }
  }
}
```

### YAML Configuration (ContinueDev extension)

```yaml
name: Transcript MCP Server
description: A new MCP server for handling transcripts.
version: 0.0.1
schema: v1
mcpServers:
  - name: Transcript MCP server
    command: npx
    args:
      - mcp-remote
      - https://agents-mcp-hackathon-transcript-generator.hf.space/gradio_api/mcp/sse
      - --transport
      - sse-only
```

## 🔑 Authentication

You'll need a Groq API key to use this service. You can obtain one from the [Groq Console](https://console.groq.com/).

The API key can be provided in several ways:
1. As a parameter in the tool call
2. Set as an environment variable (`GROQ_API_KEY`)
3. In the request headers (for certain clients)

## 💡 Usage Example

When using with an AI assistant that supports MCP, you can request transcriptions with prompts like:

> "Please generate the transcript for this audio file: https://huggingface.co/spaces/anewryzm/transcript-generator-client/resolve/main/test_files/this%20people%203.m4a"

The assistant will use the appropriate MCP tool to fetch and return the transcript.

## 🔗 Useful Links

- [Get your Groq API key](https://console.groq.com/)
- [Groq Documentation](https://console.groq.com/docs)
- [Supported audio formats](https://console.groq.com/docs/speech-to-text)
- [Hugging Face Spaces Configuration](https://huggingface.co/docs/hub/spaces-config-reference)
