# 🎓 Document Analyzer API — R.S Education Solution

An AI-powered academic document analyzer built with FastAPI + EasyOCR + Groq AI.  
Upload a marksheet, certificate, or resume and get instant course eligibility recommendations.

---

## 🚀 Deploy on Render (Step-by-Step)

### 1. Push to GitHub

```bash
git add -A
git commit -m "feat: prepare for Render deployment"
git push origin main
```

### 2. Create a New Web Service on Render

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub repository**
4. Use these settings:

| Setting | Value |
|---|---|
| **Name** | `document-analyzer-api` |
| **Runtime** | `Python 3` |
| **Build Command** | `chmod +x build.sh && ./build.sh` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1` |
| **Plan** | Free |

### 3. Set Environment Variables in Render Dashboard

Go to **Environment** tab and add:

| Key | Value |
|---|---|
| `GROQ_API_KEY` | `your_groq_api_key_here` ⚠️ |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` |
| `APP_NAME` | `R.S Education Document Analyzer` |
| `APP_VERSION` | `1.0.0` |
| `TEMP_DIR` | `/tmp/uploads` |
| `MAX_FILE_SIZE` | `10485760` |

> ⚠️ **Never commit `.env` to GitHub.** Always set `GROQ_API_KEY` manually in the Render dashboard.

### 4. Deploy

Click **"Create Web Service"** — Render will:
1. Install all dependencies
2. Pre-download EasyOCR models (via `build.sh`)
3. Start the server

Your live URL will be: `https://document-analyzer-api.onrender.com`

---

## 🧪 Local Development

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env       # Edit with your keys

# Start server
uvicorn app.main:app --reload
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 📁 Project Structure

```
document-analyzer-api/
├── app/
│   ├── main.py              # FastAPI app + routes
│   ├── config.py            # Settings & environment variables
│   ├── models/
│   │   └── schemas.py       # Pydantic response models
│   ├── services/
│   │   ├── ai_service.py    # Groq AI analysis
│   │   └── ocr_service.py   # EasyOCR text extraction
│   └── utils/
│       └── file_handler.py  # File validation & cleanup
├── static/
│   ├── index.html           # Frontend UI
│   └── style.css            # Claymorphism styles
├── build.sh                 # Render build script (pre-downloads OCR models)
├── render.yaml              # Render deployment blueprint
├── runtime.txt              # Python version pin
├── requirements.txt         # Pinned dependencies
└── .gitignore               # Excludes .env, venv, temp/
```

---

## 🔒 Security Notes

- `.env` is **never committed** to git (in `.gitignore`)
- API keys are set via **Render environment variables** only
- Uploaded files are **automatically deleted** after analysis
- Temp files use `/tmp/uploads` (ephemeral, safe on Render)