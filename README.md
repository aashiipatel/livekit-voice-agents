# 🎙️ LiveKit Voice Agents

A collection of Voice AI agents built with **LiveKit Agents**, demonstrating conversational AI using speech recognition, LLMs, text-to-speech, and the **Model Context Protocol (MCP)**.

This repository contains two implementations:

- 🤖 **Basic Voice Assistant** – A standard LiveKit voice agent powered by Gemini.
- 🏡 **Airbnb MCP Voice Assistant** – A voice agent that can search live Airbnb listings using the Airbnb MCP Server.

---

# ✨ Features

## Basic Voice Agent
- 🎤 Speech-to-Text using Deepgram
- 🧠 Google Gemini LLM
- 🔊 ElevenLabs Text-to-Speech
- 🎙️ Voice Activity Detection (Silero)
- 💬 Natural voice conversations
- 🕒 Built-in function calling example (Current Date & Time)

---

## Airbnb MCP Voice Agent
Everything from the Basic Voice Agent plus:

- 🏡 Live Airbnb search
- 🔎 Real-time listing discovery
- 📍 Property details lookup
- 🤖 Model Context Protocol (MCP) integration
- 🐳 Docker MCP Gateway support
- 🔐 Bearer Token authentication
- 🎙️ Voice-controlled Airbnb assistant

---

# 📂 Project Structure

```
.
├── livekit_basic_agent.py      # Standard Voice Assistant
├── livekit_mcp_agent.py        # Airbnb MCP Voice Assistant
├── .env.example
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

---

# 🛠️ Tech Stack

- Python
- LiveKit Agents
- Google Gemini
- Deepgram STT
- ElevenLabs TTS
- Silero VAD
- Docker MCP Toolkit
- Airbnb MCP Server
- Model Context Protocol (MCP)

---

# 📦 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/livekit-voice-agents.git

cd livekit-voice-agents
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

or

```bash
uv sync
```

---

# 🔑 Environment Variables

Create a `.env` file.

Example:

```env
GOOGLE_API_KEY=your_google_api_key

DEEPGRAM_API_KEY=your_deepgram_api_key

ELEVEN_API_KEY=your_elevenlabs_api_key

ELEVENLABS_VOICE_ID=your_voice_id

MCP_GATEWAY_TOKEN=your_gateway_token
```

---

# 🐳 Running the Airbnb MCP Gateway

Start Docker Desktop.

Run:

```bash
docker mcp gateway run --transport streaming --port 8089 --profile voice_agent
```

The gateway will start at

```
http://localhost:8089/mcp
```

---

# 🚀 Running the Agents

## Basic Voice Agent

```bash
python livekit_basic_agent.py console
```

---

## Airbnb MCP Voice Agent

Start the Docker MCP Gateway first.

Then run

```bash
python livekit_mcp_agent.py console
```

---

# 💬 Example Prompts

### Basic Agent

```
What time is it?

Tell me a joke.

Explain quantum computing.

Summarize AI in simple terms.
```

---

### Airbnb MCP Agent

```
Find Airbnbs in Goa for next weekend.

Show villas in Bali under $200 per night.

Find pet-friendly stays in New York.

Search cabins in Colorado for 4 adults.

Show beachfront homes in Malibu.

Give me details for this Airbnb listing.
```

---

# 🧩 Architecture

```
                ┌─────────────────┐
                │   User Speech   │
                └────────┬────────┘
                         │
                   Deepgram STT
                         │
                    Google Gemini
                         │
          ┌──────────────┴──────────────┐
          │                             │
   Basic Voice Agent             Airbnb MCP Agent
          │                             │
          │                     Docker MCP Gateway
          │                             │
          │                     Airbnb MCP Server
          │                             │
          └──────────────┬──────────────┘
                         │
                 ElevenLabs TTS
                         │
                    Spoken Response
```

---

# 📋 Requirements

- Python 3.11+
- Docker Desktop
- Node.js
- LiveKit Agents
- Deepgram API Key
- Google Gemini API Key
- ElevenLabs API Key

---

# 📚 Resources

- LiveKit Agents
- Google Gemini
- Deepgram
- ElevenLabs
- Docker MCP Toolkit
- Model Context Protocol (MCP)

---

# 🤝 Contributing

Contributions are welcome!

Feel free to open an issue or submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# ⭐ If you found this project useful

Please consider giving it a ⭐ on GitHub.
