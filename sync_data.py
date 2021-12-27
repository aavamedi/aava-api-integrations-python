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


def main():
    # Check the command line parameters to see, what is required of this run
    acceptable_args = [
        '--help',
        '-sd', '--suppress_deps',
        '-se', '--suppress_employees',
        '-sa', '--suppress_absences',
        '-sc', '--suppress_ccs',
        '--read_only'
    ]

    for a in argv[1:]:
        if a not in acceptable_args:
            print('Argument ' + a + ' not recognized, exiting!')
            exit()

    if '--help' in argv:
        print('''
        How to use:
        python sync_data.py [--help | --suppress_deps | --suppress_employees | --suppress_absences | --read_only ]

        Options:
        --help - Show this help
        -sd / --suppress_deps - Don't read or write department information
        -se / --suppress_employees - Don't read or write employee information
        -sa / --suppress_absences - Don't read or write absence information
        -sc / --suppress_ccs - Don't read or write cost center information
        --read_only - Don't make API call, only print out the data that was read from source
        ''')
        exit()

    process_departments = '-sd' not in argv and '--suppress_deps' not in argv
    process_cost_centers = '-sc' not in argv and '--suppress_ccs' not in argv
    process_employees = '-se' not in argv and '--suppress_employees' not in argv
    process_absences = '-sa' not in argv and '--suppress_absences' not in argv

    # Load the connection parameters or inform user that the parameter file is not found
    props = load_properties()

    message_ids = []

    # Run the imports for each connection
    for conn in props['connections']:
        if "connectionName" in conn:
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

        if process_departments:
            # Load department data from HRM adjacent system and push it to Aava-API
            deps = hrm.get_departments(conn["hrMgmtSystem"])
            if '--read_only' in argv:
                print(json.dumps(deps, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(deps)) + " departments...")
                res_deps = api.import_departments(conn, deps)
                message_ids.append(res_deps['importDepartments']['messageId'])

        if process_cost_centers:
            # Load cost center data from HRM adjacent system and push it to Aava-API
            ccs = hrm.get_cost_centers(conn["hrMgmtSystem"])
            if '--read_only' in argv:
                print(json.dumps(ccs, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(ccs)) + " cost centers...")
                res_ccs = api.import_cost_centers(conn, ccs)
                message_ids.append(res_ccs['importCostCenters']['messageId'])

        if process_employees:
            # Load employee data from HRM and push it to Aava-API
            emps = hrm.get_personnel(conn["hrMgmtSystem"])
            if '--read_only' in argv:
                print(json.dumps(emps, indent=4, sort_keys=True))
            else:
                write_log(LOG_LEVEL.NOTICE,
                          "Importing " + str(len(emps)) + " employees...")
                res_emps = api.import_employees(conn, emps)
                message_ids.append(res_emps['importEmployees']['messageId'])

        if process_absences:
            # Load absence data from hour trackin system and push it to Aava-API
            abs = ttr.get_absences(conn["hourTrackingSystem"])
            if '--read_only' in argv:
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
