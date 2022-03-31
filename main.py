import os
from dotenv import load_dotenv
import requests
import json
import time
from utils import *

# load dotenv vars located in .env file
load_dotenv()

'''
    Survey's common name
'''
common_names = {
    "deployments": "Camara Trampa y Grabadoras v 1.1 cumulo",
    "individuals": "Pequeños Mamíferos v 1.1",
    "erie": "ERIE - Evaluacion Ecosistemica"
}


# Auth credentials
auth = (os.getenv('KOBO_USER'), os.getenv('KOBO_PASSWORD'))

# login request
login = requests.get(
    os.getenv('KOBO_URL') + "token/?format=json", auth=auth)

if login.status_code == 200: # if login was succesful proceed

    # retreive token from response
    token = json.loads(login.text)['token']

    # set headers for the following requests
    headers = {
        "Authorization": "Token " + token,
        "Accept": "application/json"
    }

    for survey_type,common_name in common_names.items():

        print("Filtering %s reports" % survey_type)
        # get the surveys with a common name
        filtered = get_surveys(common_name,headers)


        # before making another request 
        # wait 2 second to not overload the server
        time.sleep(2)

        reports = get_data(filtered,headers)

        # get a session object with zendro credentials
        session = login_to_zendro()

        print("Deploying %s reports" % survey_type)
        # build deployments query and post to zendro
        if survey_type == "deployments":
           build_n_post_deployment_query(session,reports,common_name,survey_type)

        # build individuals and erie query and post to zendro
        if survey_type == "individuals" or survey_type == "erie":
            build_n_post_individuals_n_erie_query(session,reports,survey_type)
        

else:
    print("Bad Credentials!")