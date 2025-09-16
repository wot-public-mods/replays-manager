# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import os
import BigWorld

from adisp import adisp_process
from gui.app_loader import spaces
from gameplay.listeners import PlayerEventsAdaptor
from gameplay.machine import BattleReplayMachine
from helpers import dependency
from skeletons.gameplay import IGameplayLogic
from gui import DialogsInterface

from .._constants import  REPLAY_FLAG_FILE, REPLAYS_PATH

class BattleReplayPlayer:

	gameplayLogic = dependency.descriptor(IGameplayLogic)

	def __init__(self):
		self.__replay_file = None

	def init(self):
		if os.path.exists(REPLAY_FLAG_FILE):
			with open(REPLAY_FLAG_FILE) as f:
				self.__replay_file = REPLAYS_PATH + f.read()
			os.remove(REPLAY_FLAG_FILE)
		if self.__replay_file:
			if os.path.isfile(self.__replay_file):
				self.start_replay_gameplay()
			else:
				self.__replay_file = None

	def fini(self):
		self.__replay_file = None

	def getReplayFileName(self):
		return self.__replay_file

	def start_replay_gameplay(self):

		# configure our BattleReplayMachine
		machine = BattleReplayMachine()
		adaptor = PlayerEventsAdaptor(machine)
		observers = self.gameplayLogic._GameplayLogic__machine._StateMachine__observers
		machine._StateMachine__observers._observers = observers._observers[:]

		# swap GameplayStateMachine to our BattleReplayMachine
		self.gameplayLogic._GameplayLogic__machine = machine
		self.gameplayLogic._GameplayLogic__adaptor = adaptor

		# swap ReplayFinished dialog handler
		@adisp_process
		def doAction(self):
			result = yield DialogsInterface.showI18nConfirmDialog('replayStopped')
			if result:
				BigWorld.restartGame()
		spaces.ReplayFinishDialogAction.doAction = doAction
