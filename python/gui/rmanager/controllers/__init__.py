# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

from ..events import g_eventsManager

__all__ = ('g_controllers', )

class ControllersHolder():

	def __init__(self):
		self.actions = None
		self.database = None
		self.parser = None
		self.player = None
		self.uploader = None

	def init(self):

		from .actions import ActionsController
		from .database import DataBaseController
		from .parser import ParserController
		from .player import BattleReplayPlayer
		from .uploader import UploaderController

		self.player = BattleReplayPlayer()
		self.actions = ActionsController()
		self.database = DataBaseController()
		self.parser = ParserController()
		self.uploader = UploaderController()

		self.actions.init()
		self.database.init()
		self.parser.init()
		self.player.init()
		self.uploader.init()

		g_eventsManager.onAppFinish += self.fini

	def fini(self):

		self.actions.fini()
		self.database.fini()
		self.parser.fini()
		self.player.fini()
		self.uploader.fini()

		self.actions = None
		self.database = None
		self.parser = None
		self.uploader = None

g_controllers = ControllersHolder()
