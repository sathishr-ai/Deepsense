<div align="center">

# 🌌 DeepSense 
### Advanced Multi-Modal AI Interface & Neural Engine
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI%20GPT--4o--mini-412991.svg?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-success.svg?style=for-the-badge)](#license)

[**Live Demo**](https://deepsense.streamlit.app) • [**Report Bug**](https://github.com/sathishr-ai/Deepsense/issues) • [**Request Feature**](https://github.com/sathishr-ai/Deepsense/issues)

</div>

---

## 📖 Overview

**DeepSense** (formerly *VoxMind*) is a state-of-the-art conversational AI platform engineered to bridge the gap between powerful neural language models and seamless, multi-modal human interaction.

Designed from the ground up to rival top-tier industry applications, DeepSense provides an ultra-premium **Cyber-Cyan** glassmorphism interface that perfectly scales from enterprise desktop displays down to a native-feeling ChatGPT-style mobile application.

It acts as a dynamic intelligence hub—capable of listening to your voice, answering complex queries, extracting data from uploaded documents, and synthesizing its responses back to you audibly in real-time.

---

## ⚡ Core Features

### 🎙️ 1. Voice Intelligence Engine (STT/TTS)
DeepSense breaks the barrier of text-only interfaces. 
- **Speech-to-Text (STT):** Utilizing high-fidelity local microphone APIs (`PyAudio` & `SpeechRecognition`), DeepSense accurately transcribes your spoken word into neural queries.
- **Text-to-Speech (TTS):** Responses aren't just generated; they are spoken. Featuring offline fast-speech synthesis (`pyttsx3`) and cloud-based natural rendering (`gTTS`), DeepSense audibly communicates with you in multiple languages.

### 🧠 2. Deep Language Processing & Multi-Lingual Support
Powered by the blazing-fast **GPT-4o-mini** architecture, DeepSense understands context, nuance, and logic.
- Natively supports both **English** and **Tamil**.
- Automatic language detection dynamically switches the AI's processing and speaking engine depending on the user's origin language.

### 🌍 3. Live Web Search & Telemetry
Large Language Models have a knowledge cutoff. DeepSense does not.
- Features a **Live Web Override** button that connects the AI directly to global internet streams (`Tavily API`).
- Extracts real-time stock prices, breaking news, and current events to augment the neural generation process dynamically.

### 📄 4. Multi-Modal Document Extraction
Need to analyze data? Simply drop it into the intelligence core.
- **PDF Parsing:** Extracts and tokenizes multi-page `.pdf` reports (`PyPDF2`).
- **CSV Data:** Parses and ingests structured tabular data (`Pandas`).
- **Vision/Images:** Encodes images via Base64 and allows the neural network to "see" your uploads.

### 📱 5. Responsive "Glassmorphism" UI/UX
- **Mobile First:** Engineered with a custom CSS engine that aggressively forces a flawless, stacked, pill-based mobile layout (mimicking native iOS/Android apps).
- **Cinematic Splash Screen:** Features a pulsing "System Core" loading sequence.
- **Dashboard Telemetry:** Displays system status, network latency, and active engine nodes in a top-right cyber-navigation bar.

### 📜 6. Neural Link Transcripts
Never lose a conversation. DeepSense tracks all context in local state memory and allows one-click generation of professional `.pdf` chat logs (`FPDF`) to save and share your intelligence sessions.

---

## 🏗️ System Architecture

The project is structured using a clean, modular design pattern to ensure scalability and ease of deployment.

```text
DeepSense/
├── app.py                      # Main Streamlit UI & Application Core
├── requirements.txt            # Dependency management
├── packages.txt                # System-level dependencies for Cloud Deployments
├── .env                        # Environment configurations (API Keys)
│
├── core/
│   ├── chatbot.py              # LLM integration & System Prompts
│   ├── stt.py                  # Speech-to-Text handler
│   └── tts.py                  # Text-to-Speech synthesizer
│
├── ui/
│   └── style.css               # Advanced CSS overrides (Cyber-Cyan / Mobile Resizing)
│
└── memory/
    └── conversation_memory.py  # Context window & state persistence
```

---

## ⚙️ Installation & Local Setup

### Prerequisites
- **Python:** `3.10` or higher
- **Git:** Version control

### 1. Clone the Repository
```bash
git clone https://github.com/sathishr-ai/Deepsense.git
cd Deepsense
```

### 2. Install System Audio Drivers (Linux Only)
If you are running on Ubuntu/Debian, you must install the `portaudio` C-library before installing Python audio libraries.
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio
```
*(Mac users: `brew install portaudio`)*

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory. You will need an OpenAI API key.
```env
OPENAI_API_KEY="sk-your-openai-api-key-here"
TAVILY_API_KEY="tvly-your-tavily-api-key-here" # (Optional) For Live Web Search
```

### 5. Initialize the Core
```bash
streamlit run app.py
```
The application will boot and become accessible at `http://localhost:8501`.

---

## 🚀 Cloud Deployment (Streamlit Community Cloud)

DeepSense is fully optimized for one-click deployment via Streamlit Community Cloud. The included `packages.txt` ensures that server-side audio dependencies are automatically resolved.

1. Ensure your repository is pushed to GitHub (excluding your `.env` file).
2. Navigate to [share.streamlit.io](https://share.streamlit.io/).
3. Click **New app** and connect your GitHub repository.
4. Set the main file path to `app.py`.
5. Open **Advanced settings** and inject your API keys into the Secrets Manager:
   ```toml
   OPENAI_API_KEY="sk-..."
   TAVILY_API_KEY="tvly-..."
   ```
6. Click **Deploy**. Your app will be live globally in under 2 minutes.

---

## 🛠️ Technology Stack

| Category | Technologies Used |
| :--- | :--- |
| **Frontend Framework** | Streamlit, HTML5, Vanilla CSS3 (Custom Glassmorphism) |
| **Language Model** | OpenAI GPT-4o-mini |
| **Voice Processing** | `SpeechRecognition`, `PyAudio`, `pyttsx3`, `gTTS` |
| **Data Parsing** | `PyPDF2`, `Pandas`, `urllib` |
| **State Management** | Streamlit Session State |

---

## 🔮 Future Roadmap
- [ ] **Local LLM Integration:** Fallback support for local models (e.g., Llama 3 via Ollama) to run entirely offline.
- [ ] **Advanced RAG Pipeline:** Implement ChromaDB for deep, persistent vector storage of uploaded documents.
- [ ] **Whisper Transcription:** Replace Google Web Speech STT with OpenAI Whisper for flawless, offline transcription.

---

## 👨‍💻 Author & Career Details

**Sathish R.**  
*AI Engineer & Software Developer*  

If you are a recruiter or hiring manager reviewing this repository, below are templates you can use to understand the scope of my work on this project:

### 📝 Resume / CV Bullet Points
> - Engineered **DeepSense**, a full-stack, voice-enabled AI platform utilizing Python, Streamlit, and the OpenAI GPT-4 API, architected with a responsive, native-mobile CSS UI.
> - Implemented multi-modal data ingestion pipelines capable of parsing PDFs, CSVs, and Base64 images, combined with real-time web scraping integration for live data augmentation.
> - Developed a complete NLP voice stack featuring local audio buffering (`PyAudio`), offline transcription, and multi-lingual text-to-speech synthesis logic.

### 🌐 LinkedIn Post Template
> 🚀 **Just launched DeepSense — a Voice-Enabled AI Chatbot!**
> 
> I am thrilled to share my latest project: a highly advanced, multi-modal conversational AI agent built with Streamlit and OpenAI. 
> 
> DeepSense breaks away from standard text interfaces. It features a complete Cyber-Cyan UI, real-time web search capabilities, dynamic document parsing, and full voice interactions (Speak to it, and it speaks back!).
> 
> Check out the live demo and the source code on GitHub! Let me know what you think of the architecture in the comments. 👇
> 
> #AI #Python #DeepLearning #Streamlit #OpenAI #SoftwareEngineering

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">
  <p><i>DeepSense – Where Voice Meets Intelligence</i></p>
</div>
