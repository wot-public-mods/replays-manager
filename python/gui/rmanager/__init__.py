
__author__ = "Andrii Andrushchyshyn"
__copyright__ = "Copyright 2023, poliroid"
__credits__ = ["Andrii Andrushchyshyn"]
__license__ = "LGPL-3.0-or-later"
__version__ = "3.7.6"
__maintainer__ = "Andrii Andrushchyshyn"
__email__ = "contact@poliroid.me"
__status__ = "Production"

from .hooks import *
from .events import g_eventsManager
from .controllers import g_controllers
from .views import *

__all__ = ('init', 'fini')

def init():
	g_controllers.init()

def fini():
	g_eventsManager.onAppFinish()
