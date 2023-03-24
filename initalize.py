import ee 

def initialise():
    service_account = 'dulcet-order-380816@appspot.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, 'dulcet-order-380816-c70b6f72a2bc.json')
    ee.Initialize(credentials)