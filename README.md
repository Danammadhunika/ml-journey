# 🚀 Madhu's Machine Learning Journey

From zero Python knowledge to deployed ML and AI applications — built from scratch, one commit at a time.

![GitHub](https://img.shields.io/badge/GitHub-Danammadhunika-181717?logo=github) ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![Status](https://img.shields.io/badge/Status-Actively%20Building-brightgreen) ![Projects](https://img.shields.io/badge/Projects-5-orange)

## 👩‍💻 About Me

**Madhunika Danam** — Data Analyst · Python Developer · ML Engineer
📍 Connecticut, USA &nbsp;|&nbsp; 🎓 M.S. Computer Science, Sacred Heart University &nbsp;|&nbsp; STEM OPT Authorized
📧 danammadhunika@gmail.com &nbsp;|&nbsp; 🔗 [LinkedIn](https://linkedin.com/in/danammadhunika) &nbsp;|&nbsp; 💻 [GitHub](https://github.com/Danammadhunika)

I build real, end-to-end data and AI projects from scratch — no templates, no shortcuts. Every project is independently built, documented, and either deployed live or fully tested locally. Currently specializing in AI integration, backend development with FastAPI, and LLM-powered applications.

## 🌐 Projects at a Glance

| # | Project | Tech Stack | Status | Live Demo |
|---|---------|-----------|--------|-----------|
| 1 | 🚢 Passenger Survival Risk Model | Python · Scikit-learn · Logistic Regression | ✅ Complete | [Code →](#-project-1--passenger-survival-risk-model) |
| 2 | 🎬 Personalized Movie Recommendation Engine | Python · Collaborative & Content-Based Filtering · Streamlit | ✅ Complete | ▶️ [Try Live App](#) |
| 3 | 🛒 E-commerce Revenue Intelligence Platform | SQL · CTEs · Window Functions · SQLite | ✅ Complete | [Code →](#-project-3--e-commerce-revenue-intelligence-platform) |
| 4 | 🤖 AI-Powered Resume Analyzer | FastAPI · Anthropic Claude API · Prompt Engineering · Streamlit | ✅ Complete | ▶️ [Try Live App](#) |
| 5 | 🧭 AI Job Search & Application Agent | Python · Typer · SQLAlchemy · Anthropic Claude API · Adzuna API | ✅ Complete | [Code →](#-project-5--ai-job-search--application-agent) |

## 🛠️ Skills & Tools

| Category | Skills |
|----------|--------|
| Languages | Python 3.11, SQL |
| Data Analysis | NumPy, Pandas |
| Databases | SQLite — SELECT, JOINs, Subqueries, CTEs, Window Functions, LAG/LEAD; SQLAlchemy ORM |
| Machine Learning | Scikit-learn, Logistic Regression, Cosine Similarity |
| Recommendation Systems | Collaborative Filtering, Content-Based Filtering, Hybrid Models |
| Visualization | Matplotlib, Seaborn |
| Web & APIs | FastAPI, Streamlit, RESTful APIs, Pydantic, Uvicorn, Typer (CLI) |
| AI Integration | Anthropic Claude API, LLM APIs, Prompt Engineering, structured JSON output, fact-checking generated text against a source of truth |
| Third-Party APIs | GitHub REST API, Adzuna Job Search API |
| Document Generation | PDF export (ReportLab), Excel export (openpyxl) |
| Testing | pytest (180+ automated tests across all projects) |
| Deployment | Render (FastAPI backend), Streamlit Cloud (frontend) |
| Tools | Git, GitHub (daily commits), VS Code, Jupyter Notebook, Anaconda |

---

## 📊 Project 1 — Passenger Survival Risk Model

**Status:** ✅ Complete

Built a classification model to predict passenger survival using the classic Titanic dataset — my first end-to-end ML project.

| Property | Value |
|----------|-------|
| Dataset | Kaggle Titanic — 891 passengers, 12 features |
| Model | Logistic Regression |
| Accuracy | 81% (145/179 correct) |
| Key Insight | Female survival rate 74% vs. male 19%; 1st class 63% vs. 3rd class 24% |

**What I built:** Cleaned 177+ missing `Age` values, encoded categorical features, conducted exploratory data analysis, engineered new features, then trained and evaluated a Logistic Regression classifier using a confusion matrix and classification report.

`Python` `Pandas` `NumPy` `Matplotlib` `Scikit-learn`

📅 [View daily build log](#)

---

## 🎬 Project 2 — Personalized Movie Recommendation Engine

**Status:** ✅ Complete &nbsp;|&nbsp; 🌐 [Try the Live App](#)

A Netflix-style recommendation engine using three algorithms, deployed as a live, publicly accessible web app.

| Property | Value |
|----------|-------|
| Dataset | MovieLens 100K — 100,000 ratings, 943 users, 1,682 movies |
| Algorithms | Collaborative Filtering, Content-Based Filtering, Hybrid Model |
| Deployment | Live on Streamlit Cloud |

**What I built:** Built a 943×943 user similarity matrix using Cosine Similarity, built genre-based content filtering, combined both into a hybrid model, then deployed it as an interactive web app where a user enters an ID and instantly receives personalized recommendations.

`Python` `Pandas` `Scikit-learn` `Seaborn` `Streamlit`

📅 [View daily build log](#)

---

## 🛒 Project 3 — E-commerce Revenue Intelligence Platform

**Status:** ✅ Complete

Advanced SQL analysis on over half a million real e-commerce transactions — built and queried entirely like a working data analyst.

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
| Guest Checkouts | 24.93% — flagged as a retention opportunity |
| Highest AOV | Netherlands — £120/order vs. UK £25/order |

**What I built:** Loaded 541,909 rows into SQLite, wrote SQL across `SELECT`/`JOIN`/subqueries/`CASE WHEN`, applied CTEs, window functions (`DENSE_RANK`, `PARTITION BY`), and `LAG`/`LEAD` to rank VIP customers and track revenue trends, then built six professional visualizations and delivered business recommendations.

`Python` `SQL` `SQLite` `Pandas` `Matplotlib` `Seaborn`

📅 [View daily build log (28 days)](#)

---

## 🤖 Project 4 — AI-Powered Resume Analyzer

**Status:** ✅ Complete &nbsp;|&nbsp; 🌐 [Try the Live App](#)

A production-ready, full-stack AI application that analyzes a resume against a job description using Claude AI — returning a match score, missing keywords, and actionable improvement suggestions. Built from scratch in 14 days.

| Property | Value |
|----------|-------|
| Backend | FastAPI + Python — deployed on Render |
| AI Layer | Anthropic Claude API (`claude-sonnet-4-6`) |
| Frontend | Streamlit — deployed on Streamlit Cloud |
| File Upload | pdfplumber — extracts text from PDF resumes |
| Live Backend | https://ml-journey.onrender.com |
| Live Frontend | https://madhu-resume-analyzer.streamlit.app |

**What it does:**
- Upload a PDF resume or paste resume text
- Paste any job description from any job board
- Get an AI-powered match score (0–100) with a color-coded progress bar
- See exactly which keywords are missing from your resume
- Get one specific, actionable suggestion to improve your resume for that role

**Tech concepts demonstrated:** REST API design with FastAPI (GET + POST routes, Pydantic data validation) · prompt engineering with structured JSON output from an LLM · full-stack integration (Streamlit frontend calling a FastAPI backend over HTTP) · PDF text extraction with pdfplumber · robust error handling (connection errors, timeouts, empty-input validation, JSON parsing) · secure environment variable management (`.env` + python-dotenv) · cloud deployment (FastAPI on Render, Streamlit on Streamlit Cloud).

**How to run locally:**
```bash
# Terminal 1 — start the backend
cd backend
uvicorn main:app --reload

# Terminal 2 — start the frontend
cd frontend
streamlit run app.py
```

`Python` `FastAPI` `Anthropic Claude API` `Prompt Engineering` `Streamlit` `pdfplumber` `Pydantic` `REST API` `Render` `Streamlit Cloud`

📅 [View daily build log](#)

---

## 🧭 Project 5 — AI Job Search & Application Agent

**Status:** ✅ Complete

A command-line agent that automates the repetitive, time-consuming parts of a real job search — searching, scoring, drafting tailored materials, and tracking every application's pipeline — while keeping every decision and every submission in the user's hands. Built after running it against real, live job postings and using it to track real applications end to end.

| Property | Value |
|----------|-------|
| Interface | Python CLI (Typer) |
| AI Layer | Anthropic Claude API — job matching, resume tailoring, cover letters, recruiter outreach |
| Job Search | Adzuna public job search API (real, live postings — not scraped) |
| Database | SQLite + SQLAlchemy — application tracker with recruiter, screening, interview, and follow-up history |
| Output | Tailored resume & cover letter as PDF (ReportLab), full tracker export to Excel (openpyxl) |
| Testing | 100+ automated tests (pytest), all passing |

**What it does:**
- Searches real, live job postings and scores each one (0–100) against a master resume across technical skills, experience, education, seniority, and location
- Automatically drafts a tailored resume, cover letter, and recruiter outreach message — as PDFs — for any posting that clears a configurable match-score threshold
- Independently fact-checks every specific claim in a drafted resume or cover letter against the real master resume before showing it, so nothing about a candidate's experience is ever invented
- Tracks each application's real status (applied, recruiter contacted, screening, interview scheduled/completed, offer, etc.), automatically updating the existing record instead of creating a duplicate when the same company is mentioned again
- Exports the full application tracker to a spreadsheet
- Imports a real GitHub repository and drafts a fact-checked resume/LinkedIn project entry from its actual code and README (this is literally how "ml-journey" and "AI-Powered Resume Analyzer" became resume entries)
- Logs day-to-day skill practice separately from the resume, only adding a skill to the resume once it's a genuinely confident, demonstrated skill — never on a single mention

**Hard rule built into the system:** it never submits an application, sends a message, or fabricates a qualification, skill, or metric — every output is a draft for human review and explicit approval before anything leaves the tool.

**Tech concepts demonstrated:** agentic system design with per-agent Pydantic schemas · prompt engineering with structured, validated LLM output · fact-checking generated text against a verified source of truth · SQLAlchemy schema migrations on a live database · REST API integration (Anthropic, GitHub, Adzuna) · PDF generation · Excel export · CLI design with Typer.

`Python` `Typer` `SQLAlchemy` `Anthropic Claude API` `Adzuna API` `ReportLab` `Pydantic` `pytest`

📅 [View daily build log](#)

---

## 🎯 Roadmap

- [x] Passenger Survival Risk Model — Logistic Regression
- [x] Personalized Movie Recommendation Engine — Deployed
- [x] E-commerce Revenue Intelligence Platform — Advanced SQL
- [x] AI-Powered Resume Analyzer — FastAPI + Claude API — Live 🚀
- [x] AI Job Search & Application Agent — CLI automation for job search, matching, tailored materials, and pipeline tracking
- [ ] Advanced ML — Random Forest, Feature Engineering
- [ ] RAG Systems + Vector Databases
- [ ] AI Engineer 🚀

## 📬 Contact

📧 Email: danammadhunika@gmail.com &nbsp;|&nbsp; 💼 LinkedIn: [linkedin.com/in/danammadhunika](https://linkedin.com/in/danammadhunika) &nbsp;|&nbsp; 📍 Location: Connecticut, USA

*Every commit in this repository represents a real learning session. Built from scratch — no shortcuts.* 💪