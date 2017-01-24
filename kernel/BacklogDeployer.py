import re
from jira.client import JIRA
from kernel import tool_settings

__author__ = "Manuel Escriche <mev@tid.es>"


class IssueDefinition:
    def __init__(self, sprint, deadline):
        self.project = None
        self.component = None
        self.sprint = sprint
        self._sprint = re.sub(r'\.', '', self.sprint)
        self.fixVersion = 'Sprint {}'.format(self.sprint)
        self.deadline = deadline
        self.inwards = []
        self.outwards = []
        self.issue = None
        self.assignee = None
        self.watchers = []
        self.reporter = None

    def description(self):
        raise NotImplementedError()

    def summary(self):
        raise NotImplementedError()


class BacklogDeployer:

    def __init__(self, task, description=False):
        server = tool_settings.server['JIRA']
        options = {'server': 'https://{}'.format(server.domain)}
        self.jira = JIRA(options, basic_auth=(server.username, server.password))
        self.task = task
        self.description = description

    def print(self):
        print('--> Backlog ')
        for k, issue in enumerate(self.task.issues, start=1):
            print(k, issue.summary(), ' : Deadline=', issue.deadline, ' : Assignee=', issue.assignee)
            if self.description:
                print(k, issue.description())
            for link in issue.inwards:
                print('\t in:', link.summary())
            for link in issue.outwards:
                print('\t out', link.summary())
            print('\n')

    def deploy(self):
        print('--> DEPLOYING')
        for iss_desc in self.task.issues:
            duedate = iss_desc.deadline.strftime('%Y-%m-%d') if iss_desc.deadline else None

            issue_dict = {'project': {'key': iss_desc.project},
                          'components': [{'id': iss_desc.component}],
                          'summary': iss_desc.summary(),
                          'description': iss_desc.description(),
                          'issuetype': {'name': 'WorkItem'},
                          'fixVersions': [{'name': iss_desc.fixVersion}],
                          'duedate': duedate}

            if iss_desc.reporter:
                issue_dict['reporter'] = {'name': iss_desc.reporter}

            issue = self.jira.create_issue(fields=issue_dict)

            if iss_desc.reporter:
                self.jira.remove_watcher(issue, 'mev')

            if iss_desc.assignee:
                self.jira.assign_issue(issue, iss_desc.assignee)

            if len(iss_desc.watchers):
                for watcher in iss_desc.watchers:
                    self.jira.add_watcher(issue, watcher)

            iss_desc.issue = issue
            print('Created:', issue, issue.fields.summary)
        for iss_desc in self.task.issues:
            for _iss_desc in iss_desc.outwards:
                self.jira.create_issue_link('relates to', iss_desc.issue, _iss_desc.issue)

    def monitor(self):
        print('--> MONITOR')
        for item in self.task.issues:
            print(item.issue, item.issue.fields.summary)

    def search(self):
        print('--> SEARCHING')
        for item in self.task.issues:
            seed = item.action
            query = 'component = {} and summary ~ {}'.format(item.component, seed)
            outcome = self.jira.search_issues(query)
            for issue in outcome:
                print(issue.fields.summary)

    def clean(self):
        print('--> CLEANING')
        for item in self.task.issues:
            print('removing: ', item.issue)
            try:
                item.issue.delete()
            except Exception as e:
                print(e)
                print("{} doesn't exit".format(item.issue))
