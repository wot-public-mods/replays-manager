
__author__ = "Andrii Andrushchyshyn and Kirill Malyshev"
__copyright__ = "Copyright 2022, poliroid"
__credits__ = ["Andrii Andrushchyshyn", "Kirill Malyshev"]
__license__ = "LGPL-3.0-or-later"
__version__ = "3.6.4"
__maintainer__ = "Andrii Andrushchyshyn"
__email__ = "contact@poliroid.me"
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
