import ee


def initialise():
    # Add the service account mail ID from Google Cloud
    service_account = 'earthengine-v2@earthengine-v2.iam.gserviceaccount.com'
    # Give the location of the privatekey file of the service account
    credentials = ee.ServiceAccountCredentials(
        service_account, 'earthengine-v2.json')
    ee.Initialize(credentials)
