import json
import importlib
from datetime import datetime
from time import sleep
from sys import argv
from enum import Enum

# All the API calls are wrapped in functions
import aavahr_graphql as api

# Properties are read using a specific mnodule
from properties import load_properties


class LOG_LEVEL(Enum):
    DEBUG = 0
    INFO = 1
    NOTICE = 2
    ERROR = 3
    CRITICAL = 4


def write_log(level, message):
    """
    Writes a log entry in the system log

    Args:
        level (LOG_LEVEL): [description]
        message (String): [description]
    """

    # If run manually, all this may be of interest to the user
    print(message)

    props = load_properties()

    if "logFile" in props:
        log_file = props['logFile']
    else:
        log_file = 'execution_log.txt'

    if "logLevel" in props:
        log_level = props['logLevel']
    else:
        log_level = LOG_LEVEL.NOTICE.value

    if level.value >= log_level:
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        lfile = open(log_file, 'a')
        lfile.writelines("\n{}: {:<8} {}".format(now, level.name, message))
        lfile.close()


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


def main():
    # Load the connection parameters or inform user that the parameter file is not found
    props = load_properties()

    args = get_command_line_arguments()

    message_ids = []

    # Run the imports for each connection
    index = 0
    for conn in props['connections']:
        conn_name = "Connection_#{}".format(index)
        index += 1

        if "connectionName" in conn:
            conn_name = conn['connectionName']

        if args['import_only_organization']:
            if args['import_only_organization'] != conn_name:
                write_log(LOG_LEVEL.INFO,
                          "Skipping import for '{}'".format(conn["connectionName"]))
                continue

        write_log(LOG_LEVEL.INFO,
                  "Running import for '{}'".format(conn["connectionName"]))

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

        if args['import_departments']:
            # Load department data from HRM adjacent system and push it to Aava-API
            deps = hrm.get_departments(conn["hrMgmtSystem"])
            if args['read_only']:
                print(json.dumps(deps, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(deps)) + " departments...")
                res_deps = api.import_departments(conn, deps)
                message_ids.append(res_deps['importDepartments']['messageId'])

        if args['import_cost_centers']:
            # Load cost center data from HRM adjacent system and push it to Aava-API
            ccs = hrm.get_cost_centers(conn["hrMgmtSystem"])
            if args['read_only']:
                print(json.dumps(ccs, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(ccs)) + " cost centers...")
                res_ccs = api.import_cost_centers(conn, ccs)
                message_ids.append(res_ccs['importCostCenters']['messageId'])

        if args['import_employees']:
            # Load employee data from HRM and push it to Aava-API
            emps = hrm.get_personnel(conn["hrMgmtSystem"])
            if args['read_only']:
                print(json.dumps(emps, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(emps)) + " employees...")
                res_emps = api.import_employees(conn, emps)
                message_ids.append(res_emps['importEmployees']['messageId'])

        if args['import_absences']:
            # Load absence data from hour trackin system and push it to Aava-API
            abs = ttr.get_absences(conn["hourTrackingSystem"])
            if args['read_only']:
                print(json.dumps(abs, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(abs)) + " absences...")
                res_abs = api.import_absences(conn, abs)
                message_ids.append(res_abs['importAbsences']['messageId'])

        print("Results:")

        while True:
            # Keep reading statuses until they are all ready
            ready = True
            results = api.get_statuses(conn, message_ids)

            for r in results['processingStatusWithVerify']:
                if r['importStatus'] == 'UNKNOWN' or r['importStatus'] == 'IN_PROGRESS':
                    ready = False

            if ready:
                break

            print('prosessing...')
            sleep(1)

        for r in results['processingStatusWithVerify']:
            write_log(LOG_LEVEL.NOTICE,
                      "For " + str(r['importType']) +
                      " at " + str(r['timestamp']))
            write_log(LOG_LEVEL.NOTICE,
                      "Message ID: " + r['messageId'])
            write_log(LOG_LEVEL.NOTICE,
                      "Status    : " + r['importStatus'])
            if r['importStatus'] == 'FAILURE':
                write_log(LOG_LEVEL.CRITICAL,
                          "Error     : " + r['error'])
            if r['warnings']:
                write_log(LOG_LEVEL.ERROR,
                          "There were warnings:")
                for warning in r['warnings']:
                    write_log(LOG_LEVEL.ERROR,
                              warning['warning'] + ' / ' + warning['externalId'])


if __name__ == "__main__":
    main()
