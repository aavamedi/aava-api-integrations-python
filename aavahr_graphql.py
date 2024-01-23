import json
import logging

from urllib import request, error


def capfirst(text):
    """
    Only changes the case of first letter of string to capital,
    leaves others untouched, unlike capitalize()
    """
    return text[:1].upper() + text[1:]


def graphql_request(parameters: dict, payload: str) -> dict:
    """
    Performs the actual GraphQL request to Aava-API.

    Args:
        parameters (dict): Contains URL and credential information for API connection
        payload (str): A formatted GraphQL request

    Returns:
        dict: _description_
    """
    url = parameters["aavaApiServer"] + "/hr"
    req = request.Request(url, data=payload.encode("utf-8"), method="POST")
    req.add_header(
        "X-API-key", f"{parameters['clientId']}:{parameters['clientSecret']}"
    )
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/json")
    try:
        response = request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))

        if "errors" in result:
            error_messages = []
            for err in result["errors"]:
                locations = []
                for loc in err["locations"]:
                    locations.append(f"row {loc['line']}, column {loc['column']}")
                error_messages.append(f"{err['message']}, {' & '.join(locations)}")
            raise ValueError("\n".join(error_messages))

        return result["data"]
    except error.HTTPError:
        logging.critical(f"Error importing {type}s. Exiting.")
        exit()
    except ValueError as e:
        logging.error("Invalid content %s", e)
        return None


def format_query(type: str) -> str:
    """
    Format a mutation that can be sent to Aava-API

    Args:
        type (str): The type of import (department, costCenter, employee, absence)

    Returns:
        str: The formatted query string that can be passed to Aava-API
    """

    query = f"""
            mutation import{capfirst(type)}s(
                $organizationExternalId: ID!
                ${type}s: [{capfirst(type)}Input!]!
            ) {{
                import{capfirst(type)}s(
                organizationExternalId: $organizationExternalId
                {type}s: ${type}s
                ) {{
                    messageId
                }}
            }}
        """

    return query


def import_data(type: str, parameters: dict, data: dict) -> dict:
    """
    Performs the import query of a given type.

    Args:
        type (str): Type of import (department, costCenter, employee, absence)
        parameters (dict): URL and credentials for Aava-API
        data (dict): The data that is to be imported

    Returns:
        dict: _description_
    """
    request_data = {
        "query": format_query(type),
        "variables": {
            "organizationExternalId": parameters["organizationId"],
            f"{type}s": data,
        },
    }
    result = graphql_request(parameters=parameters, payload=json.dumps(request_data))
    return result


def import_departments(parameters: dict, departments: dict) -> dict:
    return import_data("department", parameters, departments)


def import_cost_centers(parameters: dict, costCenters: dict) -> dict:
    return import_data("costCenter", parameters, costCenters)


def import_employees(parameters: dict, employees: dict) -> dict:
    return import_data("employee", parameters, employees)


def import_absences(parameters: dict, absences) -> dict:
    return import_data("absence", parameters, absences)


def get_statuses(parameters: dict, message_ids: list) -> dict:
    """
    Used to query the status of import operations. Returns a list of status objects, each object containing
    the request ID ('messageId'), timestamp ('timestamp'), import type ('importType') and the current status
    of the operation (key 'importStatus', value one of UNKNOWN, IN_PROGRESS, FAILURE, DONE). If there is an
    error, the 'error' parameter contains a string telling about it. Also, if the operation was succesful
    with some minor hitches, the 'warnings' value gives more information about the problematic inputs.

    Args:
        parameters (dict): Parameters for connecting to Aava API (see properties-template.json)
        message_ids (list): An array containing the message IDs received from import requests

    Returns:
        dict: A dictionary object with key 'processingStatusWithVerify', under which there is an array of status objects
    """

    request_data = {
        "query": """
            query processingStatusWithVerify(
                $messageIds: [ID!]!
                $organizationExternalId: ID!
            ) {
                processingStatusWithVerify(
                    messageIds: $messageIds,
                    organizationExternalId: $organizationExternalId
                ) {
                    messageId,
                    importType,
                    importStatus,
                    timestamp,
                    error,
                    warnings { warning, externalId }
                }
            }
        """,
        "variables": {
            "messageIds": message_ids,
            "organizationExternalId": parameters["organizationId"],
        },
    }

    return graphql_request(parameters, json.dumps(request_data))
