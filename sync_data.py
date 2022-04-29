import json
import importlib
from os import write
from time import sleep
from sys import argv

# All the API calls are wrapped in functions
import aavahr_graphql as api

# Properties are read using a specific mnodule
from prop_handler import load_properties

# There is also a module for handling writing to logs
from log_handler import LOG_LEVEL, write_log, set_log_file, set_log_level


def get_command_line_arguments():
    arguments = {
        'import_departments': True,
        'import_cost_centers': True,
        'import_employees': True,
        'import_absences': True,
        'import_only_organization': None,
        'read_only': False
    }

    # Check the command line parameters to see, what is required of this run
    acceptable_args = {
        '--suppress_deps': 'Skips importing departments',
        '--suppress_ccs': 'Skips importing cost centers',
        '--suppress_employees': 'Skips importing employee information',
        '--suppress_absences': 'Skips importing absence information',
        '-sd': 'Short for --suppress_deps',
        '-sc': 'Short for --suppress_ccs',
        '-se': 'Short for --suppress_employees',
        '-sa': 'Short for --suppress_absences',
        '--import_org': 'Only import named organization',
        '--read_only': 'Only read the information and show output on screen, do not call API',
        '--help': 'Show this help',
    }

    if '--help' in argv:
        print('''This script reads the employee and absence data from specified source
and sends it to Aava-API.

How to use:
python sync_data.py [--help] [--suppress_deps] [--suppress_employees]
    [--suppress_absences] [--import_org "<org name>"] [--read_only]

Options:''')
        for k_arg in acceptable_args.keys():
            print(" {:<20} - {}".format(k_arg, acceptable_args[k_arg]))
        exit()

    cli_args = argv[1:]
    while len(cli_args) > 0:
        a = cli_args.pop(0)
        if a not in acceptable_args:
            print('Argument ' + a + ' not recognized, exiting!')
            exit()

        if a == '-sd' or a == '--suppress_deps':
            arguments['import_departments'] = False

        if a == '-sc' or a == '--suppress_ccs':
            arguments['import_cost_centers'] = False

        if a == '-se' or a == '--suppress_employees':
            arguments['import_employees'] = False

        if a == '-sa' or a == '--suppress_absences':
            arguments['import_absences'] = False

        if a == '--read_only':
            arguments['read_only'] = True

        if a == '--import_org':
            org = cli_args.pop(0)
            arguments['import_only_organization'] = org

    return arguments


def process_results(conn, msg_id):
    while True:
        # Keep reading status until it is ready
        res = api.get_statuses(conn, [msg_id])
        status = res['processingStatusWithVerify']
        if status[0]['importStatus'] not in ['UNKNOWN', 'IN_PROGRESS']:
            break
        print('processing...')
        sleep(1)

    write_log(LOG_LEVEL.NOTICE,
              "For " + str(status[0]['importType']) +
              " at " + str(status[0]['timestamp']))
    write_log(LOG_LEVEL.NOTICE,
              "Message ID: " + status[0]['messageId'])
    write_log(LOG_LEVEL.NOTICE,
              "Status    : " + status[0]['importStatus'])
    if status[0]['importStatus'] == 'FAILURE':
        write_log(LOG_LEVEL.CRITICAL,
                  "Error     : " + status[0]['error'])
    if status[0]['warnings']:
        write_log(LOG_LEVEL.ERROR,
                  "There were warnings:")
        for warning in status[0]['warnings']:
            write_log(LOG_LEVEL.ERROR,
                      warning['warning'] + ' / ' + warning['externalId'])


def main():
    # Load the connection parameters or inform user that the parameter file is not found
    props = load_properties()
    if "logFile" in props:
        set_log_file(props["logFile"])

    if "logLevel" in props:
        set_log_level(LOG_LEVEL(props["logLevel"]))

    args = get_command_line_arguments()

    # Run the imports for each connection
    index = 0
    for conn in props['connections']:
        # If there is are connection specific log settings that should be used, they are set now
        if "logFile" in conn:
            set_log_file(conn["logFile"])
        elif "logFile" in props:
            set_log_file(props["logFile"])
        else:
            set_log_file(None)

        if "logLevel" in conn:
            set_log_level(LOG_LEVEL(conn["logLevel"]))
        elif "logLevel" in props:
            set_log_level(LOG_LEVEL(props["logLevel"]))
        else:
            set_log_level(None)

        index += 1
        conn_name = "Connection_#{}".format(index)

        if "connectionName" in conn:
            conn_name = conn['connectionName']

        if args['import_only_organization']:
            if args['import_only_organization'] != conn_name:
                write_log(LOG_LEVEL.INFO,
                          "Skipping import for '{}'".format(conn_name))
                continue

        write_log(LOG_LEVEL.INFO,
                  "Running import for '{}'".format(conn_name))

        # Personnel and department data fetching is wrapped in one source file,
        # absences in another one.
        try:
            hrm = importlib.import_module(
                conn["hrMgmtSystem"]["moduleName"]
            )
            ttr = importlib.import_module(
                conn["hourTrackingSystem"]["moduleName"]
            )
        except ModuleNotFoundError as e:
            print("Module loading failed:", repr(e))
            exit()

        # Load department data from HRM adjacent system and push it to Aava-API
        if args['import_departments']:
            deps = hrm.get_departments(conn["hrMgmtSystem"])
            if args['read_only']:
                print(json.dumps(deps, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(deps)) + " departments...")
                res = api.import_departments(conn, deps)
                process_results(conn, res['importDepartments']['messageId'])

        # Load cost center data from HRM adjacent system and push it to Aava-API
        if args['import_cost_centers']:
            ccs = hrm.get_cost_centers(conn["hrMgmtSystem"])
            if args['read_only']:
                print(json.dumps(ccs, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(ccs)) + " cost centers...")
                res = api.import_cost_centers(conn, ccs)
                process_results(conn, res['importCostCenters']['messageId'])

        # Load employee data from HRM and push it to Aava-API
        if args['import_employees']:
            emps = hrm.get_personnel(conn["hrMgmtSystem"])
            if args['read_only']:
                print(json.dumps(emps, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(emps)) + " employees...")
                res = api.import_employees(conn, emps)
                process_results(conn, res['importEmployees']['messageId'])

        # Load absence data from hour trackin system and push it to Aava-API
        if args['import_absences']:
            abs = ttr.get_absences(conn["hourTrackingSystem"])
            if args['read_only']:
                print(json.dumps(abs, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(abs)) + " absences...")
                res = api.import_absences(conn, abs)
                process_results(conn, res['importAbsences']['messageId'])


if __name__ == "__main__":
    main()
