**RIGHT NOW USES**


**For FAST API-Uvicorn Activation**
cd C:\\Users\\danam\\OneDrive\\Desktop\\ML\_journey\\project\_04\_ai\_resume\_analyzer\\backend

..\\venv\\Scripts\\Activate.ps1

uvicorn main:app --reload



**For Run Streamlit**
cd C:\\Users\\danam\\OneDrive\\Desktop\\ML\_journey\\project\_04\_ai\_resume\_analyzer\\frontend

..\\venv\\Scripts\\Activate.ps1

streamlit run app.py





**PYTHON VS CODE SHORTCUTS**

Muilt-Cursor       = Alt + Click anywhere

Comment the line   = Ctrl + /

Thick black block  = Inster key

Coming to next line = Shift + Enter



**IN JUPYTER NOTEBOOK FROM TERMINAL**

cd C:\\Users\\danam\\OneDrive\\Desktop\\ML\_journey

jupyter notebook



**UPDATE README FROM TERMINAL**

cd C:\\Users\\danam\\OneDrive\\Desktop\\ML\_journey

git add .

git commit -m "Day XX: topic description here"

git push



**PYTHON TELLS US WHAT IS IN THAT FOLDER**

import os

path = r'C:\\Users\\danam\\OneDrive\\Desktop\\~~ML\_journey\\project\_03\_ecommerce\_sql\\datasets'~~

print("Folder exists?", os.path.exists(path))

print("\\nFiles inside:")

print(os.listdir(path))



orders table — 8 columns:

InvoiceNo, StockCode, Description, Quantity,

InvoiceDate, UnitPrice, CustomerID, Country

country\_info table — 3 columns:

Country, Region, Currency

