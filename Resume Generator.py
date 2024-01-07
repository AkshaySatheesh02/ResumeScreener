import streamlit as st
from reportlab.pdfgen import canvas
import base64
import os
from io import BytesIO
from PIL import Image,ImageDraw
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def make_round_image(image):
    # Create a circular mask
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, image.size[0], image.size[1]), fill=255)

    # Apply the circular mask to the image
    rounded_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
    rounded_image.paste(image, mask=mask)

    return rounded_image

def read_pdf_file(file):
    # Read the PDF file as bytes
    with open(file, 'rb') as file:
        pdf_bytes = file.read()
    # Base64 encode the PDF content
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

    # Create a data URI for the PDF content
    pdf_data_uri = f'data:application/pdf;base64,{pdf_base64}'

    return pdf_data_uri


def main():
    st.set_page_config(
        page_title="Enter your Resume details",
        page_icon="📝",
    )

    st.title("Resume Generator")

    name = st.text_input("Name:")
    contact_info = st.text_area("Contact Information:")
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])
    description = st.text_area("Brief Summary:")
    educational_details = st.text_area("Educational Details:")
    work_experience = st.text_area("Work Experience:")
    project_details = st.text_area("Project Details:")
    skills = st.text_area("Skills:")

    data = {
        "name": name,
        "contact_info": contact_info,
        "description": description,
        "educational_details": educational_details,
        "work_experience": work_experience,
        "project_details": project_details,
        "skills": skills,
    }
    st.subheader("Input Data:")

    # Create and download the PDF
    if st.button("Generate PDF"):
        if uploaded_image is not None:
            image_bytes = uploaded_image.read()
            pdf_filename = create_pdf(data, image_bytes)
            st.success("PDF generated successfully!")
        else:
            st.warning("Please upload an image before generating the PDF.")

        st.markdown(f'<iframe src="{read_pdf_file(pdf_filename)}" width="100%" height="700px"></iframe>',
                    unsafe_allow_html=True)




def create_pdf(data, image):
    pdf_filename = "./Resumes/resume.pdf"

    # Create PDF document
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    sections = [
    ("Contact Information", "contact_info"),
    ("Brief Summary", "description"),
    ("Educational Details", "educational_details"),
    ("Work Experience", "work_experience"),
    ("Project Details", "project_details"),
    ("Skills", "skills"),
]


    # Font styles
    c.setFont("Times-Roman", 12)

    # Name and Image
    c.setFont("Times-Bold", 45)

    # Calculate available width for the name
    available_width_name = 400 - 100  # Adjusted for the left margin
    wrapped_name = ""

    # Break the name into segments that fit within the available width
    for word in data['name'].split():
        if c.stringWidth(wrapped_name + word, "Times-Bold", 45) <= available_width_name:
            wrapped_name += word + " "
        else:
            c.drawString(100, 720, wrapped_name.strip())
            c.translate(0, -44)  # Adjusted Y-coordinate for the wrapped name
            wrapped_name = word + " "

    if wrapped_name:
        c.drawString(100, 720, wrapped_name.strip())
        c.translate(0, 0)  # Adjusted Y-coordinate for the wrapped name

    if image is not None:
        image = Image.open(BytesIO(image))
        image_width, image_height = image.size
        c.drawInlineImage(image, 400, 710, width=100, height=100)

    c.setFont("Times-Roman", 12)

    # Spacer between name and other sections
    c.translate(0, 0)

    # Loop through sections and draw them
    y_coordinate = 650  # Initial Y-coordinate for the first section
    for title, key in sections:
        # Section Title
        c.setFont("Times-Bold", 16)
        c.drawString(100, y_coordinate, f"{title}")
        c.line(100, y_coordinate - 10, 500, y_coordinate - 10)  # Adjusted Y-coordinate for reduced space
        c.setFont("Times-Roman", 12)

        # Text Content
        text_lines = data[key].split('\n')
        for line in text_lines:
            if y_coordinate < 50:
                c.showPage()  # New page
                y_coordinate = 750  # Reset Y-coordinate for the new page

            # Calculate available width for each line
            available_width = 500 - 100  # Adjusted for the left margin
            wrapped_text = ""

            # Break the line into segments that fit within the available width
            for word in line.split():
                if c.stringWidth(wrapped_text + word, "Times-Roman", 12) <= available_width:
                    wrapped_text += word + " "
                else:
                    c.drawString(100, y_coordinate - 25, wrapped_text.strip())
                    y_coordinate -= 15  # Adjust the Y-coordinate for the next line
                    wrapped_text = word + " "

            if wrapped_text:
                c.drawString(100, y_coordinate - 25, wrapped_text.strip())
                y_coordinate -= 15  # Adjust the Y-coordinate for the next line

        y_coordinate -= 55  # Adjust the Y-coordinate for the next section

    # Save the PDF
    c.save()

    # Return the generated PDF filename
    return pdf_filename



if __name__ == "__main__":
    main()
