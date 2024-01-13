import streamlit as st
import pickle
import re
import nltk
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import base64
import pdfplumber
import os,tempfile


nltk.download('punkt')
nltk.download('stopwords')

# Loading models
clf = pickle.load(open(r'./clf.pkl', 'rb'))
tfidfd = pickle.load(open(r'./tfidf.pkl', 'rb'))

# YouTube API key (replace 'YOUR_API_KEY' with your actual API key)
API_KEY = 'AIzaSyAR8Gp1ambP-AfOGu8rR8RbP7-62T-MbaA'
youtube = build('youtube', 'v3', developerKey=API_KEY)


def clean_resume(resume_text):
    clean_text = re.sub('http\S+\s*', ' ', resume_text)
    clean_text = re.sub('RT|cc', ' ', clean_text)
    clean_text = re.sub('#\S+', '', clean_text)
    clean_text = re.sub('@\S+', '  ', clean_text)
    clean_text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', clean_text)
    clean_text = re.sub(r'[^\x00-\x7f]', r' ', clean_text)
    clean_text = re.sub('\s+', ' ', clean_text)
    return clean_text


# Function to extract video ID from YouTube video link
def extract_video_id(youtube_link):
    query = urlparse(youtube_link)
    if query.hostname == 'www.youtube.com':
        if 'v' in query.query:
            return parse_qs(query.query)['v'][0]
    elif query.hostname == 'youtu.be':
        return query.path[1:]
    return None


# Function to search for YouTube videos based on the predicted category
def search_youtube_videos(query, max_results=1):
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=2
    )
    response = request.execute()
    videos = response.get('items', [])
    if videos:
        video_id1 = videos[0]['id']['videoId']
        video_title1 = videos[0]['snippet']['title']
        video_id2 = videos[1]['id']['videoId']
        video_title2 = videos[1]['snippet']['title']
        return video_id1, video_title1,video_id2, video_title2
    return None, None

#  background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
def sidebar_bg():


   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
        background-color: #1f1652;
        
      }}
      </style>
      """,
      unsafe_allow_html=True,
      )

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True) 

def topbar(topbar):

   img_ext = 'png'
   bin_str = get_base64(topbar)
   st.markdown(
      f"""
      <style>
      header.css-k0sv6k.e8zbici2 {{
          background: url(data:image/{img_ext};base64,{bin_str});
      }}
      </style>
        """,
      unsafe_allow_html=True,
      )  
   

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            try:
                text += page.extract_text()
            except TypeError:
                # Handle cases where the page extraction fails
                pass
    return text      


# Web app
def main():

    st.set_page_config(page_title="screener", page_icon="📈")

    st.title("Resume Screener")
    line_html = '''
    <hr style="
        border: none;
        height: 2px;
        background-color:  #E5CCFF;
        ">
    '''


    # Display the colored line using st.markdown
    st.markdown(line_html, unsafe_allow_html=True)
    sidebar_bg()
    set_background(r"pages/3.gif")
    topbar(r"pages/Home.png")

    st.markdown('<style>' +\
            'div.stMarkdown div.css-5rimss { color: #E5CCFF; }' +\
            'div.css-zt5igj {font-size:50}'+\
            'div.stMarkdown span.css-10trblm {  color: #E5CCFF; }' +\
            'div.css-8u98yl section.css-vjj2ce { background-color: #E5CCFF;  color: black}' +\
            'span.css-pkbazv { color: #E5CCFF;}'+\
            'span.css-17lntkn { color:#E5CCFF;}'+\
            '</style>', unsafe_allow_html=True)

    

    # Create a sidebar for upload
    st.header("Upload Resume")
    uploaded_file = st.file_uploader('', type=['txt', 'pdf'])
    

    if uploaded_file is not None:
        # Use tempfile to store the PDF temporarily
        temp_pdf = tempfile.NamedTemporaryFile(delete=False)
        temp_pdf.write(uploaded_file.read())

        # Pass the temporary PDF file to extract_text_from_pdf
        resume_text = extract_text_from_pdf(temp_pdf.name)
        temp_pdf.close()
        cleaned_resume = clean_resume(resume_text)
        print("cleaned text =====>",cleaned_resume)
        input_features = tfidfd.transform([cleaned_resume])
        prediction_id = clf.predict(input_features)[0]

        # Map category ID to category name
        category_mapping = {
            15: "Java Developer",
            23: "Testing",
            8: "DevOps Engineer",
            20: "Python Developer",
            24: "Web Designing",
            12: "HR",
            13: "Hadoop",
            3: "Blockchain",
            10: "ETL Developer",
            18: "Operations Manager",
            6: "Data Science",
            22: "Sales",
            16: "Mechanical Engineer",
            1: "Arts",
            7: "Database",
            11: "Electrical Engineering",
            14: "Health and fitness",
            19: "PMO",
            4: "Business Analyst",
            9: "DotNet Developer",
            2: "Automation Testing",
            17: "Network Security Engineer",
            21: "SAP Developer",
            5: "Civil Engineer",
            0: "Advocate",
        }

        category_name = category_mapping.get(prediction_id, "Unknown")

        # Highlight the predicted category label
        highlighted_category = f'<span style="font-size: 40px; color: #FF5733;">{category_name}</span>'
        st.markdown(f"Predicted Category:     {  highlighted_category}", unsafe_allow_html=True)


        prediction_probabilities = clf.predict_proba(input_features)[0]

        st.header("Prediction Percentages Bar Chart")

        # Prepare data for the bar chart
        categories = [category_mapping.get(category_id, "Unknown") for category_id in clf.classes_]
        percentages = [percentage * 100 for percentage in prediction_probabilities]

        # Create a bar chart
        st.bar_chart({f"{category} ": percentage for category, percentage in zip(categories, percentages)})

        # Search for YouTube videos based on the predicted category
        youtube_query = f"how to write a {category_name} resume "

        # Display two YouTube video links side by side
        st.header("Here are a few YouTube links to enhance your resume building skills.")
        col1, col2 = st.columns(2)

        for i in range(1):
            predicted_video_id1, video_title1,predicted_video_id2, video_title2 = search_youtube_videos(youtube_query)
            if predicted_video_id1 is not None:
                # Display YouTube video title
                col1.header(f"Video Title:\n {video_title1}")

                # Display YouTube video thumbnail for predicted category with clickable link
                youtube_thumbnail_url = f"https://img.youtube.com/vi/{predicted_video_id1}/hqdefault.jpg"
                youtube_thumbnail_html = f'<a href="https://www.youtube.com/watch?v={predicted_video_id1}" target="_blank"><img src="{youtube_thumbnail_url}" alt="YouTube Thumbnail" width="350" height="225"></a>'
                col1.markdown(youtube_thumbnail_html, unsafe_allow_html=True)
            else:
                col1.warning("No relevant YouTube video found for the predicted category.")
            
            
            if predicted_video_id2 is not None:
                # Display YouTube video title in col2
                col2.header(f"Video Title:\n {video_title2}")

                # Display YouTube video thumbnail for predicted category with clickable link in col2
                youtube_thumbnail_url = f"https://img.youtube.com/vi/{predicted_video_id2}/hqdefault.jpg"
                youtube_thumbnail_html = f'<a href="https://www.youtube.com/watch?v={predicted_video_id2}" target="_blank"><img src="{youtube_thumbnail_url}" alt="YouTube Thumbnail" width="350" height="225"></a>'
                col2.markdown(youtube_thumbnail_html, unsafe_allow_html=True)
            else:
                col2.warning("No relevant YouTube video found for the predicted category.")    

    # Repeat the process for the second column (col2) if needed

# Python main
if __name__ == "__main__":
    main()
