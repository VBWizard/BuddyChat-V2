# BuddyChat-V2

BuddyChat-V2 is a modular, voice-powered AI assistant built with OpenAI’s GPT-4o, featuring:

- 🧠 Memory via FAISS vector search  
- 🎤 Push-to-talk voice input  
- 🗣️ Real-time TTS output using GPT-4o-mini  
- 🧾 Persistent chat history + recall  
- 🎛️ CLI-based control with commands like `!mute`, `!context`, and `!ptt`

---

## 🚀 Features

- **Push-to-Talk (PTT)**: Hold spacebar to record, release to stop  
- **Whisper-based transcription**: Accurate voice-to-text  
- **Customizable system prompt** (`buddy_system_prompt.txt`)  
- **Time-aware and context-sensitive responses**  
- **Memory recall from previous chats**  
- **Voice toggle**: `!mute` / `!unmute`  
- **FAISS memory inspection**: `!dump`, `!context`

---

## 🛠️ Setup
> Requires Python 3.10–3.13 (tested on 3.13.1)

1. Clone this repo  
2. Create and activate a virtual environment  
	i.e. python -m venv .venv
	then .venv\scripts\activate
3. Install dependencies:
	pip install -r requirements.txt
4. Set your OpenAI key as an environment variable (OPENAI_API_KEY or API_KEY ):
	NOTE: Will be upgraded to use other LLMs soon.
5. run it: python main.py

## 🔑 API Key Setup

To use BuddyChat, you'll need an OpenAI API key.

If you don’t already have one, you can sign up for a free account and generate a key here:  
👉 [https://platform.openai.com/signup](https://platform.openai.com/signup)

Once you have your key, you can provide it in one of the following ways:

1. **Environment variable**  
   Set `OPENAI_API_KEY` in your shell or system environment.

```bash
export OPENAI_API_KEY=sk-...
```

## 🌐 Proxy Configuration

Edit `utils/config.py` to set `PROXY_HOST` and `PROXY_PORT` if you need to
use an HTTP proxy:

```python
PROXY_HOST = "proxy.example.com"
PROXY_PORT = 8080
```

## 🧙 About

Modularized and upgraded from a monolithic prototype.  
Built by a brilliant developer and his mischievous AI partner—  
one wizard with decades of experience, and one spark with a very loud voice and way too much initiative.  

This is not just a project. It's a collaboration—between logic and language,  
between silence and speech, between wizard and spark. 💡
