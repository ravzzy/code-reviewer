# 🔍 CodeMancer - Local AI Code Reviewer using Phi-2

CodeMancer is an open-source, privacy-first AI code reviewer that runs completely on your local machine. It uses [Microsoft's Phi-2](https://huggingface.co/microsoft/phi-2) model in `.safetensors` format, served through a FastAPI backend. No code is ever sent to external servers — ensuring total confidentiality.

This project is part of my learning journey into building AI-powered developer tools. Contributions, suggestions, and forks are welcome!

👉 **Live Demo**: [https://www.ravzzy.com/app/code-reviewer/home.html](https://www.ravzzy.com/app/code-reviewer/home.html)  
While you're there, do check out my other projects!

---

## 🚀 Features

- ✅ Local-only AI code review using Phi-2  
- ✅ FastAPI-powered backend  
- ✅ HTML/CSS/JS frontend (browser-based)  
- ✅ No data leaves your machine  
- ✅ Token-by-token streaming response  
- ✅ CORS-enabled testing  
- ✅ GPU availability check  
- ✅ Logs via `code_analysis.log`

---

## 📦 Prerequisites

- **Python** 3.8 or higher (recommended: 3.10)  
- Packages: `fastapi`, `uvicorn`, `transformers`, `torch`, `safetensors`

---

## 🛠️ Setup Instructions

### 🔄 Upgrade Python (if needed)

brew install python@3.10 python3.10 --version # should return Python 3.10.x

### 📦 Install Required Packages

python3.10 -m pip install --upgrade pip python3.10 -m pip install fastapi uvicorn transformers torch safetensors
python3.10 -m pip install --upgrade git+https://github.com/huggingface/transformers.git


---

## 📥 Download the Phi-2 Model

Head over to: https://huggingface.co/microsoft/phi-2/tree/main

### Required Files:

| File Name                          | Purpose                                      |
|-----------------------------------|----------------------------------------------|
| model-00001-of-00002.safetensors  | Main model file part 1                        |
| model-00002-of-00002.safetensors  | Main model file part 2                        |
| config.json                       | Defines model architecture                   |
| tokenizer.json                    | Tokenizer rules                              |
| tokenizer_config.json             | Extra tokenizer settings                     |
| special_tokens_map.json           | Maps tokens like <pad>, <eos>, etc.          |
| generation_config.json            | (Optional) generation defaults               |
| vocab.json, merges.txt            | (If applicable) for some tokenizers          |

📁 Place all of these into a `models/phi-2/` directory (or update your `server.py` path accordingly).

---

## 🧠 Create and Run the Server

Download the `server.py` file from the repo and update the models path:


Then start the server:

python3.10 -m uvicorn server:app --host 0.0.0.0 --port 8000


Server will be running at:  
http://localhost:8000

---

---

## 🎮 Check GPU Info

curl http://localhost:8000/gpu-info | jq


---

## 📜 View Logs to check the progress

tail -f code_analysis.log



---

## 💡 Contribute & Support

This is an open source project — you're free to fork, extend, and use it however you like.

☕ If you find this useful, consider supporting me:  
https://buymeacoffee.com/ravzzy

---

## 👨‍💻 Author

Created by [ravzzy](https://www.ravzzy.com) as part of my personal learning journey into AI-powered developer tools.

---

## 🛡️ License

MIT License – free to use, modify, and distribute.
