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

I build real, end-to-end data and ML projects from scratch — no templates, no shortcuts. Every project below is independently built, documented, and (where possible) deployed live for anyone to try. Currently expanding into backend development and AI integration with FastAPI and LLM APIs.

---

## 🌐 Projects at a Glance

| # | Project | Tech Focus | Status | Live Demo |
|---|---------|-----------|--------|-----------|
| 1 | 🚢 **Passenger Survival Risk Model** | Python · Scikit-learn · Logistic Regression | ✅ Complete | [Code →](https://github.com/Danammadhunika/ml-journey/tree/main/project_01_titanic) |
| 2 | 🎬 **Personalized Movie Recommendation Engine** | Python · Collaborative & Content-Based Filtering | ✅ Complete | **[▶️ Try Live App](https://madhu-movie-recommender.streamlit.app)** |
| 3 | 🛒 **E-commerce Revenue Intelligence Platform** | SQL · CTEs · Window Functions · SQLite | ✅ Complete | [Code →](https://github.com/Danammadhunika/ml-journey/tree/main/project_03_ecommerce_sql) |
| 4 | 🤖 **AI-Powered Resume Analyzer** | FastAPI · LLM API · Prompt Engineering | 🚧 In Progress | Coming Soon |

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
| **Web & APIs** | Streamlit (deployed live app), FastAPI, RESTful APIs *(in progress)* |
| **AI Integration** | LLM APIs, Prompt Engineering *(in progress)* |
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
**Status: 🚧 In Progress**

Building a full-stack application that uses an LLM API to analyze a resume against a job description and suggest improvements — my first project combining backend development with AI integration.

| Property | Value |
|----------|-------|
| Backend | FastAPI |
| AI Layer | LLM API + Prompt Engineering |
| Frontend | Streamlit |
| Goal | Deployed, end-to-end AI application |

**Tech stack in progress:** FastAPI · Python · LLM API · Prompt Engineering · JSON · Streamlit

<details>
<summary>📅 View daily build log</summary>

| Day | Topic | Status |
|-----|-------|--------|
| Day 1 | Project structure, virtual environment, FastAPI + Uvicorn installed | ✅ |
| Day 2 | First FastAPI route (`/`) — GET requests, decorators, JSON responses, tested via Swagger docs | ✅ |
| Day 3 | Path parameters (`/hello/{name}`) — dynamic routes, `datetime`, time-based greeting logic | ✅ |
| Day 4 | POST requests, Pydantic BaseModel, ResumeRequest class with resume_text and job_description fields, tested via Swagger docs | ✅ |
| Day 5 | Anthropic API integrated — Claude analyzes resume vs job description, returns match score, missing keywords, and improvement suggestion | ✅ |
| Day 6 | Prompt engineering — rewrote prompt to force structured JSON output (match_score, missing_keywords, suggestion), added json.loads() parsing | ✅ |
| Day 7 | Built Streamlit frontend — full stack app working end to end (resume input → FastAPI → Claude → results displayed) | ✅ |

*Updated as the project progresses.*

</details>

---

## 🎯 Roadmap

- [x] Passenger Survival Risk Model — Logistic Regression
- [x] Personalized Movie Recommendation Engine — Deployed
- [x] E-commerce Revenue Intelligence Platform — Advanced SQL
- [ ] AI-Powered Resume Analyzer — FastAPI + LLM API *(in progress)*
- [ ] Advanced ML — Random Forest, Feature Engineering
- [ ] RAG Systems + Vector Databases
- [ ] AI Engineer 🚀

---

## 📬 Contact

📧 **Email:** danammadhunika@gmail.com &nbsp;|&nbsp; 💼 **LinkedIn:** [linkedin.com/in/danammadhunika](https://linkedin.com/in/danammadhunika) &nbsp;|&nbsp; 📍 **Location:** Connecticut, USA

<div align="center">

*Every commit in this repository represents a real learning session. Built from scratch — no shortcuts. 💪*

</div>