import os
from collections import OrderedDict
from xml.etree import ElementTree

from kconfig import enablersBookByName, toolsBookByName, workingGroupsBookByName, \
    coordinationBook, helpdeskCompBookByName, accountsDeskBookByName, labCompBook, labNodesBook

__author__ = "Manuel Escriche <mev@tid.es>"


class Tracker:
    def __init__(self, tracker):
        tags_list = [child.tag for child in tracker]
        self.name = tracker.get('name')
        self.type = tracker.get('type')
        self.keystone = tracker.find('keystone').text
        self.leader = tracker.find('leader').text if 'leader' in tags_list else 'Unknown'
        self.inbox = tracker.find('inbox').text if 'inbox' in tags_list else 'Unknown'

    @property
    def tracker(self):
        return self.keystone

    @property
    def key(self):
        return self.keystone

    def __repr__(self):
        return '{0.name}, {0.keystone}'.format(self)


class Chapter(Tracker):
    def __init__(self, chapter):
        super().__init__(chapter)
        tags_list = [child.tag for child in chapter]

        self.architect = chapter.find('architect').text if 'architect' in tags_list else None
        self.Name = chapter.find('name').text if 'name' in tags_list else None

        self.enablers = OrderedDict((name, enablersBookByName[name])
                                    for name in enablersBookByName if enablersBookByName[name].tracker == self.keystone)

        self.tools = OrderedDict((name, toolsBookByName[name])
                                 for name in toolsBookByName if toolsBookByName[name].tracker == self.keystone)

        coordination = [coordinationBook[key]
                        for key in coordinationBook if coordinationBook[key].tracker == self.keystone]

        self.coordination = coordination[0] if len(coordination) else None
        # print(coordination, self.coordination)


class HelpDesk(Tracker):
    def __init__(self, tracker):
        super().__init__(tracker)
        # tagsList = [child.tag for child in tracker]
        self.channels = OrderedDict((name, helpdeskCompBookByName[name])
                                    for name in helpdeskCompBookByName
                                    if helpdeskCompBookByName[name].tracker == self.keystone)


class AccountsDesk(Tracker):
    def __init__(self, tracker):
        super().__init__(tracker)
        # tagsList = [child.tag for child in tracker]

        self.channels = OrderedDict((name, accountsDeskBookByName[name])
                                    for name in accountsDeskBookByName
                                    if accountsDeskBookByName[name].tracker == self.keystone)


class WorkGroup(Tracker):
    def __init__(self, tracker):
        super().__init__(tracker)
        # tagsList = [child.tag for child in tracker]
        self.groups = OrderedDict((name, workingGroupsBookByName[name])
                                  for name in workingGroupsBookByName
                                  if workingGroupsBookByName[name].tracker == self.keystone)

        coordination = [coordinationBook[key]
                        for key in coordinationBook if coordinationBook[key].tracker == self.keystone]

        self.coordination = coordination[0] if len(coordination) else None


class Lab(Tracker):
    def __init__(self, tracker):
        super().__init__(tracker)
        # tagsList = [child.tag for child in tracker]

        self.comps = OrderedDict((name, labCompBook[name])
                                 for name in labCompBook if labCompBook[name].tracker == self.keystone)

        self.nodes = OrderedDict((name, labNodesBook[name])
                                 for name in labNodesBook if labNodesBook[name].tracker == self.keystone)

        coordination = [coordinationBook[key]
                        for key in coordinationBook if coordinationBook[key].tracker == self.keystone]

        self.coordination = coordination[0] if len(coordination) else None


class Management(Tracker):
    def __init__(self, tracker):
        super().__init__(tracker)
        # tagsList = [child.tag for child in tracker]


class TrackerBook:
    _typeDict = {'CHAPTER': Chapter, 'MNG': Management, 'WG': WorkGroup,
                 'HDESK': HelpDesk, 'ADESK': AccountsDesk, 'LAB': Lab}
    _singlenton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singlenton:
            cls._singlenton = super(TrackerBook, cls).__new__(cls, *args, **kwargs)
        return cls._singlenton

    def __init__(self):
        self.codeHome = os.path.dirname(os.path.abspath(__file__))
        self.configHome = os.path.join(os.path.split(self.codeHome)[0], 'site_config')
        xmlfile = os.path.join(self.configHome, 'Trackers.xml')
        # print(xmlfile)
        tree = ElementTree.parse(xmlfile)
        root = tree.getroot()
        self.trackersByKey = OrderedDict()
        for _tracker in root.findall('tracker'):
            keystone = _tracker.find('keystone').text
            tracker_type = _tracker.get('type')
            self.trackersByKey[keystone] = TrackerBook._typeDict[tracker_type](_tracker)

        self.trackersByName = OrderedDict((self.trackersByKey[item].name, self.trackersByKey[item])
                                          for item in self.trackersByKey)

    def __getitem__(self, item):
        if item in self.trackersByKey:
            return self.trackersByKey[item]

        if item in self.trackersByName:
            return self.trackersByName[item]

        raise KeyError

    def __iter__(self):
        return self.trackersByName.__iter__()


class ChapterBook:
    _singlenton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singlenton:
            cls._singlenton = super(ChapterBook, cls).__new__(cls, *args, **kwargs)
        return cls._singlenton

    def __init__(self):
        trackers_book = TrackerBook()
        self.chaptersByKey = OrderedDict((trackers_book[item].keystone, trackers_book[item])
                                         for item in trackers_book if type(trackers_book[item]) == Chapter)

        self.chaptersByName = OrderedDict((trackers_book[item].name, trackers_book[item])
                                          for item in trackers_book if type(trackers_book[item]) == Chapter)

    def __getitem__(self, item):
        if item in self.chaptersByKey:
            return self.chaptersByKey[item]

        if item in self.chaptersByName:
            return self.chaptersByName[item]

        raise KeyError

    def __iter__(self):
        return self.chaptersByName.__iter__()

    @property
    def chapters(self):
        return list(self.chaptersByName.keys())

    def __len__(self):
        return len(self.chaptersByKey)


class WorkGroupBook:
    _singlenton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singlenton:
            cls._singlenton = super(WorkGroupBook, cls).__new__(cls, *args, **kwargs)
        return cls._singlenton

    def __init__(self):
        trackers_book = TrackerBook()
        self.workingGroupByKey = OrderedDict((trackers_book[item].keystone, trackers_book[item])
                                             for item in trackers_book if type(trackers_book[item]) == WorkGroup)

        self.workingGroupByName = OrderedDict((trackers_book[item].name, trackers_book[item])
                                              for item in trackers_book if type(trackers_book[item]) == WorkGroup)

    def __getitem__(self, item):
        if item in self.workingGroupByKey:
            return self.workingGroupByKey[item]

        if item in self.workingGroupByName:
            return self.workingGroupByName[item]

        raise KeyError

    def __iter__(self):
        return self.workingGroupByName.__iter__()

    @property
    def workgroups(self):
        return list(self.workingGroupByName.keys())

    def __len__(self):
        return len(self.workingGroupByKey)


class HelpDeskBook:
    _singlenton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singlenton:
            cls._singlenton = super(HelpDeskBook, cls).__new__(cls, *args, **kwargs)
        return cls._singlenton

    def __init__(self):
        trackers_book = TrackerBook()
        self.deskByKey = OrderedDict((trackers_book[item].keystone, trackers_book[item])
                                     for item in trackers_book if type(trackers_book[item]) == HelpDesk)

        self.deskByName = OrderedDict((trackers_book[item].name, trackers_book[item])
                                      for item in trackers_book if type(trackers_book[item]) == HelpDesk)

    def __getitem__(self, item):
        if item in self.deskByKey:
            return self.deskByKey[item]

        if item in self.deskByName:
            return self.deskByName[item]

        raise KeyError

    def __iter__(self):
        return self.deskByName.__iter__()

    @property
    def desks(self):
        return list(self.deskByName.keys())

    def __len__(self):
        return len(self.deskByKey)


class AccountsDeskBook:
    _singlenton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singlenton:
            cls._singlenton = super(AccountsDeskBook, cls).__new__(cls, *args, **kwargs)
        return cls._singlenton

    def __init__(self):
        trackers_book = TrackerBook()
        self.deskByKey = OrderedDict((trackers_book[item].keystone, trackers_book[item])
                                     for item in trackers_book if type(trackers_book[item]) == AccountsDesk)

        self.deskByName = OrderedDict((trackers_book[item].name, trackers_book[item])
                                      for item in trackers_book if type(trackers_book[item]) == AccountsDesk)

    def __getitem__(self, item):
        if item in self.deskByKey:
            return self.deskByKey[item]

        if item in self.deskByName:
            return self.deskByName[item]

        raise KeyError

    def __iter__(self):
        return self.deskByName.__iter__()

    @property
    def desks(self):
        return list(self.deskByName.keys())

    def __len__(self):
        return len(self.deskByKey)


class LabBook:
    _singlenton = None

    def __new__(cls, *args, **kwargs):
        if not cls._singlenton:
            cls._singlenton = super(LabBook, cls).__new__(cls, *args, **kwargs)
        return cls._singlenton

    def __init__(self):
        trackers_book = TrackerBook()
        self.labsByKey = OrderedDict((trackers_book[item].keystone, trackers_book[item])
                                     for item in trackers_book if type(trackers_book[item]) == Lab)

        self.labsByName = OrderedDict((trackers_book[item].name, trackers_book[item])
                                      for item in trackers_book if type(trackers_book[item]) == Lab)

    def __getitem__(self, item):
        if item in self.labsByKey:
            return self.labsByKey[item]

        if item in self.labsByName:
            return self.labsByName[item]

        raise KeyError

    def __iter__(self):
        return self.labsByName.__iter__()

    @property
    def labs(self):
        return list(self.labsByName.keys())

    def __len__(self):
        return len(self.labsByKey)


# trackersBook = TrackerBook()
# trackersBookByKey = trackersBook.trackersByKey
# trackersBookByName = trackersBook.trackersByName

# chaptersBook = ChapterBook()
# chaptersBookByName = chaptersBook.chaptersByName
# chaptersBookByKey = chaptersBook.chaptersByKey

# workGroupBook = WorkGroupBook()
# workGroupByName = workGroupBook.workingGroupByName
# workGroupByKey = workGroupBook.workingGroupByKey

# helpdeskBook = HelpDeskBook()
# helpdeskBookByName = helpdeskBook.deskByName
# helpdeskBookByKey = helpdeskBook.deskByKey

# accountsdeskBook = AccountsDeskBook()
# accountsdeskBookByName = accountsdeskBook.deskByName
# accountsdeskBookByKey = accountsdeskBook.deskByKey

# labsBook = LabBook()
# labsBookByName = labsBook.labsByName
# labsBookByKey = labsBook.labsByKey

if __name__ == "__main__":
    pass
