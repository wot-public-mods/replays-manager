# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

import BigWorld
import os

from constants import PremiumConfigs
from gui import DialogsInterface
from gui.shared.personality import ServicesLocator
from gui.Scaleform.daapi.view.dialogs import (SimpleDialogMeta, ConfirmDialogButtons,
												InfoDialogButtons, DIALOG_BUTTON_ID)
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.framework.managers import context_menu
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache

from ..controllers import g_controllers
from ..events import g_eventsManager
from ..hooks import showUploader
from ..lang import l10n
from ..utils import getLogger
from .._constants import REPLAYS_PATH, REPLAY_CM_HANDLER_TYPE, REPLAY_ACTIONS, REPLAY_FLAG_FILE

logger = getLogger(__name__)

class CustomDialogButtons(ConfirmDialogButtons):
	def getLabels(self):
		return [{'id': DIALOG_BUTTON_ID.SUBMIT, 'label': self._submit, 'focused': False},
				{'id': DIALOG_BUTTON_ID.CLOSE, 'label': self._close, 'focused': True}]

class ActionsController(object):

	rankedController = dependency.descriptor(IRankedBattlesController)
	epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)
	battleResults = dependency.descriptor(IBattleResultsService)
	itemsCache = dependency.descriptor(IItemsCache)

	def __init__(self):
		self.skip_statistics = False

	def init(self):
		context_menu.registerHandlers((REPLAY_CM_HANDLER_TYPE, ReplayContextMenuHandler))

	def fini(self):
		self.skip_statistics = False

	def handleAction(self, actionType, replayName):
		logger.debug('handleAction => actionType: %s, replayName: %s', actionType, replayName)
		if actionType == REPLAY_ACTIONS.SHOW_RESULTS:
			self.__showBattleResults(replayName)
		if actionType == REPLAY_ACTIONS.PLAY:
			self.__playBattleReplay(replayName)
		if actionType == REPLAY_ACTIONS.UPLOAD:
			self.__uploadBattleReplay(replayName)
		if actionType == REPLAY_ACTIONS.FAVORITE_ADD:
			self.__setReplayFavorite(replayName, True)
		if actionType == REPLAY_ACTIONS.FAVORITE_REMOVE:
			self.__setReplayFavorite(replayName, False)
		if actionType == REPLAY_ACTIONS.REMOVE:
			self.__removeBattleReplay(replayName)

	def __showBattleResults(self, replayName):
		try:

			# fix 1.5
			piggyBankCfg = {'multiplier': 0.1}
			settings = ServicesLocator.lobbyContext.getServerSettings().getSettings()
			settings[PremiumConfigs.PIGGYBANK] = settings.get(PremiumConfigs.PIGGYBANK, piggyBankCfg)

			replayData = g_controllers.database.getReplayResultData(replayName)
			if not replayData:
				return

			arenaUniqueID = replayData.get('arenaUniqueID', 0)

			logger.debug("__showBattleResults => replayData: %s", replayData)

			if not self.battleResults.areResultsPosted(arenaUniqueID):
				rankedControllerABRWS = self.rankedController._RankedBattlesController__arenaBattleResultsWasShown
				if arenaUniqueID not in rankedControllerABRWS:
					rankedControllerABRWS.add(arenaUniqueID)

				if not hasattr(self.epicMetaGameCtrl, '_arenaBattleResultsWasShown'):
					self.epicMetaGameCtrl._arenaBattleResultsWasShown = set()

				epicMetaGameCtrlABRWS = self.epicMetaGameCtrl._arenaBattleResultsWasShown
				if arenaUniqueID not in epicMetaGameCtrlABRWS:
					epicMetaGameCtrlABRWS.add(arenaUniqueID)
				
				self.skip_statistics = True
				if self.itemsCache.isSynced():
					self.battleResults.postResult(replayData, False)
				else:
					original_isSynced = self.itemsCache.items.isSynced
					self.itemsCache.items.isSynced = lambda *a, **kw: True
					self.battleResults.postResult(replayData, False)
					self.itemsCache.items.isSynced = original_isSynced
				self.skip_statistics = False

			# handler for windows diplay
			#  ClassicResults
			#  BattleRoyaleResults
			#  HalloweenResults
			handler = self.battleResults._BattleResultsService__notifyBattleResultsPosted
			handler(arenaUniqueID, True)

			logger.debug('__showBattleResults => replayName: %s', replayName)
		except:
			logger.exception('__showBattleResults')

	def __playBattleReplay(self, replayName):
		try:
			def getPlayConfirmDialogMeta():
				buttons = CustomDialogButtons(l10n('ui.popup.button.yes'), l10n('ui.popup.button.no'))
				return SimpleDialogMeta(message=l10n('ui.popup.play.message'), title=l10n('ui.popup.play.title'), buttons=buttons)
			def dialogCallback(result):
				if result:
					with open(REPLAY_FLAG_FILE, 'w') as f:
						f.write(replayName)
					BigWorld.savePreferences()
					BigWorld.restartGame()
			DialogsInterface.showDialog(getPlayConfirmDialogMeta(), dialogCallback)
		except:
			logger.exception('__playBattleReplay')

	@staticmethod
	def __uploadBattleReplay(replayName):
		try:
			replayData = g_controllers.database.getReplayCommonData(replayName)
			if replayData:
				noError = g_controllers.uploader.prepare(replayName, replayData.get('playerID'), replayData.get('playerName'))
				if noError:
					showUploader()
				else:
					def getErrorInfoDialogMeta():
						buttons = InfoDialogButtons(l10n('ui.popup.button.close'))
						return SimpleDialogMeta(message=l10n('ui.uploader.status%s' % g_controllers.uploader.status),
												title=l10n('ui.uploader.statusErrorOccure'), buttons=buttons)
					DialogsInterface.showDialog(getErrorInfoDialogMeta(), lambda *args: None)
		except:
			logger.exception('__uploadBattleReplay')

	@staticmethod
	def __setReplayFavorite(replayName, isFavorite):
		try:
			g_controllers.database.setReplayFavorite(replayName, isFavorite)
			g_eventsManager.onNeedToUpdateReplaysList()
		except:
			logger.exception('__setReplayFavorite')

	@staticmethod
	def __removeBattleReplay(replayName):
		def getConfirmDialogMeta():
			buttons = CustomDialogButtons(l10n('ui.popup.button.yes'), l10n('ui.popup.button.no'))
			return SimpleDialogMeta(message=l10n('ui.popup.delete.message') % replayName,
									title=l10n('ui.popup.delete.title'), buttons=buttons)
		def dialogCallback(result):
			if result:
				try:
					os.remove(REPLAYS_PATH + replayName)
				except:
					logger.exception('__removeBattleReplay dialogCallback os.remove')
				g_eventsManager.onNeedToUpdateReplaysList()
		DialogsInterface.showDialog(getConfirmDialogMeta(), dialogCallback)

class ReplayContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

	def __init__(self, cmProxy, ctx=None):
		self._replayName = None
		self._isFavorite = None
		self._hasBattleResults = None
		self._canShowBattleResults = None
		self._canPlay = None
		super(ReplayContextMenuHandler, self).__init__(cmProxy, ctx, self._getHandlers())

	def showResults(self):
		logger.debug('ReplayContextMenuHandler.showResults')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.SHOW_RESULTS, self._replayName)

	def playReplay(self):
		logger.debug('ReplayContextMenuHandler.playReplay')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.PLAY, self._replayName)

	def uploadReplay(self):
		logger.debug('ReplayContextMenuHandler.uploadReplay')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.UPLOAD, self._replayName)

	def replayAddFavorite(self):
		logger.debug('ReplayContextMenuHandler.replayAddFavorite')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.FAVORITE_ADD, self._replayName)

	def replayRemoveFavorite(self):
		logger.debug('ReplayContextMenuHandler.replayRemoveFavorite')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.FAVORITE_REMOVE, self._replayName)

	def removeReplay(self):
		logger.debug('ReplayContextMenuHandler.removeReplay')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.REMOVE, self._replayName)

	def _getHandlers(self):
		result = {
			REPLAY_ACTIONS.SHOW_RESULTS: 'showResults',
			REPLAY_ACTIONS.PLAY: 'playReplay',
			REPLAY_ACTIONS.UPLOAD: 'uploadReplay',
			REPLAY_ACTIONS.FAVORITE_ADD: 'replayAddFavorite',
			REPLAY_ACTIONS.FAVORITE_REMOVE: 'replayRemoveFavorite',
			REPLAY_ACTIONS.REMOVE: 'removeReplay'
		}
		return result

	def _generateOptions(self, ctx=None):
		options = [
			self._makeItem(REPLAY_ACTIONS.SHOW_RESULTS, l10n('ui.action.showResults'),
							{'enabled': self._hasBattleResults and self._canShowBattleResults}),
			self._makeItem(REPLAY_ACTIONS.PLAY, l10n('ui.action.play'),
							{'enabled': self._canPlay}),
			self._makeItem(REPLAY_ACTIONS.UPLOAD, l10n('ui.action.upload'))
		]
		options.extend(self._getFavorite())
		options2 = [
			self._makeSeparator(),
			self._makeItem(REPLAY_ACTIONS.REMOVE, l10n('ui.action.delete'))
		]
		options.extend(options2)
		return options

	def _getFavorite(self):
		result = [self._makeItem(REPLAY_ACTIONS.FAVORITE_ADD, l10n('ui.action.favoriteAdd'))]
		if self._isFavorite:
			result = [self._makeItem(REPLAY_ACTIONS.FAVORITE_REMOVE, l10n('ui.action.favoriteDelete'))]
		return result

	def _initFlashValues(self, ctx):
		self._replayName = str(ctx.replayName)
		self._isFavorite = bool(ctx.isFavorite)
		self._hasBattleResults = bool(ctx.hasBattleResults)
		self._canShowBattleResults = bool(ctx.canShowBattleResults)
		self._canPlay = bool(ctx.canPlay)

	def _clearFlashValues(self):
		self._replayName = None
		self._isFavorite = None
		self._hasBattleResults = None
		self._canShowBattleResults = None
		self._canPlay = None
