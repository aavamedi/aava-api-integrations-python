import os
import csv
import pysftp
import paramiko
from base64 import decodebytes


def parse_date(datestring):
    # Timeplan return the date in format "dd-mm-yy"
    day, month, year = datestring.split('-')
    year = str(int(year) + 2000)
    return '{}-{}-{}'.format(year, month, day)


def get_absences(props):
    try:
        assert props != None, 'No hourTrackingSystem properties section'
        assert props['moduleName'] != None, 'Time tracking module name not set'
        assert props['host'] != None, 'Time tracking host not set'
        assert props['port'] != None, 'Time tracking server port not set'
        assert props['path'] != None, 'Time tracking file path not set'
        assert props['id'] != None, 'Time tracking user ID not set'
        assert props['pw'] != None, 'Time tracking password not set'
        assert props['hostKey'] != None, 'Time tracking hostKey not set'
    except Exception as ex:
        print("Properties file not complete:", repr(ex))
        exit()

    absences = []

    # For added security, the server's hostkey is verified against the one stored in properties
    bHostKey = str.encode(props['hostKey'])
    hostKey = paramiko.DSSKey(data=decodebytes(bHostKey))
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys.add(props['host'],
                        'ssh-rsa',
                        hostKey)

    tempfile = '__temp.csv'

    with pysftp.Connection(host=props['host'],
                           username=props['id'],
                           password=props['pw'],
                           cnopts=cnopts) as sftp:
        sftp.get(props['path'], tempfile)

    csvfile = open(tempfile, 'r')
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        external_id, start_date, end_date = row
        absence = {
            'externalId': external_id,
            'startDate': parse_date(start_date),
            'endDate': parse_date(end_date)
        }
        absences.append(absence)

    os.remove(tempfile)

    return absences
