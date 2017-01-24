__author__ = "Manuel Escriche <mev@tid.es>"

import base64, certifi, requests
from kconfig import settings

class ConnectionToJIRA(Exception):
    pass

class Connector:

    url_api = {
        'session':'/rest/auth/1/session',
        'project':'/rest/api/latest/project',
        'component':'/rest/api/latest/component/',
        'search':'/rest/api/latest/search',
        'user': '/rest/api/latest/user'
    }
    instance = None
    verify = False

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
             cls.instance = Connector()
        return cls.instance

    def __init__(self):
        if Connector.instance is not None:
            raise ValueError("An instantiation already exists!")
        self._connect()

    def _connect(self):
        username = settings.server['JIRA'].username
        password = settings.server['JIRA'].password
        auth = '{}:{}'.format(username, password)
        keyword = base64.b64encode(bytes(auth,'utf-8'))
        access_key = str(keyword)[2:-1]
        headers = {'Content-Type': 'application/json', "Authorization": "Basic {}".format(access_key)}
        self.root_url = 'https://{}'.format(settings.server['JIRA'].domain)
        #print(self.root_url)
        self.session = requests.session()

        #url = '{}{}'.format(self.root_url, Connector.url_api['session'])
        answer =  self.session.get(self.root_url, headers = headers, verify=Connector.verify)
        if answer.status_code != requests.codes.ok:
            raise ConnectionToJIRA

        self.session.headers.update({'Content-Type': 'application/json'})

    def component(self, cmp_id):
        #print('component')
        url = '{}{}{}'.format(self.root_url, Connector.url_api['component'], cmp_id)
        try:
            answer = self.session.get(url, verify=Connector.verify)
        except Exception:
            try:
                self._connect()
                answer = self.session.get(url, verify=Connector.verify)
            except Exception:
                raise ConnectionToJIRA

        data = answer.json()
        return data

    def componentLeader(self, cmp_id):
        url = '{}{}{}'.format(self.root_url, Connector.url_api['component'], cmp_id)
        try:
            answer = self.session.get(url, verify=Connector.verify)
        except Exception:
            return 'Unknown'

        data = answer.json()
        return data['realAssignee']['displayName']

    def tracker(self, tracker_id):
        #print('tracker')
        url = '{}{}{}'.format(self.root_url, Connector.url_api['project'], tracker_id)
        try:
            answer = self.session.get(url, verify=Connector.verify)
        except Exception:
            try:
                self._connect()
                answer = self.session.get(url, verify=Connector.verify)
            except Exception:
                raise ConnectionToJIRA
        #print(answer.url)
        data = answer.json()
        return data

    def trackerLeader(self, tracker_id):
        url = '{}{}/{}?lead'.format(self.root_url, Connector.url_api['project'], tracker_id)
        try:
            answer = self.session.get(url, verify=Connector.verify)
        except Exception:
            try:
                self._connect()
                answer = self.session.get(url, verify=Connector.verify)
            except Exception:
                raise ConnectionToJIRA
        data = answer.json()
        return data['lead']['displayName']

    def search(self, params):
        #print('search')
        url = '{}{}'.format(self.root_url, Connector.url_api['search'])
        #print(url)
        try:
            answer = self.session.get(url, params=params, verify=Connector.verify)
        except Exception:
            try:
                self._connect()
                answer = self.session.get(url, params=params, verify=Connector.verify)
            except Exception:
                raise ConnectionToJIRA
        #print(answer.url)
        data = answer.json()
        return data

    def displayName(self, username):
        url = '{}{}'.format(self.root_url, Connector.url_api['user'])
        params = {'username': username }
        for n in range(0,1):
            try:
                answer = self.session.get(url, params=params, verify=Connector.verify)
            except Exception:
                if n: raise ConnectionToJIRA
            else: break
        #print(answer.url)
        data = answer.json()
        return data['displayName']

class JIRA:
    _fields = '*navigable'
    fields = 'summary,status,project,components,priority,issuetype,description,reporter,' \
             'resolution,assignee,created,updated,duedate,resolutiondate,fixVersions,releaseDate,issuelinks'
    verify = False
    url_api = {
        'session':'/rest/auth/1/session',
        'project':'/rest/api/2/project',
        'component':'/rest/api/2/component/',
        'search':'/rest/api/2/search'
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
        answer =  self.session.get(self.root_url, headers = headers, verify=JIRA.verify)
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


if __name__ == "__main__":
    pass