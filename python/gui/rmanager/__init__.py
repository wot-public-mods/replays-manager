
__author__ = "Andruschyshyn Andrey and Kirill Malyshev"
__copyright__ = "Copyright 2019, Wargaming"
__credits__ = ["Andruschyshyn Andrey", "Kirill Malyshev"]
__license__ = "CC BY-NC-SA 4.0"
__version__ = "3.3.8"
__maintainer__ = "Andruschyshyn Andrey"
__email__ = "prn.a_andruschyshyn@wargaming.net"
__status__ = "Production"

from gui.rmanager.hooks import *
from gui.rmanager.lang import *
from gui.rmanager.events import *
from gui.rmanager.utils import *
from gui.rmanager.rmanager_constants import *
from gui.rmanager.controllers import g_controllers
from gui.rmanager.views import *

def init():
	g_controllers.init()

def fini():
	g_eventsManager.onAppFinish()
