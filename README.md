
Demo video: https://www.linkedin.com/posts/rajarajeswari-s-49671428b_hello-everyone-my-new-project-activity-7184590631166500864-jdLi?utm_source=share&utm_medium=member_desktop

Problem Statement:
You have been tasked with developing a Streamlit application that allows users to upload an image of a business card and extract relevant information from it using easyOCR. The extracted information should include the company name, card holder name, designation, mobile number, email address, website URL, area, city, state,and pin code. The extracted information should then be displayed in the application's graphical user interface (GUI).

In addition, the application should allow users to save the extracted information into a database along with the uploaded business card image. The database should be able to store multiple entries, each with its own business card image and extracted information.

To achieve this, you will need to use Python, Streamlit, easyOCR, and a database management system like SQLite or MySQL. The application should have a simple and intuitive user interface that guides users through the process of uploading the business card image and extracting its information. The extracted information should be displayed in a clean and organized manner, and users should be able to easily add it to the database with the click of a button. And Allow the user to Read the data, Update the data and Allow the user to delete the data through the streamlit UI.

To run this project open colab,
 1.Install the packages from requirements.txt .
 
 2.Connection string for sqlite3 .
 
 3.set of buisness card images https://drive.google.com/drive/folders/1FhLOdeeQ4Bfz48JAfHrU_VXvNTRgajhp
 
 4.upload card.py , business-card.jpg and extract.png in runtime.
 
 5.  !wget -q -O - ipv4.icanhazip.com  give this command in a cell and run which will provide an ip address that will be a password for tunnel.
    
 6.  ! streamlit run card.py & npx localtunnel --port 8501  give this command in another cell and run click 'your url is:' ,this will open a page and give the tunnel password click submit, streamlit page will be opened.

Data Extraction:

Utilizing the easyOCR library, the application extracts key details including company name, cardholder name, designation, mobile number, email address, website URL, area, city, state, and pin code which will display in bounding box and convert to a dataframe.

Database Integration:

Users can save the extracted information into a database along with the uploaded business card image. The database, powered by SQLite, is designed to store multiple entries, each associated with its respective business card image(binary format) and extracted information.

Note: Use primary key to avoid duplication.

CRUD Operations:

The application supports essential CRUD (Create, Read, Update, Delete) operations. Users can easily add, view, update, and delete entries through the Streamlit UI.
