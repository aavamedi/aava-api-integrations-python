import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def import_departments(parameters: dict, departments: dict) -> dict:
    """
    Imports the department information to Aava API.

    Args:
        parameters (dict): Parameters for connecting to Aava API (see properties-template.json)
        departments (dict): A dictionary object containing the department data (see simple_example_hrm.py)

    Returns:
        dict: Structure containing the request ID for querying the status of request; in r['importDepartments']['messageId']
    """

    mutation = '''
        mutation importDepartments(
            $organizationExternalId: ID!
            $departments: [DepartmentInput!]!
        ) {
            importDepartments(
            organizationExternalId: $organizationExternalId
            departments: $departments
            ) {
            messageId
            }
        }
    '''
    client = Client(transport=RequestsHTTPTransport(
        url=parameters['aavaApiServer'] + '/hr',
        headers={'X-API-key': parameters['clientId'] + ':' + parameters['clientSecret']})
    )

    query = gql(mutation)
    variables = {
        "organizationExternalId": parameters['organizationId'],
        "departments": departments,
    }

    result = client.execute(query, variable_values=json.dumps(variables))
    return result


def import_cost_centers(parameters: dict, costCenters: dict) -> dict:
    """
    Imports the cost center information to Aava API.

    Args:
        parameters (dict): Parameters for connecting to Aava API (see properties-template.json)
        costCenters (dict): A dictionary object containing the cost center data (similar to department data)

    Returns:
        dict: Structure containing the request ID for querying the status of request; in r['importCostCenters']['messageId']
    """

    mutation = '''
        mutation importCostCenters(
            $organizationExternalId: ID!
            $costCenters: [CostCenterInput!]!
        ) {
            importCostCenters(
            organizationExternalId: $organizationExternalId
            costCenters: $costCenters
            ) {
            messageId
            }
        }
    '''
    client = Client(transport=RequestsHTTPTransport(
        url=parameters['aavaApiServer'] + '/hr',
        headers={'X-API-key': parameters['clientId'] + ':' + parameters['clientSecret']})
    )

    query = gql(mutation)
    variables = {
        "organizationExternalId": parameters['organizationId'],
        "costCenters": costCenters,
    }

    result = client.execute(query, variable_values=json.dumps(variables))
    return result


def import_employees(parameters: dict, employees: dict) -> dict:
    """
    Imports the employee information retrieved from HRM to Aava API

    Args:
        parameters (dict): Parameters for connecting to Aava API (see properties-template.json)
        employees (dict): A dictionary object containing the employee data (see simple_example_hrm.py)

    Returns:
        dict: Structure containing the request ID for querying the status of request; in r['importEmployees']['messageId']
    """

    mutation = '''
        mutation importEmployees(
            $organizationExternalId: ID!
            $employees: [EmployeeInput!]!
        ) {
            importEmployees(
                organizationExternalId: $organizationExternalId
                employees: $employees
            ) {
            messageId
            }
        }
    '''
    client = Client(transport=RequestsHTTPTransport(
        url=parameters['aavaApiServer'] + "/hr",
        headers={'X-API-key': parameters['clientId'] + ':' + parameters['clientSecret']})
    )

    query = gql(mutation)
    variables = {
        "organizationExternalId": parameters['organizationId'],
        "employees": employees,
    }

    result = client.execute(query, variable_values=json.dumps(variables))
    return result


def import_absences(parameters: dict, absences) -> dict:
    """
    Imports the absence data retrieved from work hour tracking system to Aava API

    Args:
        parameters (dict): Parameters for connecting to Aava API (see properties-template.json)
        absences (dict): A dictionary object containing the absence data (see simple_example_time_tracker.py)

    Returns:
        dict: Structure containing the request ID for querying the status of request; in r['importAbsences']['messageId']
    """

    mutation = '''
        mutation importAbsences(
            $organizationExternalId: ID!
            $absences: [AbsenceInput!]!
        ) {
            importAbsences(
                organizationExternalId: $organizationExternalId
                absences: $absences
            ) {
                messageId
            }
        }
    '''
    client = Client(transport=RequestsHTTPTransport(
        url=parameters['aavaApiServer'] + "/hr",
        headers={'X-API-key': parameters['clientId'] + ':' + parameters['clientSecret']})
    )

    query = gql(mutation)
    variables = {
        "organizationExternalId": parameters['organizationId'],
        "absences": absences,
    }

    result = client.execute(query, variable_values=json.dumps(variables))
    return result


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

    query = gql('''
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
    ''')
    client = Client(transport=RequestsHTTPTransport(
        url=parameters['aavaApiServer'] + "/hr",
        headers={'X-API-key': parameters['clientId'] + ':' + parameters['clientSecret']})
    )

    variables = {
        "messageIds": message_ids,
        "organizationExternalId": parameters['organizationId']
    }

    result = client.execute(query, variable_values=json.dumps(variables))
    return result
