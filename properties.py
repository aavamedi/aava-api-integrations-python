import json
import shutil


PROPERTIES = None


def load_properties() -> dict:
    """
    Loads the properties from 'properties.json' to be used for connecting to
    Aava API and to specify the modules that are used for retrieving the employee
    and absence data from 


    Returns:
        dict: A dictionary object with a number of connection parameter sets;
            the parameter set for current connection is passed to import functions
    """

    global PROPERTIES

    if PROPERTIES:
        return PROPERTIES

    try:
        with open('properties.json') as json_file:
            PROPERTIES = json.load(json_file)

            # The properties file should contain a list of connections. If only one set of connection
            # parameters is provided, the list is created and this set included as the one and only
            if "connections" not in PROPERTIES:
                new_props = {'connections': [PROPERTIES]}
                PROPERTIES = new_props

            for conn in PROPERTIES['connections']:
                conn_name = ''
                if "connectionName" in conn:
                    conn_name = " in parameter set '{}'".format(
                        conn["connectionName"])
                assert "aavaApiServer" in conn, "aavaApiServer missing" + conn_name
                assert "clientId" in conn, "clientId missing" + conn_name
                assert "clientSecret" in conn, "clientSecret missing" + conn_name
                assert "organizationId" in conn, "organizationId missing" + conn_name
                assert "hrMgmtSystem" in conn, "hrMgmtSystem missing" + conn_name
                assert "moduleName" in conn["hrMgmtSystem"], "hrMgmtSystem.moduleName missing" + conn_name
                assert "hourTrackingSystem" in conn, "hourTrackingSystem missing" + conn_name
                assert "moduleName" in conn["hourTrackingSystem"], "hourTrackingSystem.moduleName missing" + conn_name

            return PROPERTIES

    except FileNotFoundError:
        shutil.copyfile('properties-template.json', 'properties.json')
        print('''
        Empty properties file has been created as 'properties.json'
        Fill in the connection parameters and rerun the script
        ''')
        exit()
    except AssertionError as e:
        print("Properties file not complete:")
        print(repr(e))
        exit()
