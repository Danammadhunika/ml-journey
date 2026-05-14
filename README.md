# 🚀 Madhu's Machine Learning Journey

> *From Python basics to production ML apps — built from scratch, committed every day.*

[![GitHub](https://img.shields.io/badge/GitHub-Danammadhunika-blue?style=flat&logo=github)](https://github.com/Danammadhunika/ml-journey)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)
![Projects](https://img.shields.io/badge/Projects-2%20Complete-success?style=flat)

---

## 👩‍💻 About Me

**Madhunika Danam** — Aspiring Data Scientist & ML Engineer
📍 Connecticut, USA | 🎓 STEM OPT Student
📧 danammadhunika@gmail.com
🔗 [GitHub](https://github.com/Danammadhunika/ml-journey)

I am actively building real-world machine learning projects from scratch to strengthen my portfolio and transition into a Data Science / ML role in the US. Every project in this repository was built step by step — no shortcuts, no templates.

---

## 🌐 Live Projects

| # | Project | Status | Live Demo | GitHub |
|---|---------|--------|-----------|--------|
| 1 | 🚢 Titanic Survival Prediction | ✅ Complete | Coming Soon | [View Code](https://github.com/Danammadhunika/ml-journey/tree/main/project_01_titanic) |
| 2 | 🎬 Movie Recommendation Engine | ✅ Complete | [▶️ Try Live App!](https://madhu-movie-recommender.streamlit.app/) | [View Code](https://github.com/Danammadhunika/ml-journey/tree/main/project_02_movie_recommender) |

---

## 🗂️ Repository Structure

```
ML_journey/
├── project_01_titanic/               ✅ Complete
│   ├── datasets/                     → train.csv, test.csv
│   ├── notebooks/                    → titanic_exploration.ipynb
│   ├── projects/                     → final Python scripts
│   └── notes/                        → PDF notes + PPT presentation
│
├── project_02_movie_recommender/     ✅ Complete
│   ├── datasets/                     → MovieLens 100K data
│   ├── notebooks/                    → movie_recommender.ipynb
│   └── projects/                     → app.py (Streamlit web app)
│
└── README.md
```

---

## 📊 Project 1: Titanic Survival Prediction

**Status: ✅ Complete**

> Predicting which passengers survived the Titanic using real historical data and machine learning.

### Dataset
| Property | Value |
|----------|-------|
| Source | Kaggle — Titanic: Machine Learning from Disaster |
| Size | 891 passengers, 12 features |
| Target | Survived (0 = Died, 1 = Survived) |

### What I Built
| Step | Task | Tool |
|------|------|------|
| 1 | Loaded & explored real passenger data | Pandas |
| 2 | Cleaned missing values — Age (177), Cabin (687), Embarked (2) | Pandas |
| 3 | Analyzed survival patterns by gender, class, age | Pandas, NumPy |
| 4 | Created 7 data visualizations | Matplotlib |
| 5 | Feature engineering — converted text columns to numbers | Pandas |
| 6 | Built Logistic Regression model | Scikit-learn |
| 7 | Evaluated with confusion matrix & classification report | Scikit-learn |

### Key Findings
| Analysis | Finding |
|----------|---------|
| Overall survival | Only **38.4%** survived (342 of 891) |
| By gender | Female **74%** vs Male **19%** |
| By class | 1st Class **63%** vs 3rd Class **24%** |
| Best case | Female 1st Class → **97%** survival |
| Worst case | Male 3rd Class → **14%** survival |
| By age | Children **58%** vs Seniors **23%** |

### Model Performance
| Metric | Score |
|--------|-------|
| **Overall Accuracy** | **81%** |
| Precision — Died | 83% |
| Precision — Survived | 79% |
| Correct Predictions | 145 / 179 |
| Confusion Matrix | [[90, 15], [19, 55]] |

### Technologies
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat&logo=numpy)
![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat&logo=pandas)
![Matplotlib](https://img.shields.io/badge/-Matplotlib-11557c?style=flat)
![Scikit--learn](https://img.shields.io/badge/-Scikit--learn-F7931E?style=flat&logo=scikit-learn)

---

## 🎬 Project 2: Netflix-Style Movie Recommendation Engine

**Status: ✅ Complete | 🌐 [Live Demo](https://madhu-movie-recommender.streamlit.app/)**

> A recommendation engine using three algorithms — Collaborative Filtering, Content-Based Filtering, and a Hybrid Model — deployed as a live Streamlit web app.

### Dataset
| Property | Value |
|----------|-------|
| Source | GroupLens — MovieLens 100K |
| Ratings | 100,000 |
| Users | 943 |
| Movies | 1,682 |
| Rating Scale | 1 to 5 stars |
| Most Rated Movie | Star Wars (1977) — 583 ratings |

### Three Recommendation Algorithms Built

| Algorithm | How It Works | Key Concept |
|-----------|-------------|-------------|
| Collaborative Filtering | Finds users with similar taste | Cosine Similarity |
| Content-Based Filtering | Finds movies with similar genres | Genre Matrix |
| Hybrid Model | Combines both approaches | Best of both worlds |

### What I Built
| Step | Task | Tool |
|------|------|------|
| 1 | Loaded & explored 100K ratings | Pandas |
| 2 | Created visualizations — top movies, rating distribution | Matplotlib, Seaborn |
| 3 | Built User-Movie matrix (943×1682) | Pandas pivot_table |
| 4 | Calculated user similarity scores | Cosine Similarity |
| 5 | Built Collaborative Filtering function | Scikit-learn |
| 6 | Built Content-Based Filtering on genres | Scikit-learn |
| 7 | Combined both into Hybrid Model | Python |
| 8 | Deployed live web app | Streamlit Cloud |

### Live App Features
- 🎛️ Enter any User ID (1–943)
- 🎚️ Slider for number of recommendations (1–20)
- 🎬 Click button → get personalized movie recommendations instantly!
- 🌐 Accessible from anywhere in the world

### Technologies
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat&logo=pandas)
![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat&logo=numpy)
![Scikit--learn](https://img.shields.io/badge/-Scikit--learn-F7931E?style=flat&logo=scikit-learn)
![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat&logo=streamlit)

---

## 🛠️ Skills & Tools

| Category | Skills |
|----------|--------|
| **Languages** | Python 3.11 |
| **Data Analysis** | NumPy, Pandas |
| **Visualization** | Matplotlib, Seaborn |
| **Machine Learning** | Scikit-learn, Logistic Regression, Cosine Similarity |
| **Recommendation Systems** | Collaborative Filtering, Content-Based, Hybrid |
| **Web Apps** | Streamlit |
| **Version Control** | Git, GitHub (daily commits) |
| **Environment** | Anaconda, Jupyter Notebook, VS Code |

---

## 📈 Daily Progress

### Project 1 — Titanic Survival Prediction
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

### Project 2 — Movie Recommendation Engine
| Day | Topic | Status |
|-----|-------|--------|
| Day 1 | Loaded MovieLens 100K data, explored ratings & movies | ✅ |
| Day 2 | Data visualization — rating distribution, top movies | ✅ |
| Day 3 | Collaborative Filtering — user similarity matrix | ✅ |
| Day 4 | Content-Based Filtering — genre similarity | ✅ |
| Day 5 | Hybrid Model — combined both algorithms | ✅ |
| Day 6 | Streamlit web app — built interface | ✅ |
| Day 7 | Deployed to Streamlit Cloud — live app! | ✅ |

---

## 🎯 Goals

- [x] Complete Titanic ML Project
- [x] Build Movie Recommendation Engine with live deployment
- [ ] Build Customer Churn Predictor with Business Dashboard
- [ ] Learn SQL for data querying
- [ ] Secure a Data Science / ML Analyst role in the US
- [ ] Grow into an independent ML Engineer

---

## 📬 Contact

- **GitHub:** [github.com/Danammadhunika](https://github.com/Danammadhunika/ml-journey)
- **Email:** danammadhunika@gmail.com
- **Location:** Connecticut, USA

---

*Every commit in this repository represents a real learning session. Built from scratch — no shortcuts. 💪*