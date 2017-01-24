__author__ = 'Manuel Escriche'

from kernel.DataFactory import DataFactory
from kernel.TComponentsBook import enablersBook, helpdeskCompBook
from kernel import settings


class Data:
    @staticmethod
    def getHelpDeskTechChannel():
        techChannel = helpdeskCompBook['Tech']
        return DataFactory(settings.storeHome).getComponentData(techChannel.key)
