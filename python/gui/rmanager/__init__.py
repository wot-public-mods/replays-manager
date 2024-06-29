# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

__version__ = "1.4.7"

from .hooks import *
from .events import g_eventsManager
from .controllers import g_controllers
from .views import *

__all__ = ('init', 'fini')

def init():
	g_controllers.init()

def fini():
	g_eventsManager.onAppFinish()
