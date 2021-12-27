def get_departments(_):
    departments = [
        {
            'externalId': 'dep1',
            'names': {
                'fi': 'Osasto 1',
                'sv': 'Avdelning 1',
                'en': 'Department 1'
            }
        },
        {
            'externalId': 'dep2',
            'names': {
                'fi': 'Osasto 2',
                'sv': 'Avdelning 2',
                'en': 'Department 2'
            }
        }
    ]
    return departments


def get_cost_centers(_):
    return []


def get_personnel(_):
    employees = [
        {
            'externalId': 'ceo',
            'ssn': '090977-954P',
            'callName': 'Cecily',
            'lastName': 'Ceo',
            'emailAddress': 'ceo@company.com',
            'localPhoneNumber': '0101234567',
            'startDate': '2016-01-02',
            'departments': [
                {
                    'externalId': 'dep2',
                    'startDate': '2016-01-02',
                    'endDate': '2016-12-31'
                },
                {
                    'externalId': 'dep1',
                    'startDate': '2017-01-01'
                }
            ]
        },
        {
            'externalId': 'emp1',
            'ssn': '161165-951M',
            'callName': 'Adam',
            'lastName': 'Ant',
            'emailAddress': 'adam.ant@company.com',
            'localPhoneNumber': '0101122334',
            'startDate': '2018-01-02',
            'endDate': '2020-12-31',
            'departments': [{
                'externalId': 'dep1',
                'startDate': '2018-01-02',
                'endDate': '2020-12-31'
            }],
            'supervisors': [{
                'externalId': 'ceo',
                'startDate': '2018-01-02',
                'endDate': '2020-12-31'
            }]
        },
        {
            'externalId': 'emp2',
            'ssn': '110674-9046',
            'callName': 'Betty',
            'lastName': 'Boo',
            'emailAddress': 'betty.boo@company.com',
            'localPhoneNumber': '0107654321',
            'startDate': '2017-01-02',
            'departments': [{
                'externalId': 'dep2',
                'startDate': '2017-01-02'
            }],
            'supervisors': [{
                'externalId': 'ceo',
                'startDate': '2017-01-02'
            }]
        }
    ]
    return employees
