# Reference implementation for integrating personnel and hour tracking systems with Aava API

This is the implementation for entering personnel data from an HR management system
and absence data from hour tracking system and using GraphQL interface for pushing them to
AavaHR via Aava API.

Example modules for verifying the API without fetching actual data from anywhere are included
and can be found in the 'examples' folder.

Also, to see if the data fetched from HRM system or hour tracker by your module makes sense, you
can run the script using the "--read_only" argument, in which case the retrieved results are
printed out instead of sent to API.

## Making a copy of the repository

In order to seamlessly add your own code on top of the basic building blocks of
the reference implementation, you should create your own repository in, for example,
Github. Have the reference implementation as a read-only remote, so you can easily
refresh any new feature additions or bug fixes.

Copy following commands to a text editor, replace the repository user and name with
your own, then run it on console (will require some tuning for Windows).

```sh
export REPO_USER=github-user
export REPO_NAME=new-integration-repo
git clone --bare git@github.com:aavamedi/aava-api-integrations-python.git
cd aava-api-integrations-python.git
git push --mirror git@github.com:$REPO_USER/$REPO_NAME.git
cd ..
rm -rf aava-api-integrations-python.git
git clone git@github.com:$REPO_USER/$REPO_NAME.git
cd $REPO_NAME
git remote add reference git@github.com:aavamedi/aava-api-integrations-python.git
git remote set-url --push reference DISABLE
```

Later, to update the codes from the reference implementatio, just run the
following commands:

```sh
git fetch reference
git rebase reference/master
```

## Prerequisites

Python must be installed. This code has been verified as working on Python 3.8.5. While there
should be no problems using 3.7 or newer, no testing with any other version has been made.

Some module are also required for this, install them using pip

`pip install -r requirements.txt`

## Running the program

### Before running

Connection to Aava API requires certain parameters to be set in properties.json file. You
can create it by copying the properties-template.json or by copying the following code block.

```json
{
  "connections": [
    {
      "connectionName": "Example Company",
      "aavaApiServer": "https://api-test.aava.fi",
      "clientId": "<ask from your aava representative>",
      "clientSecret": "<ask from your aava representative>",
      "organizationId": "<ask from your aava representative>",
      "hrMgmtSystem": {
        "moduleName": "hrm_module"
      },
      "hourTrackingSystem": {
        "moduleName": "time_tracker_module"
      }
    }
  ]
}
```

For testing, the server address can also be <https://api-test.aava.fi>.

Objects "hrMgmtSystem" and "hourTrackingSystem" refer to the HR management system and hour
tracking system modules, respectively. When you create your own module for reading the data
from your systems, change this to the name of the module you will be using.

Rest of the parameters you will receive from your Aava contact.

If the file is not available upon execution, an empty one will be created but it must be
filled before the program can work correctly.

### Executing the program

Import is executed from command line with the command:

`python sync_data.py`

Following command line options are available:

`-sd / --suppress_deps` Departments are ignored: they are neither read from the source nor
sent to the API

`-sc / --suppress_ccs` Cost centers are ignored: they are neither read from the source nor
sent to the API

`-se / --suppress_employees` Employee data is ignored: it is neither read from the source nor
sent to the API

`-sa / --suppress_absences` Absence data is ignored: it is neither read from the source nor
sent to the API

`--import_org` When multiple connections have been defined in the properties file, this
argument can be used for importing data for only one of the organizations. The organization's
name is given as the next argument (in "quotes").

`--read_only` This is useful for testing the data read: the information is retrieved from the
source, but it is not sent to the API

### Examples

`python sync_data.py --read_only --suppress_employees --suppress_absences`

Only retrieves department and cost center information and prints it out on the screen. Printout
will be something along the lines of:

```json
[
    {
        "externalId": "prod",
        "names": {
            "en": "Production",
            "fi": "Tuotanto"
        }
    },
    {
        "externalId": "rnd",
        "names": {
            "en": "Research and Development",
            "fi": "Kehitys"
        }
    },
    ...
]
[
    {
        "externalId": "cc1234",
        "names": {
            "en": "General Administration",
            "fi": "Yleishallinto"
        }
    },
    {
        "externalId": "cc2345",
        "names": {
            "en": "Salaried employees",
            "fi": "Tuntipalkkaiset työntekijät"
        }
    },
    ...
]
```

`python sync_data.py --read_only -sd -sc -sa`

Only retrieves and prints out the employee data without invoking the API. This kind of information may
be shown on the console:

```json
[
    {
        "callName": "Kari-Matti",
        "departments": [
            {
                "externalId": "admin",
                "startDate": "2013-07-31"
            }
        ],
        "emailAddress": "kari-matti.hokkanen@corporate.com",
        "externalId": "A01010",
        "lastName": "Hokkanen",
        "localPhoneNumber": "0115745316",
        "ssn": "161165-951M",
        "startDate": "2013-07-31"
    },
    {
        "callName": "Taavi",
        "departments": [
            {
                "externalId": "admin",
                "startDate": "2014-09-20"
            }
        ],
        "emailAddress": "taavi.eriksson@corporate.com",
        "externalId": "A01011",
        "lastName": "Eriksson",
        "localPhoneNumber": "0112000585",
        "ssn": "281278-9030",
        "startDate": "2014-09-20",
        "supervisors": [
            {
                "externalId": "A01010",
                "startDate": "2014-09-20"
            }
        ]
    },
    {
        "callName": "Lumia",
        "departments": [
            {
                "externalId": "admin",
                "startDate": "2019-02-18"
            }
        ],
        "emailAddress": "lumia.nissil\u00e4@corporate.com",
        "externalId": "A01012",
        "lastName": "Nissil\u00e4",
        "localPhoneNumber": "0115392274",
        "ssn": "090977-954P",
        "startDate": "2019-02-18",
        "supervisors": [
            {
                "externalId": "A01010",
                "startDate": "2019-02-18"
            }
        ]
    },
    ...
]
```

## Technical details

In order to implement a new data retriever for HRM or time tracker system, a new module should
be written. The modules must implement certain functions as explained in following sections.

If the modules return the required values in correct format, there is no need to touch any of the
original code. Only the parameters in properties.json file need to be changed.

If the HRM or time tracker data fetchers require additional parameters to be passed to them,
such parameters can be added in the "hrMgmtSystem" or "hourTrackingSystem" sections in the
properties.json file. These sections are passed as parameters to the invoked functions.

**Note!** The fields supported by Aava API may change over time. Please refer to the schema
exposed at <https://api.aava.fi/hr> for up to date information.

### HR management system integration module

`get_departments(props)`

Retrieves the department data from HRM or other source as an array whose items are dictionary
objects. Each object must be of following structure:

```json
{
    "externalId": "<any string>",
    "names": {
        "en": "<human readable department name in English>",
        "fi": "<human readable department name in Finnish>",
        "sv": "<human readable department name in Swedish>"
    }
}
```

Not all languages are required, but of course it helps to have at least one human readable name.
External ID should be permanent, so any changes to the department names can be handled correctly.

`get_cost_centers(props)`

Retrieves the cost center data from HRM or other source as an array whose items are dictionary
objects. Each object must be of following structure:

```json
{
    "externalId": "<any string>",
    "names": {
        "en": "<human readable cost center name in English>",
        "fi": "<human readable cost center name in Finnish>",
        "sv": "<human readable cost center name in Swedish>"
    }
}
```

Not all languages are required, but of course it helps to have at least one human readable name.
External ID should be permanent, so any changes to the cost center names can be handled correctly.

`get_personnel(props)`

Retrieves the personnel data from HRM. Returned value is an array with dictionary objects as
its members. The objects must be of following structure:

```json
{
    "externalId": "<any string>",
    "ssn": "<social security number, optional>",
    "callName": "<First name of the employee>",
    "lastName": "<Last name of the employee>",
    "emailAddress": "<valid email address, optional>",
    "localPhoneNumber": "<phone number without country code, optional>",
    "startDate": "<start date of employment in format YYYY-MM-DD>",
    "endDate": "<end date of employment in format YYYY-MM-DD, optional>",
    "departments": [
        {
            "externalId": "<an external ID as sent in department info>",
            "startDate": "<date of starting at the department in format YYYY-MM-DD>",
            "endDate": "<date of leaving the department in format YYYY-MM-DD, optional>"
        }
    ],
    "supervisors": [
        {
            "externalId": "<the external ID of the supervisor as submitted with this function>",
            "startDate": "<date when sup-sub relationship started in format YYYY-MM-DD>",
            "endDate": "<date when sup-sub relationship ended in format YYYY-MM-DD, optional>"
        }
    ]
}
```

Any number of superior-subordinate relationships and employments at various departments may be submitted.
Nevertheless, the "departments" and "supervisors" values must be arrays with dictionary objects.

Do note that the external IDs may be provided by the external systems in which case they should be used.
Regardless, it is essential that each external ID persistently points to the same entity, as this
guarantees the coherency of data stored in AavaHR.

### Hour tracking system integration module

`get_absences(props)`

This function returns an array with dictionary objects of following structure:

```json
{
    "externalId": "<external ID of the employee (see previous section)>",
    "startDate": "<start date of absence in format YYYY-MM-DD>",
    "endDate": "<end date of absence in format YYYY-MM-DD, optional>",
    "approvalType": "<Supervisor | Doctor | Nurse, optional>"
}
```

External ID _must_ be the same as was used when retrieving data from HRM system. Approval type is
optional, and may not even be available from the hour tracking system, so don't sweat it.
