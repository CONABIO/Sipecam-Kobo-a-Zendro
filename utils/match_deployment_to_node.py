import os
import json

from helpers.clean_coordinates import clean_coordinates
from helpers.inverse_haversine import inverse_haversine
from helpers.validate_coordinates import validate_coordinates


def match_deployment_to_node(deployments, cumulus, session):
    """
    Given a list of deployments and a cumulus dict with its
    associated nodes and devices, matches a deployment with
    a node by the lat/long values of both.

    Parameters:
        deployments (list): A list of deployments

        cumulus (dict):   A dict containing the cumulus info.

        session (object):       Session object with auth credential
                                of zendro.

    Returns:
        matched_deployments (dict): A dict containing the matched
                                    deployments.
    """

    matched_deployments = []
    for d in deployments:
        m_deployment = {}
        registered = False
        if "devicesFilter" in cumulus.keys():
            for device in cumulus["devicesFilter"]:
                """
                Search for the device id by the device serial number
                """
                if d["device_serial"] == device["serial_number"]:
                    if len(device["device_deploymentsFilter"]) > 0:
                        """
                        if device has deployments, search if deployment
                        has not already been registered
                        """
                        for date in device["device_deploymentsFilter"]:
                            if date["date_deployment"] == d["date_deployment"]:
                                """
                                if found the same date_deployment for this device
                                then the deployment has already been registered
                                """
                                registered = True
                        if not registered:
                            m_deployment["device_id"] = device["id"]

                    else:
                        m_deployment["device_id"] = device["id"]

            if "device_id" not in m_deployment:
                """
                if device serial is not present in cumulus devices
                then retrieve device id from zendro server
                """
                response = session.post(os.getenv("ZENDRO_URL") 
                            + "/graphql",json={
                                "query": """
                                    query (
                                        $limit: Int!,
                                        $field: physical_deviceField,
                                        $value: String,
                                        $valueType: InputType,
                                        $operator: GenericPrestoSqlOperator
                                    )   {
                                          physical_devices(search: {
                                            field: $field,
                                            value: $value,
                                            valueType: $valueType,
                                            operator: $operator
                                          }, pagination: { limit: $limit }) {
                                            id
                                            device_deploymentsFilter(pagination:{limit:0}) {
                                                date_deployment
                                            }
                                          }
                                        }
                                """,
                                "variables": {
                                    "limit": 0,
                                    "field": "serial_number",
                                    "value": d["device_serial"],
                                    "valueType": "String",
                                    "operator": "eq"
                                }
                            })
                
                device_info = json.loads(response.text)["data"]["physical_devices"][0]

                for deployment in device_info["device_deploymentsFilter"]:
                    if deployment["date_deployment"] == d["date_deployment"]:
                        registered = True
                
                m_deployment["device_id"] = device_info["id"]

        elif "individualsFilter" in cumulus.keys():
            for individual in cumulus["individualsFilter"]:
                if individual["date_trap"] == d["date_trap"]:
                    """
                    if found the same date_trap for this individual catch
                    then the individual has already been registered
                    """
                    registered = True

        else:
            for node in cumulus["nodesFilter"]:
                for transect in node["transectsFilter"]:
                    if transect["date_transecto"] == d["date_transecto"]:
                        """
                        if found the same date_trap for this individual catch
                        then the individual has already been registered
                        """
                        registered = True

        if not registered:
            """
            if deployment is not registered in the
            database, then proceed to find the node
            where the device has been deployed
            """

            # parse coordinates to a valid format
            # e.g.: 1615568.0, 9358302.0 -> 16.16038, -93.50838
            latlng = validate_coordinates(
                clean_coordinates(d["latitude"], d["longitude"]), cumulus["geometry"]
            )

            dist = []
            match = []
            if latlng:
                for node in cumulus["nodesFilter"]:
                    # find the distance bewtween the device
                    # and the node with haversine function
                    dist.append(
                        inverse_haversine(
                            [float(latlng[0]), float(latlng[1])],
                            [
                                node["location"]["coordinates"][1],
                                node["location"]["coordinates"][0],
                            ],
                        )
                    )

                # searches the minimum distance between node
                # and device to get a match
                match = cumulus["nodesFilter"][dist.index(min(dist))]

            m_deployment.update(d)

            if (
                "individualsFilter" in cumulus.keys()
                or "devicesFilter" in cumulus.keys()
            ):
                m_deployment.update({"cumulus_id": cumulus["id"]})

            m_deployment.update(
                {
                    "node_id": match["id"] if latlng else "null",
                    "latitude": latlng[0] if latlng else "null",
                    "longitude": latlng[1] if latlng else "null",
                    "altitude": match["location"]["coordinates"][2]
                    if latlng
                    else "null",
                }
            )

            if (
                latlng
                or "devicesFilter" in cumulus.keys()
                or "individualsFilter" in cumulus.keys()
            ):
                matched_deployments.append(m_deployment)

    return matched_deployments
