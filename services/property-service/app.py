from fastapi import FastAPI, Request, Response
from xml.sax.saxutils import escape

app = FastAPI(title="Property Service (Simulated SOAP)")

MOCK_DB = {
    "CIT-1001": {
        "ownerName": "Rajesh Kumar",
        "propertyId": "PROP-BLR-8832",
        "propertyAddress": "123 MG Road, Bangalore",
        "propertyType": "Commercial"
    },
    "CIT-1002": {
        "ownerName": "Priya Sharma",
        "propertyId": "PROP-CCU-9921",
        "propertyAddress": "456 Park Street, Kolkata",
        "propertyType": "Residential"
    }
}

@app.get("/health")
def health():
    return {"status": "ok", "service": "property-soap"}

@app.post("/soap/property")
async def get_property_soap(request: Request):
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Very naive XML extraction for simulation purposes
    citizen_id = None
    if "<citizenId>" in body_str:
        citizen_id = body_str.split("<citizenId>")[1].split("</citizenId>")[0]
        
    if not citizen_id or citizen_id not in MOCK_DB:
        # Return SOAP fault
        fault = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
          <soap:Body>
            <soap:Fault>
              <faultcode>soap:Client</faultcode>
              <faultstring>Citizen ID not found or missing</faultstring>
            </soap:Fault>
          </soap:Body>
        </soap:Envelope>"""
        return Response(content=fault, media_type="text/xml", status_code=500)
        
    data = MOCK_DB[citizen_id]
    
    response_xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <GetPropertyDetailsResponse>
          <ownerName>{escape(data["ownerName"])}</ownerName>
          <propertyId>{escape(data["propertyId"])}</propertyId>
          <propertyAddress>{escape(data["propertyAddress"])}</propertyAddress>
          <propertyType>{escape(data["propertyType"])}</propertyType>
        </GetPropertyDetailsResponse>
      </soap:Body>
    </soap:Envelope>"""
    
    return Response(content=response_xml, media_type="text/xml")
