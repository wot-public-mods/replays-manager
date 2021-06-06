
__author__ = "Andruschyshyn Andrey and Kirill Malyshev"
__copyright__ = "Copyright 2021, poliroid"
__credits__ = ["Andruschyshyn Andrey", "Kirill Malyshev"]
__license__ = "LGPL-3.0-or-later"
__version__ = "3.5.9"
__maintainer__ = "Andruschyshyn Andrey"
__email__ = "poliroid@pm.me"
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
