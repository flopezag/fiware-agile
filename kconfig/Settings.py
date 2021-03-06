import os
from xml.etree import ElementTree

__author__ = "Manuel Escriche <mev@tid.es>"


class Server:
    def __init__(self, server):
        tags_list = [child.tag for child in server]
        self.name = server.get('name')
        self.domain = server.find('domain').text
        self.username = server.find('username').text if 'username' in tags_list else None
        self.password = server.find('password').text if 'password' in tags_list else None


class Settings:
    def __init__(self):
        self.codeHome = os.path.dirname(os.path.abspath(__file__))
        self.configHome = os.path.join(os.path.split(self.codeHome)[0], 'site_config')
        # base = os.path.split(self.codeHome)[0]
        # self.storeHome = os.path.join(os.path.split(base)[0], 'store')
        # print(self.storeHome)
        xmlfile = os.path.join(self.configHome, 'Settings.xml')
        # print(xmlfile)
        tree = ElementTree.parse(xmlfile)
        root = tree.getroot()
        self.server = dict()
        for _server in root.findall('server'):
            name = _server.get('name')
            self.server[name] = Server(_server)


if __name__ == "__main__":
    pass
