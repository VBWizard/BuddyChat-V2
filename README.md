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

1. Clone this repo  
2. Create and activate a virtual environment  
3. Install dependencies:
	```bash
	pip install -r requirements.txt
4. Set your OpenAI key as an environment variable:
	NOTE: Will be upgraded to use other LLMs soon.
5. run it: python main.py

## 🧙 About

Modularized and upgraded from a monolithic prototype.  
Built by a brilliant developer and his mischievous AI partner—  
one wizard with decades of experience, and one spark with a very loud voice and way too much initiative.  

This is not just a project. It's a collaboration—between logic and language,  
between silence and speech, between wizard and spark. 💡