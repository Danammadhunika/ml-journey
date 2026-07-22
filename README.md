<div align="center">

# 🚀 Madhu's Machine Learning Journey
### From zero Python knowledge to deployed ML applications — built from scratch, one commit at a time.

![GitHub](https://img.shields.io/badge/GitHub-Danammadhunika-blue) ![Python](https://img.shields.io/badge/Python-3.11-green) ![Status](https://img.shields.io/badge/Status-Actively%20Building-brightgreen) ![Projects](https://img.shields.io/badge/Projects-4-orange)

</div>

---

## 👩‍💻 About Me

**Madhunika Danam** — Data Analyst · Python Developer · ML Engineer
📍 Connecticut, USA &nbsp;|&nbsp; 🎓 M.S. Computer Science, Sacred Heart University &nbsp;|&nbsp; STEM OPT Authorized
📧 danammadhunika@gmail.com &nbsp;|&nbsp; 🔗 [LinkedIn](https://linkedin.com/in/danammadhunika) &nbsp;|&nbsp; 💻 [GitHub](https://github.com/Danammadhunika)

I build real, end-to-end data and ML projects from scratch — no templates, no shortcuts. Every project is independently built, documented, and deployed live. Currently specializing in AI integration, backend development with FastAPI, and LLM-powered applications.

---

## 🌐 Projects at a Glance

| # | Project | Tech Stack | Status | Live Demo |
|---|---------|-----------|--------|-----------|
| 1 | 🚢 **Passenger Survival Risk Model** | Python · Scikit-learn · Logistic Regression | ✅ Complete | [Code →](https://github.com/Danammadhunika/ml-journey/tree/main/project_01_titanic) |
| 2 | 🎬 **Personalized Movie Recommendation Engine** | Python · Collaborative & Content-Based Filtering · Streamlit | ✅ Complete | **[▶️ Try Live App](https://madhu-movie-recommender.streamlit.app)** |
| 3 | 🛒 **E-commerce Revenue Intelligence Platform** | SQL · CTEs · Window Functions · SQLite | ✅ Complete | [Code →](https://github.com/Danammadhunika/ml-journey/tree/main/project_03_ecommerce_sql) |
| 4 | 🤖 **AI-Powered Resume Analyzer** | FastAPI · Anthropic Claude API · Prompt Engineering · Streamlit | ✅ Complete | **[▶️ Try Live App](https://madhu-resume-analyzer.streamlit.app)** |

---

## 🛠️ Skills & Tools

| Category | Skills |
|----------|--------|
| **Languages** | Python 3.11, SQL |
| **Data Analysis** | NumPy, Pandas |
| **Databases** | SQLite — SELECT, JOINs, Subqueries, CTEs, Window Functions, LAG/LEAD |
| **Machine Learning** | Scikit-learn, Logistic Regression, Cosine Similarity |
| **Recommendation Systems** | Collaborative Filtering, Content-Based Filtering, Hybrid Models |
| **Visualization** | Matplotlib, Seaborn |
| **Web & APIs** | FastAPI, Streamlit, RESTful APIs, Pydantic, Uvicorn |
| **AI Integration** | Anthropic Claude API, LLM APIs, Prompt Engineering, JSON output structuring |
| **Deployment** | Render (FastAPI backend), Streamlit Cloud (frontend) |
| **Tools** | Git, GitHub (daily commits), VS Code, Jupyter Notebook, Anaconda |

---

## 📊 Project 1 — Passenger Survival Risk Model
**Status: ✅ Complete**

Built a classification model to predict passenger survival using the classic Titanic dataset — my first end-to-end ML project.

| Property | Value |
|----------|-------|
| Dataset | Kaggle Titanic — 891 passengers, 12 features |
| Model | Logistic Regression |
| Accuracy | **81%** (145/179 correct) |
| Key Insight | Female survival rate 74% vs Male 19%; 1st Class 63% vs 3rd Class 24% |

**What I built:** Cleaned 177+ missing Age values → encoded categorical features → conducted EDA → engineered features → trained and evaluated a Logistic Regression classifier using a confusion matrix and classification report.

`Python` `Pandas` `NumPy` `Matplotlib` `Scikit-learn`

<details>
<summary>📅 View daily build log</summary>

| Day | Topic | Status |
|-----|-------|--------|
| Day 1 | NumPy arrays, indexing, applied to Titanic age data | ✅ |
| Day 2 | NumPy 2D arrays, statistical operations | ✅ |
| Day 3 | Pandas — loaded dataset, EDA, cleaned missing values | ✅ |
| Day 4 | Data analysis — survival patterns by gender, class, age | ✅ |
| Day 5 | Data visualization — 7 charts created | ✅ |
| Day 6 | Feature engineering — text to numbers | ✅ |
| Day 7 | Logistic Regression model — 81% accuracy | ✅ |
| Day 8 | Model evaluation — confusion matrix, classification report | ✅ |

</details>

---

## 🎬 Project 2 — Personalized Movie Recommendation Engine
**Status: ✅ Complete &nbsp;|&nbsp; 🌐 [Try the Live App](https://madhu-movie-recommender.streamlit.app)**

A Netflix-style recommendation engine using three algorithms, deployed as a live, publicly accessible web app.

| Property | Value |
|----------|-------|
| Dataset | MovieLens 100K — 100,000 ratings, 943 users, 1,682 movies |
| Algorithms | Collaborative Filtering, Content-Based Filtering, Hybrid Model |
| Deployment | Live on Streamlit Cloud |

**What I built:** Built a 943×943 user similarity matrix using Cosine Similarity → built genre-based content filtering → combined both into a hybrid model → deployed as an interactive web app where users enter an ID and instantly receive personalized recommendations.

`Python` `Pandas` `Scikit-learn` `Seaborn` `Streamlit`

<details>
<summary>📅 View daily build log</summary>

| Day | Topic | Status |
|-----|-------|--------|
| Day 1 | Loaded MovieLens 100K data, explored ratings & movies | ✅ |
| Day 2 | Data visualization — rating distribution, top movies | ✅ |
| Day 3 | Collaborative Filtering — user similarity matrix | ✅ |
| Day 4 | Content-Based Filtering — genre similarity | ✅ |
| Day 5 | Hybrid Model — combined both algorithms | ✅ |
| Day 6 | Streamlit web app — built interface | ✅ |
| Day 7 | Deployed to Streamlit Cloud — live app! | ✅ |

</details>

---

## 🛒 Project 3 — E-commerce Revenue Intelligence Platform
**Status: ✅ Complete**

Advanced SQL analysis on over half a million real e-commerce transactions — built and queried entirely like a working Data Analyst.

| Property | Value |
|----------|-------|
| Dataset | UCI Online Retail — 541,909 transactions, 38 countries |
| Database | SQLite |
| Total Revenue Analyzed | £9.7M |

**Key findings:**

| Category | Finding |
|----------|---------|
| Peak Month | November 2011 — £1,509,496 |
| Top Country | UK — 89.9% of total revenue (concentration risk flagged) |
| Top VIP Customer | Customer 14646 — £280,206 spent |
| Star Product | REGENCY CAKESTAND — £174,484 revenue |
| Guest Checkouts | 24.93% — flagged as retention opportunity |
| Highest AOV | Netherlands — £120/order vs UK £25/order |

**What I built:** Loaded 541,909 rows into SQLite → wrote SQL across SELECT/JOIN/Subqueries/CASE WHEN → applied CTEs, Window Functions (DENSE_RANK, PARTITION BY), and LAG/LEAD to rank VIP customers and track revenue trends → built 6 professional visualizations → delivered business recommendations.

`Python` `SQL` `SQLite` `Pandas` `Matplotlib` `Seaborn`

<details>
<summary>📅 View daily build log (28 days)</summary>

**Week 1 — SQL Foundations**
| Day | Topic | Status |
|-----|-------|--------|
| Day 1 | SQLite setup, loaded 541,909 rows, first queries | ✅ |
| Day 2 | WHERE, AND, OR, NULL handling | ✅ |
| Day 3 | ORDER BY, LIMIT, DISTINCT, text functions | ✅ |
| Day 4 | GROUP BY, COUNT, SUM, AVG | ✅ |
| Day 5 | HAVING clause, WHERE vs HAVING | ✅ |
| Day 6 | Business questions answered with SQL | ✅ |
| Day 7 | Review + GitHub | ✅ |

**Week 2 — JOINs, Subqueries, CASE WHEN**
| Day | Topic | Status |
|-----|-------|--------|
| Day 8 | INNER JOIN | ✅ |
| Day 9 | LEFT JOIN — all 38 countries revealed | ✅ |
| Day 10 | Subqueries — nested queries | ✅ |
| Day 11 | CASE WHEN | ✅ |
| Day 12 | Date Functions — strftime, substr | ✅ |
| Day 13 | Project application day — 8 business queries | ✅ |
| Day 14 | Review + GitHub | ✅ |

**Week 3 — Advanced SQL + Python Integration**
| Day | Topic | Status |
|-----|-------|--------|
| Day 15 | CTEs — WITH clause | ✅ |
| Day 16 | Window Functions — ROW_NUMBER, RANK, DENSE_RANK, PARTITION BY | ✅ |
| Day 17 | LAG and LEAD functions — monthly revenue trends | ✅ |
| Day 18 | Python + SQLite — to_sql, summary tables | ✅ |
| Day 19 | Pandas + SQL + Visualizations — 4 charts | ✅ |
| Day 20 | Full Analysis Day — VIP customers, trends, country tiers | ✅ |
| Day 21 | Review + GitHub — Project 3 Complete! | ✅ |

**Week 4 — Portfolio Finishing**
| Day | Topic | Status |
|-----|-------|--------|
| Day 22 | Notebook cleanup | ✅ |
| Day 23 | 6 professional visualizations | ✅ |
| Day 24 | Business insights and recommendations | ✅ |
| Day 25 | Presentation deck created | ✅ |
| Day 26 | Complete notes document | ✅ |
| Day 27 | Resume updated | ✅ |
| Day 28 | Cover letter + LinkedIn fully updated | ✅ |

</details>

---

## 🤖 Project 4 — AI-Powered Resume Analyzer
**Status: ✅ Complete &nbsp;|&nbsp; 🌐 [Try the Live App](https://madhu-resume-analyzer.streamlit.app)**

A production-ready, full-stack AI application that analyzes a resume against a job description using Claude AI — returning a match score, missing keywords, and actionable improvement suggestions. Built from scratch in 14 days.

| Property | Value |
|----------|-------|
| Backend | FastAPI + Python — deployed on Render |
| AI Layer | Anthropic Claude API (claude-sonnet-4-6) |
| Frontend | Streamlit — deployed on Streamlit Cloud |
| File Upload | pdfplumber — extracts text from PDF resumes |
| Live Backend | https://ml-journey.onrender.com |
| Live Frontend | https://madhu-resume-analyzer.streamlit.app |

**What it does:**
- Upload a PDF resume or paste resume text
- Paste any job description from any job board
- Get an AI-powered match score (0–100) with color-coded progress bar
- See exactly which keywords are missing from your resume
- Get one specific, actionable suggestion to improve your resume for that role

**Tech concepts demonstrated:**
- REST API design with FastAPI (GET + POST routes, Pydantic data validation)
- Prompt engineering — structured JSON output from LLM API
- Full stack integration — Streamlit frontend calling FastAPI backend via HTTP
- PDF text extraction with pdfplumber
- Robust error handling (ConnectionError, Timeout, empty input validation, JSON parsing)
- Secure environment variable management (.env + python-dotenv)
- Cloud deployment — FastAPI on Render, Streamlit on Streamlit Cloud

**How to run locally:**

Terminal 1 — Start the backend:
```bash
cd backend
uvicorn main:app --reload
```

Terminal 2 — Start the frontend:
```bash
cd frontend
streamlit run app.py
```

`Python` `FastAPI` `Anthropic Claude API` `Prompt Engineering` `Streamlit` `pdfplumber` `Pydantic` `REST API` `Render` `Streamlit Cloud`

<details>
<summary>📅 View daily build log</summary>

| Day | Topic | Status |
|-----|-------|--------|
| Day 1 | Project structure, virtual environment, FastAPI + Uvicorn installed | ✅ |
| Day 2 | First FastAPI route (`/`) — GET requests, decorators, JSON responses, tested via Swagger docs | ✅ |
| Day 3 | Path parameters (`/hello/{name}`) — dynamic routes, `datetime`, time-based greeting logic | ✅ |
| Day 4 | POST route + Pydantic BaseModel (ResumeRequest with resume_text and job_description fields) | ✅ |
| Day 5 | Anthropic API integrated — Claude analyzes resume vs job description, returns match score, missing keywords, and improvement suggestion | ✅ |
| Day 6 | Prompt engineering — rewrote prompt to force structured JSON output (match_score, missing_keywords, suggestion), added json.loads() parsing | ✅ |
| Day 7 | Built Streamlit frontend — full stack app working end to end (resume input → FastAPI → Claude → results displayed) | ✅ |
| Day 8 | Error handling added — ConnectionError, Timeout, empty input validation | ✅ |
| Day 9 | PDF resume upload added using pdfplumber, JSON parsing fix for code fences, error handling improved | ✅ |
| Day 10 | UI polish — progress bar, color-coded match score, keyword badge styling, dividers, footer | ✅ |
| Day 11 | End to end testing — all 5 scenarios tested and passing | ✅ |
| Day 12 | Final README writeup, code cleanup | ✅ |
| Day 13 | Full deployment — FastAPI on Render, Streamlit on Streamlit Cloud — app live! | ✅ |
| Day 14 | Resume bullet written, LinkedIn post published | ✅ |

</details>

---

## 🎯 Roadmap

- [x] Passenger Survival Risk Model — Logistic Regression
- [x] Personalized Movie Recommendation Engine — Deployed
- [x] E-commerce Revenue Intelligence Platform — Advanced SQL
- [x] AI-Powered Resume Analyzer — FastAPI + Claude API — **Live** 🚀
- [ ] Advanced ML — Random Forest, Feature Engineering
- [ ] RAG Systems + Vector Databases
- [ ] AI Engineer 🚀

---

## 📬 Contact

📧 **Email:** danammadhunika@gmail.com &nbsp;|&nbsp; 💼 **LinkedIn:** [linkedin.com/in/danammadhunika](https://linkedin.com/in/danammadhunika) &nbsp;|&nbsp; 📍 **Location:** Connecticut, USA

<div align="center">

*Every commit in this repository represents a real learning session. Built from scratch — no shortcuts. 💪*

</div>