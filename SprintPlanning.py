import re
from datetime import datetime
from kconfig import chaptersBook, workGroupBook, labsBookByName
from kconfig import agileCalendar
from kernel.BacklogDeployer import BacklogDeployer

__author__ = "Manuel Escriche <mev@tid.es>"


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
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' + \
                '# Create hierarchically backlog issues for all tech chapters leaders and GE owners\n' + \
                '# Schedule and attend sprint planning meetings for all tech chapters\n' + \
                '# Take backlog snapshot for ' + self.fixVersion + '\n' + \
                '# Share sprint planning outcome with project partners \n' + \
                '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00h {color}\n'

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
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' + \
                '# Verify sprint planning issues are available for all GE owners\n' +\
                '# Organise and hold sprint planning meeting for the chapter before deadline\n' +\
                "# Update your chapter coordination backlog properly\n" +\
                "# Verify all GEs are properly planned for the sprint\n" +\
                '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n'

    def summary(self):
        return 'FIWARE.WorkItem.{}.Coordination.Agile.Sprint-{}.{}'.format(self.chapter, self._sprint, self.action)


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
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' +\
                    '# Check your sprint planning issue is available and update its status as you progress\n' +\
                    '# Create and/or schedule your backlog issues for the sprint\n' +\
                    'Topics:\n' +\
                    '#* My HelpDesk Issues - My Bugs\n' +\
                    '#* My Roadmap - My Developments\n' +\
                    '#* My Deployments (FIWARE LAB)\n' +\
                    '#* My Publishing (Catalogue)\n' +\
                    '#* My Training (Academy)\n' +\
                    '#* My Contribution to Deliverables\n' +\
                    '#* Others?\n' +\
                    '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n'

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
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' + \
                '# If needed, organise and hold sprint planning meeting for the workgroup before deadline\n' +\
                "# Update your work group coordination backlog properly\n" +\
                "# Verify all components are properly planned for the sprint\n" +\
                '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n'

    def summary(self):
        return 'FIWARE.WorkItem.{}.Coordination.Agile.Sprint-{}.{}'.format(self.workgroup, self._sprint, self.action)


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
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' +\
                    '# Create and/or schedule your backlog issues for the sprint\n' +\
                    'Topics:\n' +\
                    '#* My Contribution to Deliverables\n' +\
                    '#* Others?\n' +\
                    '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n'

    def summary(self):
        return 'FIWARE.WorkItem.{}.{}.Agile.Sprint-{}.{}'\
            .format(self.workgroup, self._group.backlogKeyword, self._sprint, self.action)


class QualityAssuranceIssue(IssueDefinition):
    _type = 'tech'

    def __init__(self, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.project = 'TCOR'
        self.component = '11700'
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' + \
                '# Create and/or schedule backlog issues for the sprint\n' + \
                'Topics:\n' +\
                '#* Test Cases and test descriptions\n' +\
                '#* My Contribution to Deliverables\n' +\
                '#* Test reports\n' +\
                '#* Others?\n' +\
                '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00h {color}\n'

    def summary(self):
        return 'FIWARE.WorkItem.QualityAssurance.Agile.Sprint-{}.{}'.format(self._sprint, self.action)


class LabIssue(IssueDefinition):
    _type = 'chapter'

    def __init__(self, action, sprint, deadline):
        super().__init__(action, sprint, deadline)
        self.lab = labsBookByName['Lab']
        self.project = self.lab.coordination.tracker
        self.component = self.lab.coordination.key
        self.reporter = 'backlogmanager'

    def description(self):
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' + \
                '# Verify sprint planning issues are available for all Nodes\n' +\
                '# Organise and hold sprint planning meeting for the chapter before deadline\n' +\
                "# Update your chapter coordination backlog properly\n" +\
                "# Verify all Nodes are properly planned for the sprint\n" +\
                '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n'

    def summary(self):
        return 'FIWARE.WorkItem.Lab.Coordination.Agile.Sprint-{}.{}'.format(self._sprint, self.action)


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
        return '+Activities requested to {color:red}Plan{color} {color:blue}*' + self.fixVersion + '*{color}+\n' +\
                    '# Check your sprint planning issue is available and update its status as you progress\n' +\
                    '# Create and/or schedule foreseen backlog issues for the sprint\n' +\
                    '\n{color: red}Deadline = ' + self.deadline.strftime('%d-%m-%Y') + ' at 18:00 {color}\n'

    def summary(self):
        return 'FIWARE.WorkItem.Lab.{}.Agile.Sprint-{}.{}'.format(self.node.backlogKeyword, self._sprint, self.action)


class SprintPlanning:
    def __init__(self):
        action = 'Planning'
        # sprint = agileCalendar.next_sprint
        sprint = agileCalendar.current_sprint
        deadline = datetime.strptime('2016-12-09', '%Y-%m-%d').date()
        self.issues = []
        self.root = SourceIssue(action, sprint, deadline)
        self.issues.append(self.root)

        for chaptername in chaptersBook:
            if chaptername in ('Marketplace', 'InGEIs', 'Catalogue', 'Academy'):
                continue

            chapter = chaptersBook[chaptername]
            chapter_issue = ChapterIssue(chaptername, action, sprint, deadline)
            chapter_issue.inwards.append(self.root)
            self.root.outwards.append(chapter_issue)
            self.issues.append(chapter_issue)
            for enablername in chapter.enablers:
                enabler = chapter.enablers[enablername]

                if enabler.mode in ('Support', 'Deprecated'):
                    continue

                enabler_issue = EnablerIssue(chaptername, enablername, action, sprint, deadline)
                enabler_issue.inwards.append(chapter_issue)
                chapter_issue.outwards.append(enabler_issue)
                self.issues.append(enabler_issue)

        # for workgroupname in workGroupBook:
        #    workgroup = workGroupBook[workgroupname]
        #    workgroupIssue = WorkGroupIssue(workgroupname, action, sprint, deadline)
        #    workgroupIssue.inwards.append(self.root)
        #    self.root.outwards.append(workgroupIssue)
        #    self.issues.append(workgroupIssue)
        #    if workgroupname in ('Collaboration', 'Dissemination', 'Exploitation', 'PressOffice'): continue
        #    for groupname in workgroup.groups:
        #        group = workgroup.groups[groupname]
        #        if group.mode != 'Active': continue
        #        groupIssue = GroupIssue(workgroupname, groupname, action, sprint, deadline)
        #        groupIssue.inwards.append(workgroupIssue)
        #        workgroupIssue.outwards.append(groupIssue)
        #        self.issues.append(groupIssue)

        lab_nodes_book = labsBookByName['Lab'].nodes
        lab_issue = LabIssue(action, sprint, deadline)
        lab_issue.inwards.append(self.root)
        self.root.outwards.append(lab_issue)
        self.issues.append(lab_issue)

        for nodename in lab_nodes_book:
            node = lab_nodes_book[nodename]

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

if __name__ == "__main__":
    task = SprintPlanning()
    tool = BacklogDeployer(task, description=False)
    options = {'0': tool.print,
               '1': tool.deploy,
               '2': tool.monitor,
               '3': tool.search,
               '4': tool.clean,
               'E': exit}

    while True:
        menu = '\nMenu:\n\t0: print\n\t1: deploy \n\t2: monitor \n\t3: search \n\t4: clean \n\tE: Exit'
        choice = input(menu + '\nEnter your choice[0-4,(E)xit] : ')
        print('Chosen option:', choice)
        options[choice]()
