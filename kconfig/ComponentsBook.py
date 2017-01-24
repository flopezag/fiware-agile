__author__ = "Manuel Escriche <mev@tid.es>"

import os, re, pickle
from datetime import date, datetime
from collections import OrderedDict, namedtuple
from operator import attrgetter
from xml.etree import ElementTree as ET
from kconfig import settings
from kernel.Connector import Connector


class ComponentLeaders(dict):
    def __init__(self):
        super().__init__()
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        self.filename = 'FIWARE.components.leaders' +'.'+ self.timestamp + '.pkl'
        codeHome = os.path.dirname(os.path.abspath(__file__))
        configHome = os.path.join(os.path.split(codeHome)[0], 'site_config')

        xmlfile = os.path.join(configHome, 'Enablers.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('enabler'):
            key = item.find('cmp_key').text
            try:
                self[key] = self.find_leader(key)
            except Exception:
                raise Exception

        xmlfile = os.path.join(configHome, 'Tools.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('tool'):
            key = item.find('cmp_key').text
            try:
                self[key] = self.find_leader(key)
            except Exception:
                raise Exception

        xmlfile = os.path.join(configHome, 'Coordination.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('coordinator'):
            key = item.find('cmp_key').text
            try:
                self[key] = self.find_leader(key)
            except Exception:
                raise Exception

        xmlfile = os.path.join(configHome, 'WorkGroups.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('group'):
            key = item.find('cmp_key').text
            try:
                self[key] = self.find_leader(key)
            except Exception:
                raise Exception

        self.save()
        self.clean()

    def find_leader(self, key):
        try:
            jiraConnector = Connector.getInstance()
            leader = jiraConnector.componentLeader(key)
        except Exception:
            leader = 'Unknown'
        return leader

    def save(self):
        #print(self)
        longFilename = os.path.join(settings.storeHome, self.filename)
        with open(longFilename, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def fromFile(cls):
        fileList = os.listdir(settings.storeHome)
        mfilter = re.compile(r'\bFIWARE\.components\.leaders\.(?P<day>\d{8})[-](?P<time>\d{4})[.]pkl\b')
        record = namedtuple('record', 'filename, day, time')
        filelist = [record(mfilter.match(f).group(0),
                           mfilter.match(f).group('day'),
                           mfilter.match(f).group('time')) for f in fileList if mfilter.match(f)]
        filelist.sort(key=attrgetter('day', 'time'), reverse=True)
        filename = filelist[0].filename
        #print('load-fromFile', filename)
        with open(os.path.join(settings.storeHome, filename), 'rb') as f:
            return pickle.load(f)

    def clean(self):
        fileList = os.listdir(settings.storeHome)
        mfilter = re.compile(r'\bFIWARE\.components\.leaders\.(?P<day>\d{8})[-](?P<time>\d{4})[.]pkl\b')
        record = namedtuple('record', 'filename, day, time')
        filelist = [record(mfilter.match(f).group(0),
                           mfilter.match(f).group('day'),
                           mfilter.match(f).group('time')) for f in fileList if mfilter.match(f)]
        filelist.sort(key=attrgetter('day', 'time'), reverse=True)
        toRemove = filelist[5:]
        if len(toRemove) > 0:
            for item in toRemove:
                os.remove(os.path.join(settings.storeHome, item.filename))

class Component:
    def __init__(self, comp, leader):
        tagsList = [child.tag for child in comp]
        self.key = comp.find('cmp_key').text
        self.tracker = comp.find('tracker_key').text
        self.name = comp.get('name')
        self._leader = leader

    def find_leader(self):
        try:
            jiraConnector = Connector.getInstance()
            data = jiraConnector.component(self.key)
            leader = data['realAssignee']['displayName']
        except Exception:
            leader = 'Unknown'
        return leader

    @property
    def leader(self):
        if self._leader == 'Unknown':
            self._leader = self.find_leader()
        return self._leader

    def __repr__(self):
        return '{0.key}, {0.tracker}, {0.name}'.format(self)

class Enabler(Component):
    def __init__(self, enabler, leader):
        super().__init__(enabler, leader)
        tagsList = [child.tag for child in enabler]
        self.chapter = enabler.get('chapter')
        self.owner = enabler.find('owner').text if 'owner' in tagsList else 'Unknown'
        self.type = enabler.find('type').text if 'type' in tagsList else 'Unknown'
        self.mode = enabler.find('mode').text if 'mode' in tagsList else 'Development'
        self.backlogKeyword = enabler.find('backlog_keyword').text if 'backlog_keyword' in tagsList else 'Unknown'
        self.packageKeyword = enabler.find('package_keyword').text if 'package_keyword' in tagsList else 'Unknown'
        self.dissemination = enabler.find('dissemination').text if 'dissemination' in tagsList else 'Open'
        self.GE = enabler.find('GE').text if 'GE' in tagsList else None
        self.GEi = enabler.find('GEi').text if 'GEi' in tagsList else None
        self.Name = '{} - {}'.format(self.GE, self.GEi) if self.GEi else self.GE

class Tool(Component):
    def __init__(self, tool, leader):
        super().__init__(tool, leader)
        tagsList = [child.tag for child in tool]
        self.chapter = tool.get('chapter')
        self.owner = tool.find('owner').text if 'owner' in tagsList else 'Unknown'
        self.mode = tool.find('mode').text if 'mode' in tagsList else 'Development'
        self.backlogKeyword = tool.find('backlog_keyword').text if 'backlog_keyword' in tagsList else 'Unknown'

class Coordinator(Component):
    def __init__(self, coordinator, leader):
        super().__init__(coordinator, leader)
        tagsList = [child.tag for child in coordinator]
        self.project = coordinator.get('tracker')
        self.owner = coordinator.find('owner').text if 'owner' in tagsList else 'Unknown'
        self.backlogKeyword = coordinator.find('backlog_keyword').text if 'backlog_keyword' in tagsList else 'Unknown'
        #print(self)

class Channel(Component):
    def __init__(self, channel, leader):
        super().__init__(channel, leader)
        tagsList = [child.tag for child in channel]
        self.inbox = channel.find('inbox').text if 'inbox' in tagsList else 'Unknown'

class AccountChannel(Component):
    def __init__(self, channel, leader):
        super().__init__(channel, leader)
        tagsList = [child.tag for child in channel]

class Group(Component):
    def __init__(self, group, leader):
        super().__init__(group, leader)
        tagsList = [child.tag for child in group]
        self.group = group.get('group')
        self.owner = group.find('owner').text if 'owner' in tagsList else 'Unknown'
        self.mode = group.find('mode').text if 'mode' in tagsList else 'Active'
        self.backlogKeyword = group.find('backlog_keyword').text if 'backlog_keyword' in tagsList else 'Unknown'

class LabComp(Component):
    def __init__(self, cmp, leader):
        super().__init__(cmp, leader)
        tagsList = [child.tag for child in cmp]
        self.owner = cmp.find('owner').text if 'owner' in tagsList else 'Unknown'
        self.backlogKeyword = cmp.find('backlog_keyword').text if 'backlog_keyword' in tagsList else 'Unknown'
        self.mode = cmp.find('mode').text if 'mode' in tagsList else 'Active'

class LabNode(Component):
    def __init__(self, cmp, leader):
        super().__init__(cmp, leader)
        tagsList = [child.tag for child in cmp]
        self.owner = cmp.find('owner').text if 'owner' in tagsList else 'Unknown'
        self.backlogKeyword = cmp.find('backlog_keyword').text if 'backlog_keyword' in tagsList else 'Unknown'
        self.mode = cmp.find('mode').text if 'mode' in tagsList else 'Active'

class ComponentsBook(OrderedDict):
    _singlenton = None
    def __new__(cls, *args, **kwargs):
        if not cls._singlenton:
            cls._singlenton = super(ComponentsBook, cls).__new__(cls, *args, **kwargs)
        return cls._singlenton

    def __init__(self):
        super().__init__()
        codeHome = os.path.dirname(os.path.abspath(__file__))
        self.configHome = os.path.join(os.path.split(codeHome)[0], 'site_config')
        try:
            self.leaders = ComponentLeaders.fromFile()
        except Exception:
            pass

        self.add_enablers()
        self.enablersByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == Enabler)
        self.enablersByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == Enabler)

        self.add_tools()
        self.toolsByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == Tool)
        self.toolsByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == Tool)

        self.add_groups()
        self.groupsByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == Group)
        self.groupsByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == Group)

        self.add_coordinators()
        self.coordinatorsByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == Coordinator)
        self.coordinatorsByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == Coordinator)

        self.add_helpDeskChannels()
        self.helpDeskByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == Channel)
        self.helpDeskByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == Channel)

        self.add_labAccountsChannels()
        self.labAccountsDeskByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == AccountChannel)
        self.labAccountsDeskByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == AccountChannel)

        self.add_lab()
        self.labCompByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == LabComp)
        self.labCompByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == LabComp)
        self.labNodesByKey = OrderedDict((cmp, self[cmp]) for cmp in self if type(self[cmp]) == LabNode)
        self.labNodesByName = OrderedDict((self[cmp].name, self[cmp]) for cmp in self if type(self[cmp]) == LabNode)

    def add_enablers(self):
        xmlfile = os.path.join(self.configHome, 'Enablers.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('enabler'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception:
                leader = 'Unknown'
            self[key] = Enabler(item, leader)

    def add_tools(self):
        xmlfile = os.path.join(self.configHome, 'Tools.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('tool'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception:
                leader = 'Unknown'
            self[key] = Tool(item, leader)
            #print(self[key])

    def add_coordinators(self):
        xmlfile = os.path.join(self.configHome, 'Coordination.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('coordinator'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception: leader = 'Unknown'
            self[key] = Coordinator(item, leader)

    def add_helpDeskChannels(self):
        xmlfile = os.path.join(self.configHome, 'HelpdeskChannels.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('channel'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception: leader = 'Unknown'
            self[key] = Channel(item, leader)

    def add_labAccountsChannels(self):
        xmlfile = os.path.join(self.configHome, 'AccountsChannels.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('channel'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception: leader = 'Unknown'
            self[key] = AccountChannel(item, leader)

    def add_groups(self):
        xmlfile = os.path.join(self.configHome, 'WorkGroups.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('group'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception: leader = 'Unknown'
            self[key] = Group(item, leader)

    def add_lab(self):
        xmlfile = os.path.join(self.configHome, 'LabNodes.xml')
        #print(xmlfile)
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        for item in root.findall('component'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception: leader = 'Unknown'
            self[key] = LabComp(item, leader)

        for item in root.findall('node'):
            key = item.find('cmp_key').text
            try:
                leader = self.leaders[key] if key in self.leaders else 'Unknown'
            except Exception: leader = 'Unknown'
            self[key] = LabNode(item, leader)


#tComponentsBook = ComponentsBook()
#enablersBook = tComponentsBook.enablersByName
#enablersBookByName = tComponentsBook.enablersByName
#enablersBookByKey = tComponentsBook.enablersByKey

#toolsBook = tComponentsBook.toolsByName
#toolsBookByName = tComponentsBook.toolsByName
#toolsBookByKey = tComponentsBook.toolsByKey

#coordinationBook = tComponentsBook.coordinatorsByKey
#coordinationBookByName = tComponentsBook.coordinatorsByName
#coordinationBookByKey = coordinationBook

#helpdeskCompBook = tComponentsBook.helpDeskByName
#helpdeskCompBookByName = tComponentsBook.helpDeskByName
#helpdeskCompBookByKey = tComponentsBook.helpDeskByKey

#accountsDeskBook = tComponentsBook.labAccountsDeskByName
#accountsDeskBookByName = tComponentsBook.labAccountsDeskByName
#accountsDeskBookByKey = tComponentsBook.labAccountsDeskByKey

#workingGroupsBook = tComponentsBook.groupsByName
#workingGroupsBookByName = tComponentsBook.groupsByName
#workingGroupsBookByKey = tComponentsBook.groupsByKey

#labCompBook = tComponentsBook.labCompByName
#labCompBookByName = tComponentsBook.labCompByName
#labCompBookByKey = tComponentsBook.labCompByKey

#labNodesBook = tComponentsBook.labNodesByName
#labNodesBookByName = tComponentsBook.labNodesByName
#labNodesBookByKey = tComponentsBook.labNodesByKey


if __name__ == "__main__":
    pass