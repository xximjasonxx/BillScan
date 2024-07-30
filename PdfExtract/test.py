import PyPDF2
import base64

with open('118hr1.pdf', 'rb') as file:
  pdf_reader = PyPDF2.PdfReader(file)
  num_pages = len(pdf_reader.pages)

  text = ""
  for page in pdf_reader.pages:
    text += page.extract_text()

encoded_contents = base64.b64encode(text.encode('utf-8'))
print(encoded_contents)