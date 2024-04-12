# import packages
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import pandas as pd
import cv2
import easyocr
import re
import os
import matplotlib.pyplot as plt

# easyocr for language english
reader = easyocr.Reader(['en'])

#sqlite3 connection
mydb=sqlite3.connect('/content/bizcard.db')
cursor=mydb.cursor()

#streamlit background color
page_bg_color='''
<style>
[data-testid="stAppViewContainer"]{
        background-color:#FFDAB9;
}
</style>'''
#streamlit button color
button_style = """
    <style>
        .stButton>button {
            background-color: #ffa089 ; 
            color: black; 
        }
        .stButton>button:hover {
            background-color: #ffddca; 
        }
    </style>    
"""
#streamlit page
st.set_page_config(
    page_title="BizCardX",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="auto")

st.markdown(page_bg_color,unsafe_allow_html=True)  #calling background color
st.markdown(button_style, unsafe_allow_html=True)  #calling button color

st.title("BizCardX: Extracting Business Card Data")

selected = option_menu(menu_title=None,options= ["Home", 'Upload & Extract','Modify','Delete'],icons=["house", "cloud-upload","pencil", "trash"],
          default_index=0,orientation='horizontal',
          styles={"container": { "background-color": "white", "size": "cover", "width": "100"},
            "icon": {"color": "brown", "font-size": "20px"},

            "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#ffe5b4"},
            "nav-link-selected": {"background-color": "#E2838A"}})

#function to  save image
def save_bizcard(image_files):
        uploaded_cards_dir = os.path.join(os.getcwd(),"Images_bizcard")
        os.makedirs(uploaded_cards_dir, exist_ok=True)
        with open(os.path.join(uploaded_cards_dir, image_files.name), "wb") as f:
            f.write(image_files.getbuffer())

#function to view image as a extracted information in bounding box
def image_box_preview(image, res):
    for (bbox, text, prob) in res:
        (tl, tr, br, bl) = bbox
        tl = (int(tl[0]), int(tl[1]))
        tr = (int(tr[0]), int(tr[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        cv2.rectangle(image, tl, br, (0, 255, 0), 2)
        cv2.putText(image, text, (tl[0], tl[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    fig, ax = plt.subplots(figsize=(15, 15))
    ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax.axis('off')
    st.pyplot(fig)

#function converting image to binary format
def image_to_binary(file):
    with open(file, 'rb') as file:
        binaryData = file.read()
    return binaryData

#function extract information(collect data)
def collect_data(result,saved_image):
    data = {"Card_Holder":[],
        "Designation":[],
        "Company_Name":[],
        "Phone_Number":[],
        "Email":[],
        "Website":[],
        "Area":[],
        "City":[],
        "State":[],
        "Pincode":[],
        "Image": image_to_binary(saved_image)
        }
    for index, i in enumerate(result):

        # To get WEBSITE_URL
        if "www " in i.lower() or "www." in i.lower():
            data["Website"].append(i)
        elif "WWW" in i:
            data["Website"] = result[4] + "." + result[5]

        # To get EMAIL ID
        elif "@" in i:
            data["Email"].append(i)

        # To get MOBILE NUMBER
        elif "-" in i:
            data["Phone_Number"].append(i)
            if len(data["Phone_Number"]) == 2:
                data["Phone_Number"] = " & ".join(data["Phone_Number"])
        # To get COMPANY NAME
        elif index == len(res) - 1:
            data["Company_Name"].append(i)

        # To get CARD HOLDER NAME
        elif index == 0:
            data["Card_Holder"].append(i)

        # To get DESIGNATION
        elif index == 1:
            data["Designation"].append(i)

        # To get AREA
        if re.findall('^[0-9].+, [a-zA-Z]+', i):
            data["Area"].append(i.split(',')[0])
        elif re.findall('[0-9] [a-zA-Z]+', i):
            data["Area"].append(i)

        # To get CITY NAME
        match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
        match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
        match3 = re.findall('^[E].*', i)
        if match1:
            data["City"].append(match1[0])
        elif match2:
            data["City"].append(match2[0])
        elif match3:
            data["City"].append(match3[0])

        # To get STATE
        state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
        if state_match:
            data["State"].append(i[:9])
        elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
            data["State"].append(i.split()[-1])
        if len(data["State"]) == 2:
            data["State"].pop(0)

        # To get PINCODE
        if len(i) >= 6 and i.isdigit():
            data["Pincode"].append(i)
        elif re.findall('[a-zA-Z]{9} +[0-9]', i):
            data["Pincode"].append(i[10:])
    return data

#function sqlite3 table creation and insertion
def table(df):
  cursor.execute('''CREATE TABLE IF NOT EXISTS card(Card_Holder Varchar(255),Designation Varchar(255),
                    Company_Name Varchar(255),Phone_Number Varchar(255),Email Varchar(255),Website Varchar(255),Area Varchar(255),
                    City Varchar(255),State Varchar(255),Pincode Varchar(255),Image LONGBLOB,PRIMARY KEY(Card_Holder))''')
  for index,row in df.iterrows():
    cursor.execute('''INSERT INTO card(Card_Holder,Designation,Company_Name,Phone_Number,Email,Website,Area,
                                  City,State,Pincode,Image) values(?,?,?,?,?,?,?,?,?,?,?)''',
                    (row['Card_Holder'],row['Designation'],row['Company_Name'],row['Phone_Number'],row['Email'],
                    row['Website'],row['Area'],row['City'],row['State'],row['Pincode'],row['Image']))
  mydb.commit()

#function preview the database
def preview():
    cursor.execute("select * from card")
    column_names = [description[0] for description in cursor.description]
    dd=pd.DataFrame(cursor.fetchall(),columns=column_names)
    st.write(dd)

#function modify table
def modify():
  cursor.execute("select distinct(Card_Holder) from card")
  column_names = [description[0] for description in cursor.description]
  dis=pd.DataFrame(cursor.fetchall(),columns=column_names)
  name=st.selectbox("Select card holder name",dis)
  st.write(f"### You have selected :red[**{name}'s**] card to modify")


  cursor.execute("select * from card where Card_Holder=?",(name,))
  change=cursor.fetchone()

  col1,col2=st.columns(2)
  with col1:
    card_holder = st.text_input("Card_Holder", change[0])
    designation = st.text_input("Designation", change[1])
    company_name = st.text_input("Company_Name", change[2])
    mobile_number = st.text_input("Mobile_Number", change[3])
    email = st.text_input("Email", change[4])
  with col2:
    website = st.text_input("Website", change[5])
    area = st.text_input("Area", change[6])
    city = st.text_input("City", change[7])
    state = st.text_input("State", change[8])
    pin_code = st.text_input("Pin_Code", change[9])

  #button
  if st.button("Modify Table"):
     cursor.execute("""UPDATE card SET Card_Holder=?,Designation=?,Company_Name=?,Phone_Number=?,Email=?,Website=?,
                                    Area=?,City=?,State=?,Pincode=? where Card_Holder=?""",
                                    (card_holder,designation,company_name, mobile_number, email, website, area, city, state,
                                    pin_code,name))

     mydb.commit()
     st.success("Information updated in database successfully.")

#function delete
def delete():
  cursor.execute("select distinct(Card_Holder) from card")
  column_names = [description[0] for description in cursor.description]
  dis=pd.DataFrame(cursor.fetchall(),columns=column_names)
  name=st.selectbox("Select card holder name",dis,key='delete')
  st.write(f"### You have selected :red[**{name}'s**] card to delete")

  #button
  if st.button("Delete"):

    cursor.execute("delete from card where Card_Holder=?",(name,))
    mydb.commit()
    st.success("Business card information has been deleted from database!!!")

#streamlit menu
#home page
if selected=="Home":
    col1,col2=st.columns(2)
    with col1:
        st.image('/content/business-card.jpg')
    with col2:
        st.write("### Business cards are cards bearing business information about a company or individual.They are shared during formal introductions as a convenience and a memory aid. A business card typically includes the giver's name, company or business affiliation (usually with a logo) and contact information such as street addresses, telephone number(s), fax number, e-mail addresses and website.")
    col3,col4=st.columns(2)
    with col3:
        st.write("### BizCardX is a Stream lit web application designed to effortlessly extract data from business cards using Optical Character Recognition (OCR) technology. With BizCardX, users can easily upload images of business cards, and the application leverages the powerful easyOCR library to extract pertinent information from the cards."
        " The extracted data is then presented in a user-friendly format and can be stored in a SQL database for future reference and management.")
    with col4:
        st.image('/content/extract.png')

#upload & extract page
if selected=="Upload & Extract":
    image_files = st.file_uploader("## Upload the Business Card below:", type=["png","jpg","jpeg"])

    if image_files != None:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            img = image_files.read()
            st.markdown("### Business Card has been uploaded")
            st.image(img)
            save_bizcard(image_files)

        with col2:
            with st.spinner("Please wait processing image..."):
              st.markdown("### Data extracted from image")
              saved_image = os.getcwd() + "/" + "Images_bizcard" + "/" + image_files.name
              image = cv2.imread(saved_image)
              res = reader.readtext(saved_image)
              image_box_preview(image, res)
        st.success("Data has been extracted from image successfully!!! ")

        saved_image = os.getcwd() + "/" + "Images_bizcard" + "/" + image_files.name
        result = reader.readtext(saved_image, detail=0, paragraph=False)
        extract=collect_data(result,saved_image)
        df=pd.DataFrame(extract)

    if st.button("DataFrame"):
      st.write(df)

    if st.button("SQL"):
      try:
        table(df)
        st.success("Datas pushed to SQL successfully!!!")
      except:
        st.error("Details already stored!!!")

    if st.button("Preview"):
      try:
        preview()
      except:
        st.error("Table is empty")

#modify page
if selected=='Modify':
     try:
        modify()
     except:
        st.error("Table is empty")
     
#delete page     
if selected=='Delete':
  try:
    delete()
  except:
        st.error("Table is empty")


