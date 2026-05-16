**PYTHON VS CODE SHORTCUTS**

Muilt-Cursor       = Alt + Click anywhere

Comment the line   = Ctrl + /

Thick black block  = Inster key

Coming to next line = Shift + Enter



**IN JUPYTER NOTEBOOK FROM TERMINAL**

cd C:\\Users\\danam\\OneDrive\\Desktop

cd ML\_journey\\project\_02\_movie\_recommender

jupyter notebook



**UPDATE README FROM TERMINAL**

cd C:\\Users\\danam\\OneDrive\\Desktop

cd ML\_journey

git add .

git commit -m "Updated README with live demo links"

git push



**PYTHON TELLS US WHAT IS IN THAT FOLDER**

import os

path = r'C:\\Users\\danam\\OneDrive\\Desktop\\~~ML\_journey\\project\_03\_ecommerce\_sql\\datasets'~~

print("Folder exists?", os.path.exists(path))

print("\\nFiles inside:")

print(os.listdir(path))

