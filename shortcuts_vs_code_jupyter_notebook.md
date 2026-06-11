**PYTHON VS CODE SHORTCUTS**

Muilt-Cursor       = Alt + Click anywhere

Comment the line   = Ctrl + /

Thick black block  = Inster key

Coming to next line = Shift + Enter



**EVERYDAY TO CLAUDE AI**

OK today is date is ??? ??? 2026, lets start day ???

1\. Updated README and push for Day ???

2\. Applied for ??? jobs today

3\. Opened Jupyter Notebook

4\. Ran all the cells


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

