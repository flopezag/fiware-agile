import os
from collections import OrderedDict, namedtuple
from xml.etree import ElementTree
from datetime import date
from dateutil.relativedelta import relativedelta
from itertools import groupby

__author__ = "Manuel Escriche <mev@tid.es>"

CalendarEntry = namedtuple('CalendarEntry', 'id, month, year')


class Calendar(OrderedDict):
    month_names = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun',
                   '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}

    def __init__(self):
        super().__init__()
        self.codeHome = os.path.dirname(os.path.abspath(__file__))
        self.configHome = os.path.join(os.path.split(self.codeHome)[0], 'site_config')
        xmlfile = os.path.join(self.configHome, 'Calendar.xml')
        # print(xmlfile)
        tree = ElementTree.parse(xmlfile)
        root = tree.getroot()

        for _entry in root.findall('entry'):
            _id = _entry.get('id')
            month = _entry.get('month')
            year = _entry.get('year')
            self[_id] = CalendarEntry(_id, month, year)

        self.start = date(int(self['M01'].year), int(self['M01'].month), 1)
        self.months = list(self.keys())
        self.monthBook = {month: '{1}-{2}'.format(*self[month]) for month in self}

    def get_month(self, month):
        start = self.start + relativedelta(months=month - 1)
        end = start + relativedelta(day=31)
        return start, end

    @property
    def past_months(self):
        month = self.current_month[0]
        return [item for item in self if int(item[1:]) <= month]

    @property
    def current_month(self):
        d1, d2 = date.today(), self.start
        month = (12 * d1.year + d1.month) - (12 * d2.year + d2.month) + 1
        month_id = self.months[month - 1]
        return month, month_id

    @property
    def next_month(self):
        month = self.current_month[0] + 1
        month_id = self.months[month - 1]
        return month, month_id

    @property
    def prev_month(self):
        month = self.current_month[0] - 1
        month_id = self.months[month - 1]
        return month, month_id

    @property
    def timeline(self):
        return list(self.keys())


#    def getFutureMonths(self):
#        current_month = self.getCurrentMonth()
#        return [item for item in self if int(item[1:]) > current_month]

# calendar = Calendar()

AgileCalendarEntry = namedtuple('AgileCalendarEntry', 'month, sprint, release')


class AgileCalendar(OrderedDict):
    def __init__(self):
        super().__init__()
        self.codeHome = os.path.dirname(os.path.abspath(__file__))
        self.configHome = os.path.join(os.path.split(self.codeHome)[0], 'site_config')
        self.calendar = Calendar()
        xmlfile = os.path.join(self.configHome, 'AgileCalendar.xml')
        tree = ElementTree.parse(xmlfile)
        root = tree.getroot()

        for _sprint in root.findall('sprint'):
            sprint = _sprint.get('id')
            release = sprint[:3]
            month = _sprint.get('month')
            self[month] = AgileCalendarEntry(month, sprint, release)

        self.sprints = [self[month].sprint for month in self]
        self.releases = [self[month].release for month in self]

        self.Sprints = ['Sprint {}'.format(sprint) for sprint in self.sprints]
        self.Releases = ['Release {}'.format(release) for release in self.releases]

    @property
    def current_timeslots(self):
        month = self.calendar.current_month[1]
        sprint = [self[month].sprint]
        release = [self[month].release]
        return release + sprint

    @property
    def past_timeslots(self):
        month = self.calendar.current_month[1]
        i = self.calendar.months.index(month) - 1
        sprints = [sprint for sprint in self.sprints[:i] if sprint != self.sprints[i]]
        _releases = [release for release in self.releases[:i] if release != self.releases[i]]
        releases = [key for key, _ in groupby(_releases)]
        return releases + sprints

    @property
    def future_timeslots(self):
        month = self.calendar.current_month[1]
        i = self.calendar.months.index(month) - 1
        sprints = [sprint for sprint in self.sprints[i:] if sprint != self.sprints[i]]
        _releases = [release for release in self.releases[i:] if release != self.releases[i]]
        releases = [key for key, _ in groupby(_releases)]
        return releases + sprints

    @property
    def next_sprint_from_current_month(self):
        _month = self.calendar.current_month[1]
        month = self.calendar.months.index(_month) + 1
        return 'Sprint {}'.format(self[month].sprint)

    @property
    def next_sprint(self):
        month = self.calendar.next_month[1]
        return self[month].sprint

    @property
    def current_sprint(self):
        month = self.calendar.current_month[1]
        return self[month].sprint

    @property
    def prev_sprint_from_current_month(self):
        _month = self.calendar.current_month[1] - 1
        month = self.calendar.months.index(_month) - 1
        return 'Sprint {}'.format(self[month].sprint)

    @property
    def prev_sprint(self):
        month = self.calendar.prev_month[1]
        return self[month].sprint

    def get_prev_sprint(self, sprint):
        for entry in self:
            if sprint == self[entry].sprint:
                prev_month = 'M{}'.format(int(self[entry].month[1:]) - 1)
                return self[prev_month].sprint
        else:
            raise ValueError

    def is_valid_sprint(self, timeSlot):
        return True if timeSlot in self.Sprints else False

    def is_valid_release(self, timeSlot):
        return True if timeSlot in self.Releases else False

    @property
    def project_time(self):
        month_id = self.calendar.current_month[1]
        entry = self.calendar[month_id]
        month = Calendar.month_names[entry.month]
        return '{} - {} {} - Sprint {}'.format(month_id, month, entry.year, self.current_timeslots[1])


if __name__ == "__main__":
    pass
