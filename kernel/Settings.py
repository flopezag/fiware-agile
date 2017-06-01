import os
from xml.etree import ElementTree as Et
from datetime import datetime
from collections import namedtuple

__author__ = "Manuel Escriche < mev@tid.es>"


class Settings:
    def __init__(self):
        self._dashboard = dict()
        self._review = dict()
        self.home = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
        self.configHome = os.path.join(self.home, 'site_config')
        self.storeHome = os.path.join(self.home, 'store')
        self.backlogHome = os.path.join(self.home, 'BACKLOGS')
        xmlfile = os.path.join(self.configHome, 'settings.xml')
        # print(xmlfile)

        tree = Et.parse(xmlfile)
        root = tree.getroot()

        self._today = datetime.now().strftime("%Y%m%d")
        self._dashboard['deliverable'] = root.find('dashboard').find('deliverable').text
        self.domain = root.find('domain').text

        self._servers = dict()
        record = namedtuple('record', ('domain, username, password'))
        for _server in root.findall('server'):
            name = _server.get('name')
            domain = _server.find('domain').text
            username = _server.find('username').text
            password = _server.find('password').text
            self._servers[name] = record(domain, username, password)

        # print(len(self.__chapters))

    @property
    def server(self):
        return self._servers

    @property
    def chapters(self):
        return ('Apps', 'Cloud', 'Data', 'IoT', 'I2ND', 'Security', 'WebUI', 'Ops', 'Academy', 'Catalogue')

    @property
    def deliverable(self):
        return self._dashboard['deliverable']

if __name__ == "__main__":
    pass
