import re
from datetime import datetime, timedelta
from jira import JIRA
from kconfig import chaptersBook, workGroupBook, labsBookByName
from kconfig import agileCalendar
from kernel import tool_settings
from kernel.BacklogDeployer import BacklogDeployer

__author__ = 'Manuel Escriche'

__version__ = '1.2.0'

retrospective_pattern = '# Retrospective Pattern:\n' +\
                '#* {color:blue}What went well{color}\n' \
                '#** identify aspects working smoothly\n' \
                '#* {color:blue}What to improve{color}\n' \
                '#** identify aspects making progress difficult\n'

reminders = '+Reminders:+\n' + \
            '# Issues left open are moved forward to next sprint automatically at sprint closing time\n' +\
            '# WorkItems almost finished can be closed, and then cloned for the next sprint\n' +\
            retrospective_pattern


class IssueDefinition:
    def __init__(self, action, sprint, deadline):
        self.project = None
        self.component = None
        self.action = action
        self.sprint = sprint
        self._sprint = re.sub(r'\.', '', self.sprint)
        self.fixVersion = 'Sprint {}'.format(self.sprint)
        self.deadline = deadline
        self.inwards = []
        self.outwards = []
        self.issue = None
        self.assignee = None
        self.watchers = []

    def description(self):
        raise NotImplementedError()

    def summary(self):
        raise NotImplementedError()


class SourceIssue(IssueDefinition):
    _type = 'source'

    def __init__(self, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.project = 'COR'
        self.component = '10249'
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' + self.fixVersion + '*{color}+\n' + \
                '# Create hierarchically backlog issues for all tech chapters leaders and GE owners\n' + \
                '# Create hierarchically backlog issues for all working group leaders and groups\n' + \
                '# Schedule and attend sprint closing meetings for all tech chapters and working groups\n' + \
                '# Take backlog snapshot for ' + self.fixVersion + '\n' + \
                '# Close effectively ' + self.fixVersion + ' on {color:red}' + \
               self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n' + \
                '# Share sprint closing outcome with project partners \n'

    def summary(self):
        return 'FIWARE.WorkItem.Coordination.Agile.Sprint-{}.{}'.format(self._sprint, self.action)


class ScrumMasterRetrospectiveIssue(IssueDefinition):
    _type = 'coordination'

    def __init__(self, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.project = 'COR'
        self.component = '10249'
        self.reporter = 'backlogmanager'

    def description(self):
        return "# Drawn from {color:blue}Chapter's and Working Group's Summary " \
               "Retrospectives{color} the {color:red}Global Retrospective{color} \n" +\
                          "# Share Global Retrospective " + retrospective_pattern

    def summary(self):
        return 'FIWARE.WorkItem.Coordination.Agile.Sprint-{}.{}'.format(self._sprint, self.action)


class ChapterIssue(IssueDefinition):
    _type = 'chapter'

    def __init__(self, chapter, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.chapter = chapter
        _chapter = chaptersBook[chapter]
        self.project = _chapter.coordination.tracker
        self.component = _chapter.coordination.key
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' \
               + self.fixVersion + '*{color}+\n' + \
               '# Close your coordination backlog issues finished during the sprint\n' +\
               '# Update your help desk issues linked to the backlog\n' +\
               "# Verify chapter enabler/tools's backlog are properly closed\n" + \
               "# Verify chapter enabler/tools's retrospective are provided in time\n" +\
               '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n'

    def summary(self):
        return 'FIWARE.WorkItem.{}.Coordination.Agile.Sprint-{}.{}'\
            .format(self.chapter, self._sprint, self.action)


class ChapterRetrospectiveIssue(IssueDefinition):
    _type = 'chapter'

    def __init__(self, chapter, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.chapter = chapter
        _chapter = chaptersBook[chapter]
        self.project = _chapter.coordination.tracker
        self.component = _chapter.coordination.key
        self.reporter = 'backlogmanager'

    def description(self):
        return "# Drawn {color:red} Chapter Summary Retrospective{color} " \
               "from {color:blue} Enablers' Retrospectives{color} \n" +\
                retrospective_pattern

    def summary(self):
        return 'FIWARE.WorkItem.{}.Coordination.Agile.Sprint-{}.{}'\
            .format(self.chapter, self._sprint, self.action)


class EnablerIssue(IssueDefinition):
    _type = 'enabler'

    def __init__(self, chapter, enabler, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.enabler = enabler
        self.chapter = chapter
        self._chapter = chaptersBook[chapter]
        self._enabler = self._chapter.enablers[enabler]
        self.project = self._enabler.tracker
        self.component = self._enabler.key
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' \
               + self.fixVersion + '*{color}+\n' +\
               '# Close your enabler/tool backlog issues finished during the sprint\n'\
               '# Update your help desk issues linked to the backlog\n'\
               '# Provide your retrospective in this specific issue created for ' \
               'this purpose by adding a comment\n' + \
               '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}' +\
               '\n' + reminders

    def summary(self):
        return 'FIWARE.WorkItem.{}.{}.Agile.Sprint-{}.{}'\
            .format(self.chapter, self._enabler.backlogKeyword, self._sprint, self.action)


class WorkGroupIssue(IssueDefinition):
    _type = 'workgroup'

    def __init__(self, workgroup, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.workgroup = workgroup
        _workgroup = workGroupBook[workgroup]
        self.project = _workgroup.coordination.tracker
        self.component = _workgroup.coordination.key
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' \
               + self.fixVersion + '*{color}+\n' +\
               '# Close your Working Group coordination backlog issues finished ' \
               'during the sprint\n'\
               '# Add any workitem not foreseen but arisen during the sprint \n'\
               "# Verify your groups' backlog are properly closed\n" + \
               "# Verify your groups' retrospective are provided in time\n" +\
               '# Provide your retrospective in this specific issue created for ' \
               'this purpose by adding a comment\n' +\
               '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') \
               + ' at 18:00 {color}\n' + reminders

    def summary(self):
        return 'FIWARE.WorkItem.{}.Coordination.Agile.Sprint-{}.{}'\
            .format(self.workgroup, self._sprint, self.action)


class WorkingGroupRetrospectiveIssue(IssueDefinition):
    _type = 'chapter'

    def __init__(self, workgroup, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.workgroup = workgroup
        _workgroup = workGroupBook[workgroup]
        self.project = _workgroup.coordination.tracker
        self.component = _workgroup.coordination.key
        self.reporter = 'backlogmanager'

    def description(self):
        return "# Drawn {color:red} Working Group Summary Retrospective{color} " \
               "from {color:blue} Groups' Retrospectives{color} \n" + \
                retrospective_pattern

    def summary(self):
        return 'FIWARE.WorkItem.{}.Coordination.Agile.Sprint-{}.{}'\
            .format(self.workgroup, self._sprint, self.action)


class GroupIssue(IssueDefinition):
    _type = 'group'

    def __init__(self, workgroup, group, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.group = group
        self.workgroup = workgroup
        self._workgroup = workGroupBook[workgroup]
        self._group = self._workgroup.groups[group]
        self.project = self._group.tracker
        self.component = self._group.key
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' \
               + self.fixVersion + '*{color}+\n' +\
               '# Close your backlog issues finished during the sprint\n'\
               '# Add any work item not foreseen but arisen during the sprint \n'\
               '# Provide your retrospective in this specific issue created for ' \
               'this purpose by adding a comment\n' +\
               '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') \
               + ' at 18:00 {color}\n' + reminders

    def summary(self):
        return 'FIWARE.WorkItem.{}.{}.Agile.Sprint-{}.{}'\
            .format(self.workgroup, self._group.backlogKeyword, self._sprint, self.action)


class LabIssue(IssueDefinition):
    _type = 'chapter'

    def __init__(self, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.lab = labsBookByName['Lab']
        self.project = self.lab.coordination.tracker
        self.component = self.lab.coordination.key
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' \
               + self.fixVersion + '*{color}+\n' + \
               '# Close your coordination backlog issues finished during the sprint\n'\
               '# Add any workitem not foreseen but arisen during the sprint \n'\
               "# Verify nodes' backlog are properly closed\n" + \
               "# Verify nodes' retrospective are provided in time\n" +\
               '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') \
               + ' at 18:00 {color}\n\n' + reminders

    def summary(self):
        return 'FIWARE.WorkItem.Lab.Coordination.Agile.Sprint-{}.{}'\
            .format(self._sprint, self.action)


class LabRetrospectiveIssue(IssueDefinition):
    _type = 'chapter'

    def __init__(self, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.lab = labsBookByName['Lab']
        self.project = self.lab.coordination.tracker
        self.component = self.lab.coordination.key
        self.reporter = 'backlogmanager'

    def description(self):
        return "# Drawn {color:red} Lab Summary Retrospective{color} " \
               "from {color:blue} Nodes's Retrospectives{color} \n" + \
                retrospective_pattern

    def summary(self):
        return 'FIWARE.WorkItem.Lab.Coordination.Agile.Sprint-{}.{}'\
            .format(self._sprint, self.action)


class NodeIssue(IssueDefinition):
    _type = 'node'

    def __init__(self, node, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.lab = labsBookByName['Lab']
        self.node = node
        self.project = self.node.tracker
        self.component = self.node.key
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' \
               + self.fixVersion + '*{color}+\n' +\
               '# Close your backlog issues finished during the sprint\n'\
               '# Add any work item not foreseen but arisen during the sprint \n'\
               '# Provide your retrospective in this specific issue created for ' \
               'this purpose by adding a comment\n' +\
               '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') \
               + ' at 18:00 {color}\n\n' + reminders

    def summary(self):
        return 'FIWARE.WorkItem.Lab.{}.Agile.Sprint-{}.{}'\
            .format(self.node.backlogKeyword, self._sprint, self.action)


class QualityAssuranceIssue(IssueDefinition):
    _type = 'tech'

    def __init__(self, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.project = 'TCOR'
        self.component = '11700'
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Close{color} {color:blue}*' \
               + self.fixVersion + '*{color}+\n' + \
               '# Close your backlog issues finished during the sprint\n'\
               '# Add any work item not foreseen but arisen during the sprint \n'\
               '# Provide your retrospective in this specific issue created for this ' \
               'purpose by adding a comment\n' +\
               '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') \
               + ' at 18:00 {color}\n' + reminders

    def summary(self):
        return 'FIWARE.WorkItem.QualityAssurance.Agile.Sprint-{}.{}'\
            .format(self._sprint, self.action)


def find_release_date(sprint):
        server = tool_settings.server['JIRA']
        options_jira = {'server': 'https://{}'.format(server.domain)}
        jira = JIRA(options_jira, basic_auth=(server.username, server.password))
        versions = jira.project_versions('COR')
        fix_version = 'Sprint {}'.format(sprint)

        release_date = datetime.strptime(
            [version.releaseDate for version in versions if version.name == fix_version][0],
            '%Y-%m-%d').date()

        return release_date


class SprintClosing:
    def __init__(self):

        action = 'Close'
        # If we want to generate the corresponding Closing tickets for the current sprint
        # we should take the sprint from the current_sprint value.
        # sprint = agileCalendar.next_sprint
        sprint = agileCalendar.current_sprint
        deadline = find_release_date(sprint)

        deadline = datetime.strptime('2017-09-29', '%Y-%m-%d').date()
        self.issues = []
        self.root = SourceIssue(action, sprint, deadline)
        self.issues.append(self.root)

        self.retrospective_root = ScrumMasterRetrospectiveIssue('Retrospective', sprint,
                                                                deadline + timedelta(days=10))
        self.issues.append(self.retrospective_root)

        for chapter_name in chaptersBook:
            if chapter_name == 'Marketplace':
                continue

            chapter = chaptersBook[chapter_name]

            if chapter_name == 'Ops':
                chapter_issue = ChapterIssue(chapter_name, action, sprint, deadline)
                chapter_issue.inwards.append(self.root)
                self.root.outwards.append(chapter_issue)
                self.issues.append(chapter_issue)

                chapter_retrospective = ChapterRetrospectiveIssue(chapter_name,
                                                                  'Retrospective',
                                                                  sprint,
                                                                  deadline + timedelta(days=5))

                self.retrospective_root.outwards.append(chapter_retrospective)
                self.issues.append(chapter_retrospective)

                temp_issue = chapter_issue
                temp_retrospective_issue = chapter_retrospective
            else:
                temp_issue = self.root
                temp_retrospective_issue = self.retrospective_root

            for enabler_name in chapter.enablers:
                enabler = chapter.enablers[enabler_name]

                if enabler.mode in ('Support', 'Deprecated'):
                    continue

                enabler_issue = EnablerIssue(chapter_name, enabler_name, action, sprint, deadline)
                enabler_issue.inwards.append(temp_issue)
                enabler_issue.inwards.append(temp_retrospective_issue)
                temp_issue.outwards.append(enabler_issue)
                temp_retrospective_issue.outwards.append(enabler_issue)
                self.issues.append(enabler_issue)

        lab_nodes_book = labsBookByName['Lab'].nodes
        lab_issue = LabIssue(action, sprint, deadline)
        lab_issue.inwards.append(self.root)
        self.root.outwards.append(lab_issue)
        self.issues.append(lab_issue)

        lab_retrospective = LabRetrospectiveIssue(
            'Retrospective', sprint, deadline + timedelta(days=5))

        self.retrospective_root.outwards.append(lab_retrospective)
        self.issues.append(lab_retrospective)

        for node_name in lab_nodes_book:
            node = lab_nodes_book[node_name]

            if node.mode in ('Negotiation', 'Closed'):
                continue

            node_issue = NodeIssue(node, action, sprint, deadline)
            node_issue.inwards.append(lab_issue)
            lab_issue.outwards.append(node_issue)
            self.issues.append(node_issue)

        # global
        # self.qa = QualityAssuranceIssue(action, sprint, deadline)
        # self.qa.inwards.append(self.root)
        # self.root.outwards.append(self.qa)
        # self.issues.append(self.qa)

        # for workgroupname in workGroupBook:
        #     workgroup = workGroupBook[workgroupname]
        #     workgroupIssue = WorkGroupIssue(workgroupname, action, sprint, deadline)
        #     workgroupIssue.inwards.append(self.root)
        #     self.root.outwards.append(workgroupIssue)
        #     self.issues.append(workgroupIssue)
        #
        #     workGroupRetrospective = WorkingGroupRetrospectiveIssue(workgroupname, 'Retrospective', sprint,
        #                                                             deadline + timedelta(days=5))
        #     self.retrospectiveroot.outwards.append(workGroupRetrospective)
        #     self.issues.append(workGroupRetrospective)
        #
        #     if workgroupname in ('Collaboration', 'Dissemination', 'Exploitation', 'PressOffice'): continue
        #     for groupname in workgroup.groups:
        #         group = workgroup.groups[groupname]
        #         if group.mode != 'Active': continue
        #         groupIssue = GroupIssue(workgroupname, groupname, action, sprint, deadline)
        #         groupIssue.inwards.append(workgroupIssue)
        #         groupIssue.inwards.append(workGroupRetrospective)
        #         workgroupIssue.outwards.append(groupIssue)
        #         workGroupRetrospective.outwards.append(groupIssue)
        #         self.issues.append(groupIssue)


if __name__ == "__main__":
    task = SprintClosing()
    tool = BacklogDeployer(task, description=False)
    options = {'0': tool.print,
               '1': tool.deploy,
               '2': tool.monitor,
               '3': tool.search,
               '4': tool.clean,
               'E': exit}

    while True:
        menu = '\nMenu:\n\t0: print\n\t1: deploy \n\t2: monitor \n\t3: ' \
               'search \n\t4: clean \n\tE: Exit'

        choice = input(menu + '\nEnter your choice[0-4,(E)xit] : ')
        print('Chosen option:', choice)

        if choice in ('0', '1', '2', '3', '4', 'E'):
            options[choice]()
        else:
            print('\n\n\nWrong option, please try again... ')
