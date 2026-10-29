# Fake-News-Deepfake-Detection-Hub

## 🛡️ Fake News & Deepfake Detection Hub

An AI-powered platform designed to detect misinformation and AI-generated media by analyzing news articles, images, videos, and audio. The system combines Natural Language Processing (NLP), Computer Vision, and Deep Learning to identify fake news, deepfake content, and cloned voices while providing confidence scores and explainable AI insights.

---

### ✨ Key Features
- 📰 **Fake News Detection:** NLP pipeline using Groq Cloud LLaMA-3.3 70B & Transformer linguistics.
- 🖼️ **Deepfake Image Detection:** Error Level Analysis (ELA) and high-frequency noise variance scanning.
- 🎥 **Deepfake Video Detection:** Temporal facial warping and boundary inconsistency inspection across sampled frames.
- 🎙️ **AI Voice Clone Detection:** Acoustic speech analysis identifying synthetic vocoder artifacts.
- 🔍 **Fact-Checking Engine:** Evidence aggregation and cross-referencing against trusted journalistic bodies.
- 📊 **Interactive Analytics Dashboard:** Telemetry tracking total scans, threat ratios, and model accuracy.
- 🗄️ **MongoDB Atlas Integration:** Document persistence for submissions, predictions, fact-checks, and audit logs.
- 🔐 **Dual Database & Auth Security:** JWT tokens, bcrypt password hashing, and ownership access control.

---

### 🛠️ Tech Stack
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Lucide Icons, Axios
- **Backend:** FastAPI, Python 3.12, Pydantic v2, Motor (PyMongo Async)
- **AI/ML:** PyTorch, TensorFlow, Hugging Face Transformers, OpenCV, Scikit-learn, Groq Cloud API
- **Databases:** MongoDB Atlas (Document Store) & PostgreSQL/SQLite (Relational Engine)
- **Testing:** Pytest, Pytest-Asyncio, Mongomock-Motor

---

### 🗄️ MongoDB Atlas Setup & Configuration

1. **Create MongoDB Atlas Cluster:**
   - Log in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
   - Create a free shared cluster (M0).
   - Create a database user with read/write privileges.
   - Whitelist your IP address (or `0.0.0.0/0` for deployment on Render/AWS).

2. **Configure Environment Variables:**
   Add your MongoDB connection string in `.env` (or Render Environment Settings):
   ```env
   # MongoDB Atlas Connection URI
   MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DATABASE=fake_news_deepfake_hub

   # AI Inference Key
   GROQ_API_KEY=gsk_your_groq_api_key_here

   # Security
   SECRET_KEY=your_secure_random_jwt_secret_key
   ```

3. **Collections & Schemas:**
   - **`users`:** `_id`, `name`, `email` (unique index), `password_hash`, `role`, `created_at`
   - **`submissions`:** `_id`, `user_id`, `content_type` (`news` | `image` | `video` | `audio`), `original_text`, `file_reference`, `source_url`, `submitted_at`, `processing_status`
   - **`predictions`:** `_id`, `submission_id`, `user_id`, `detection_type`, `predicted_label`, `confidence_score` (0.0 to 1.0), `model_name`, `model_version`, `explanation`, `created_at`
   - **`fact_checks`:** `_id`, `submission_id`, `claim`, `verdict`, `supporting_sources`, `contradictory_sources`, `checked_at`
   - **`audit_logs`:** `_id`, `user_id`, `action`, `resource_type`, `resource_id`, `created_at`

4. **Migrate Existing SQLite Data (Optional):**
   If you have existing analyses or users stored in SQLite (`truthguard.db`), migrate them safely to MongoDB Atlas without data loss:
   ```bash
   cd backend
   python -m app.database.migrate_to_mongo
   ```

---

### 🚀 Running the Project

#### 1. Backend (FastAPI)
```bash
cd backend
# Activate Python 3.12 virtual environment
.\venv312\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate       # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

#### 2. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### 🧪 Running Automated Tests
Run the test suite verifying database connectivity, CRUD operations, authorization, and error handling:
```bash
pytest backend/tests -v
```

---

### 📡 Core REST API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Comprehensive health check (MongoDB, AI engine, and SQL) |
| `POST` | `/api/submissions` | Create a new content submission |
| `GET` | `/api/submissions` | List user's submissions (supports pagination & filtering) |
| `GET` | `/api/submissions/{id}` | Retrieve a submission with predictions and fact-checks |
| `DELETE` | `/api/submissions/{id}` | Delete submission and cascade-delete associated predictions |
| `POST` | `/api/predictions` | Save a completed AI prediction |
| `GET` | `/api/submissions/{id}/predictions` | Retrieve prediction history for a submission |
| `GET` | `/api/dashboard/analytics` | Aggregated analytics from MongoDB collections |
| `POST` | `/api/v1/analyze/text` | Detect fake news and misinformation with Groq LLaMA |
| `POST` | `/api/v1/analyze/image` | Run forensic ELA & generative AI artifact scan |
| `POST` | `/api/v1/analyze/video` | Scan sampled frames for temporal facial deepfakes |
| `POST` | `/api/v1/analyze/audio` | Detect synthetic voice clone patterns |
| `POST` | `/api/v1/factcheck` | Cross-reference claims against reputable journalistic sources |
