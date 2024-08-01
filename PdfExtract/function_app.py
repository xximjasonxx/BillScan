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

    values = req_body_json.get('values')
    if not values:
      return func.HttpResponse("Please provide values", status_code=400)
    
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv('STORAGE_ACCOUNT_CONNECTION_STRING'))
    records = []
    for record in values:
      record_id = record['recordId']
      congress_number = record['data']['congressNumber']
      bill_number = record['data']['billNumber']
    
      if not congress_number or not bill_number:
        return func.HttpResponse(f"Record: {record_id} does not contain either congress number or bill name", status_code=400)
      
      blob_client = blob_service_client.get_blob_client(container='bills-pdf', blob=f'{congress_number}hr{bill_number}.pdf')
      pdf_data = blob_client.download_blob().readall()
      pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))

      text = ""
      for page in pdf_reader.pages:
        text += page.extract_text()

      records.append(
        {
          "recordId": record_id,
          "data": {
            "text_contents": text
          }
        }
      )
    
    response_json = json.dumps({ "values": records })
    print(response_json)
    return func.HttpResponse(body=response_json, mimetype="application/json")