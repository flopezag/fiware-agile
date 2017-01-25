__author__ = 'Manuel Escriche'

import base64, certifi, requests
from kconfig import settings

class ConnectionToJIRA(Exception):
    pass

class JIRA:
    _fields = '*navigable'
    fields = 'summary,status,project,components,priority,issuetype,description,reporter,' \
             'resolution,assignee,created,updated,duedate,resolutiondate,fixVersions,releaseDate,issuelinks,' \
             'customfield_11103,customfield_11104,customfield_11105'
    verify = False

    url_api = {
        'project': '/rest/api/latest/project',
        'component': '/rest/api/latest/component/',
        'search': '/rest/api/latest/search',
        'issue': '/rest/api/latest/issue'
    }

    def __init__(self):
        username = settings.server['JIRA'].username
        password = settings.server['JIRA'].password
        auth = '{}:{}'.format(username, password)
        keyword = base64.b64encode(bytes(auth,'utf-8'))
        access_key = str(keyword)[2:-1]
        headers = {'Content-Type': 'application/json', "Authorization": "Basic {}".format(access_key)}
        self.root_url = 'https://{}'.format(settings.server['JIRA'].domain)
        #print(self.root_url)
        self.session = requests.session()

        #url = '{}{}'.format(self.root_url, JIRA.url_api['session'])
        try:
            answer = self.session.get(self.root_url, headers = headers, verify=JIRA.verify)
        except ConnectionError:
            raise Exception
        if answer.status_code != requests.codes.ok:
            raise ConnectionToJIRA

        self.session.headers.update({'Content-Type': 'application/json'})

    def search(self, params):
        url = '{}{}'.format(self.root_url, JIRA.url_api['search'])
        try:
            answer = self.session.get(url, params=params, verify=JIRA.verify)
        except Exception:
            raise ConnectionToJIRA
        #print(answer.url)
        data = answer.json()
        return data

    def getComponentData(self, comp_id):
        startAt = 0
        payload = {'fields':JIRA.fields,
                   'maxResults':1000, 'startAt':startAt,
                   'jql':'component={}'.format(comp_id) }
        try:
            data = self.search(payload)
        except Exception:
            raise Exception
        totalIssues, receivedIssues = data['total'], len(data['issues'])
        while totalIssues > receivedIssues:
            payload['startAt'] = receivedIssues
            try:
                data['issues'].extend(self.search(payload)['issues'])
            except Exception:
                raise Exception
            receivedIssues = len(data['issues'])
        return data['issues']

    def getTrackerData(self, tracker_id):
        startAt = 0
        payload = {'fields':JIRA.fields,
                   'maxResults':1000, 'startAt':startAt,
                   'jql':'project={}'.format(tracker_id) }
        try:
            data = self.search(payload)
        except Exception:
            raise Exception
        totalIssues, receivedIssues = data['total'], len(data['issues'])
        while totalIssues > receivedIssues:
            payload['startAt'] = receivedIssues
            try:
                data['issues'].extend(self.search(payload)['issues'])
            except Exception:
                raise Exception
            receivedIssues = len(data['issues'])
        return data['issues']

    def getQuery(self, jql):
        startAt = 0
        payload = {'fields': JIRA.fields,
                   'maxResults':1000, 'startAt':startAt,
                   'jql': jql }
        try:
            data = self.search(payload)
        except Exception:
            raise Exception
        totalIssues, receivedIssues = data['total'], len(data['issues'])
        while totalIssues > receivedIssues:
            payload['startAt'] = receivedIssues
            try:
                data['issues'].extend(self.search(payload)['issues'])
            except Exception:
                raise Exception
            receivedIssues = len(data['issues'])
        return data['issues']

    def getIssue(self, id):
        url = '{}{}/{}'.format(self.root_url, JIRA.url_api['issue'], id)
        try:
            answer = self.session.get(url, verify=JIRA.verify)
        except Exception:
            raise ConnectionToJIRA
        #print(answer.url)
        data = answer.json()
        return data
