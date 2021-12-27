# Example modules

To kick start your integration project, some example modules are included. You
may freely copy and modify these modules to suit your purposes. There are a
couple of methods used for retrieving the data, like reading it from a locally
stored Excel, using HTTP/REST requests and fetching a CSV file over FTP. The
data structure is most apparent from simple example.

These modules depend on certain external libraries. They are included in the
requirements.txt file in the directory with main code, and are installed by
running pip command:

`pip install -r requirements.txt`

## Simple example

A module with hard coded value to demonstrate the data structure used for
sending data to the API.

Files:

```text
simple_example_hrm.py
simple_example_time_tracker.py
```

This module is preconfigured in the properties-template.json file, if you want
to play around with the data and see how it is transmitted over GraphQL.

## Excel example

This module is more closely resembling of a real life solution. It can even be
used as such by simply configuring a HR management system and Hour tracking systems
to produce Excel files with columns corresponding to the ones in the examples.

Files:

```text
excel_example_hrm.py
excel_example_time_tracker.py
excel_example_hrm.xlsx
excel_example_time_tracker.xlsx
excel_example_departments.xlsx
properties-excel-example.json
```

This example also shows, how module specific properties can be configured in the
properties JSON file. Copy the example JSON to the parent directory with name
properties.json to use it as the basis for your further development.

## SympaHR example

This is a copy of the actual module used by Aava itself (with very minor changes).
Since in our setup the departments can not be fetched from SympaHR with a separate
query, both departments and employees are retrieved in one run. Also, the department
ID is not available through the REST API, so a unique identifier is generated from
the Finnish name of the department.

Files:

```text
properties-sympahr-example.json
sympahr_example_hrm.py
```

The module specific properties are the URL of the REST API, username and password. These
can be either requested from Sympa or they can be generated with SympaHR admin tools. The
values in example properties file are copied from Sympa Integration Guide, and do not work.

## Timeplan example

This also is a copy of an Aava module, used for fetching absence data. The information is
stored in a CSV file and it is retrieved using SFTP. The file name is assumed to always be
the same to make the implementation simpler.

Files:

```text
properties-timeplan-example.json
timeplan_example_hrm.py
```
