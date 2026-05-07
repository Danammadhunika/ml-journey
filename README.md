# Titanic Survival Prediction Project 🚢

## What is this project?
A machine learning project to predict 
which passengers survived the Titanic disaster.

## Technologies Used
- Python
- NumPy
- Pandas
- Jupyter Notebook

## Project Structure
ml_journey/
├── datasets/          → CSV data files
├── notebooks/         → Jupyter notebooks
└── projects/          → Python files

## Daily Progress
- Day 1: Learned NumPy arrays, applied to Titanic age data
- Day 2: (update every day!)

## What I Learned
Day 1: Learned NumPy arrays, indexing 
and basic operations. Applied to real 
Titanic passenger age data.

"I started with a small sample of 
10 passengers to understand NumPy 
operations before applying them 
to the full 891 passenger dataset"

Day 2: Learned NumPy 2D arrays, 
statistical operations (mean, max, min).
Applied to real Titanic passenger data.

Day 3: Loaded Titanic dataset using Pandas.
Explored data using head(), shape(), info(), 
describe(). Cleaned missing values — filled 
Age with mean, Embarked with mode, 
dropped Cabin column. All columns now 
have 0 missing values!

Day 4: Data Analysis complete!
- Found overall survival rate = 38%
- Women survived more than men (74% vs 19%)
- 1st class survived more than 3rd (63% vs 24%)
- Children had highest survival rate (58%)

Day 5: Data Visualization complete!
- Bar chart: Survived vs Died
- Pie chart: Survival percentage
- Bar chart: Survival rate by gender
- Bar chart: Survival rate by class
- Histogram: Age distribution
- Bar chart: Survival rate by age group
- Bar chart: Survival by gender and class
Key finding: Female 1st class had 97% 
survival rate vs Male 3rd class 14%!

Day 6: Feature Engineering complete!
- Converted Sex column: male=0, female=1
- Converted Embarked column: C=0, Q=1, S=2
- Dropped useless columns: Name, Ticket, AgeGroup
- Dataset now has 9 numeric columns
- Data is ready for ML model!

Day 7: Machine Learning Model complete!
- Created X (features) and y (target)
- Split data: 80% train, 20% test
- Built Logistic Regression model
- Trained model on 712 passengers
- Predicted survival on 179 passengers
- Achieved 81% accuracy!

Day 8: Model Evaluation complete!
- Accuracy Score: 81%
- Confusion Matrix: 145/179 correct
- Classification Report: complete analysis
- Model better at predicting deaths (83%)
  than survivors (79%)

Added: Complete ML Notes PDF and 
Titanic Project Presentation PPT