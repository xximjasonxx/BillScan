import io
import os
import json
import azure.functions as func
import PyPDF2

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()
app = func.FunctionApp()

@app.route(route="download/pdf", auth_level=func.AuthLevel.FUNCTION)
def download_pdf(req: func.HttpRequest) -> func.HttpResponse:
    req_body_json = req.get_json()
    print(req_body_json)

    congress_number = req_body_json['values'][0]['data']['congressNumber']
    bill_number = req_body_json['values'][0]['data']['billNumber']

    if not congress_number or not bill_number:
      return func.HttpResponse("Please provide congress number and bill name", status_code=400)

    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION_STRING'))
    blob_client = blob_service_client.get_blob_client(container='bills-pdf', blob=f'{congress_number}hr{bill_number}.pdf')
    pdf_data = blob_client.download_blob().readall()

    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
    text = ""
    for page in pdf_reader.pages:
      text += page.extract_text()

    response = {
      "values": [
        {
          "recordId": req_body_json['values'][0]['recordId'],
          "data": {
            "text_contents": text
          }
        }
      ]
    }
    
    return func.HttpResponse(body=json.dumps(response), mimetype="application/json")