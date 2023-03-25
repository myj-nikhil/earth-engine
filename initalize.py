import ee 

def initialise():
    #Add the service account mail ID from Google Cloud
    service_account = 'greenhands-earthengine@greenhands-earthengine.iam.gserviceaccount.com' 
    #Give the location of the privatekey file of the service account
    credentials = ee.ServiceAccountCredentials(service_account, 'greenhands-earthengine.json')
    ee.Initialize(credentials)