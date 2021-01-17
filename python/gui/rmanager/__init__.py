
__author__ = "Andruschyshyn Andrey and Kirill Malyshev"
__copyright__ = "Copyright 2021, poliroid"
__credits__ = ["Andruschyshyn Andrey", "Kirill Malyshev"]
__license__ = "CC BY-NC-SA 4.0"
__version__ = "3.5.6"
__maintainer__ = "Andruschyshyn Andrey"
__email__ = "p0lir0id@yandex.ru"
__status__ = "Production"

from gui.rmanager.hooks import *
from gui.rmanager.events import g_eventsManager
from gui.rmanager.controllers import g_controllers
from gui.rmanager.views import *

__all__ = ('init', 'fini')

def init():
	g_controllers.init()

def fini():
	g_eventsManager.onAppFinish()
