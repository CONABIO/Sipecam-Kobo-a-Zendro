import os
import json
import time
from .match_deployment_to_node import match_deployment_to_node
from .clean_kobo_reports import *
from .parse_to_graphql_query import parse_to_graphql_query
from .get_cumulus_data import get_cumulus_nodes
from .sort_data_by_cumulus import sort_data_by_cumulus

def build_n_post_deployment_query(session,reports,common_name,survey_type):
    """
     Build the query to post to zendro from the data
     extracted for device deployments from kobo.

     Params:
        session (object):       Session object with auth credential
                                of zendro.
        reports (list):         A list containing the data of the 
                                reports.
        common_name (string):   A string containing the name of the
                                surveys.
        survey_type (string):   A string that indicates the type of
                                the surveys.

     Returns:
        (void) 
     """

    deployments = []
    for r in reports:
        """
            Match reports with its node id, cumulus id and
            device id to build a deployment dict so the script
            can make a post to zendro to create the deployment.
          """
        clean_data = clean_kobo_deployment_report(r) 
        
         
        cumulus_data = get_cumulus_nodes(
                    session,
                    int(r["name"].replace(common_name,"")),
                    survey_type
                )
        deployments = [
            *deployments,
            *match_deployment_to_node(clean_data,cumulus_data)]
        # before making another request in the loop
        # wait 2 second to not overload the server
        time.sleep(2)

    if len(deployments) > 0:
        # post data to zendro
        response = session.post(os.getenv("ZENDRO_URL")
                                + "/graphql",json={
                                    "query": "mutation {" +
                                        parse_to_graphql_query(
                                            deployments,
                                            survey_type) + "}"
                                })
        # generate a report 
        deployments_created = json.loads(response.text)["data"]
        print("Fueron creados %d reportes satisfactoriamente." % len(deployments_created))
    else:
        print("No hay nuevos desplieges que registrar.")


def build_n_post_individuals_n_erie_query(session,reports,survey_type):
    """
     Build the query to post to zendro from the data
     extracted for individuals and erie from kobo.

     Params:
        session (object):       Session object with auth credential
                                of zendro.
        reports (list):         A list containing the data of the 
                                reports.
        survey_type (string):   A string that indicates the type of
                                the surveys.

     Returns:
        (void) 
     """

    if survey_type == "individuals":
        clean_data = clean_kobo_individual_report(reports[0]) 
    elif survey_type == "erie":
        clean_data = clean_kobo_erie_report(reports[0])

    # sort data by cumulus
    sorted_data = sort_data_by_cumulus(clean_data)
    
    deployments = []
    for key,data in sorted_data.items():
        cumulus_data = get_cumulus_nodes(
                    session,
                    int(key.replace("sipecam","")),
                    survey_type
                )
        
        deployments = [
            *deployments,
            *match_deployment_to_node(data,cumulus_data)]
            
        # before making another request in the loop
        # wait 2 second to not overload the server
        time.sleep(2)
   
    if len(deployments) > 0:
        # post data to zendro
        response = session.post(os.getenv("ZENDRO_URL")
                                + "/graphql",json={
                                    "query": "mutation {" +
                                        parse_to_graphql_query(
                                            deployments,
                                            survey_type) + "}"
                                })
        # generate a report 
        deployments_created = json.loads(response.text)["data"]
        print("Fueron creados %d reportes de %s satisfactoriamente." % (
            len(deployments_created), "individuos" if survey_type == "individuals" else "erie"))
    else:
        print("No hay nuevas capturas de individuos que registrar.")
