from .Settings import Settings

__author__ = 'Manuel Escriche'

# Get Settings values
settings = Settings()

from .Calendar import AgileCalendar
from .ComponentsBook import ComponentsBook

# Get information related to Components
tComponentsBook = ComponentsBook()

enablersBookByName = tComponentsBook.enablersByName
toolsBookByName = tComponentsBook.toolsByName
workingGroupsBookByName = tComponentsBook.groupsByName
coordinationBook = tComponentsBook.coordinatorsByKey
helpdeskCompBookByName = tComponentsBook.helpDeskByName
accountsDeskBookByName = tComponentsBook.labAccountsDeskByName
labCompBook = tComponentsBook.labCompByName
labNodesBook = tComponentsBook.labNodesByName

from .TTrackerBook import TrackerBook, ChapterBook, WorkGroupBook
from .TTrackerBook import LabBook

# Get information about Agile Calendar
agileCalendar = AgileCalendar()
calendar = agileCalendar.calendar

# Get information about Chapter, Workgroup and Lab

chaptersBook = ChapterBook()

workGroupBook = WorkGroupBook()

labsBookByName = LabBook().labsByName
