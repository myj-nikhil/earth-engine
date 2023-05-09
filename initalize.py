import ee
from timeit import default_timer as timer
import logging

app_logger = logging.getLogger('initialise.py')
app_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log', mode='a')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

app_logger.addHandler(file_handler)



# This function authenticates and initialises the google earth engine.
## Warning : ** Please keep the privatekey file safe and make sure you do not upload 
# #your private key to the any cloud repository to avoid misuse of google cloud resources. **

def initialise():
    start = timer()
    # Add the service account mail ID from Google Cloud
    service_account = 'project-xyz@project-xyz-383203.iam.gserviceaccount.com'
    # Give the location of the privatekey file of the service account
    credentials = ee.ServiceAccountCredentials(
        service_account, 'project-xyz-383203.json')
    ee.Initialize(credentials)
    end = timer()
    app_logger.info("Time for initialisation : %s", end-start)
