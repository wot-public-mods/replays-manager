import os
import BigWorld
import BattleReplay
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta, ConfirmDialogButtons, InfoDialogButtons, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.framework.managers.loaders import ViewLoadParams
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName
from gui.Scaleform.framework.managers import context_menu
from gui.app_loader.loader import g_appLoader
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from skeletons.gui.game_control import IRankedBattlesController

from gui.rmanager.controllers import g_controllers
from gui.rmanager.events import g_eventsManager
from gui.rmanager.lang import l10n
from gui.rmanager.rmanager_constants import REPLAYS_PATH, REPLAY_CM_HANDLER_TYPE, REPLAY_ACTIONS, REPLAY_FLAG_FILE, REPLAYS_MANAGER_UPLOADER_ALIAS

class CustomDialogButtons(ConfirmDialogButtons):
	
	def getLabels(self):
		return [ {'id': DIALOG_BUTTON_ID.SUBMIT, 'label': self._submit, 'focused': False}, {'id': DIALOG_BUTTON_ID.CLOSE, 'label': self._close, 'focused': True } ]

class ActionsController(object):
	
	rankedController = dependency.descriptor(IRankedBattlesController)
	battleResults = dependency.descriptor(IBattleResultsService)
	
	def __init__(self):
		self.__isReplayPlayed = False
	
	def init(self):
		g_eventsManager.onLoginViewLoaded += self.__onLoginViewLoaded
		context_menu.registerHandlers((REPLAY_CM_HANDLER_TYPE, ReplayContextMenuHandler))

	def fini(self):
		g_eventsManager.onLoginViewLoaded -= self.__onLoginViewLoaded
	
	def __onLoginViewLoaded(self):
		LOG_DEBUG('ActionsController.__onLoginViewLoaded')
		if os.path.exists(REPLAY_FLAG_FILE):
			with open(REPLAY_FLAG_FILE) as f:
				replayName = f.read()
			os.remove(REPLAY_FLAG_FILE)
			if replayName:
				self.__tryToPlay(replayName) 
	
	def handleAction(self, actionType, replayName):
		LOG_DEBUG('ActionsController.handleAction => actionType: %s, replayName: %s' % (actionType, replayName))
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
			replayData = g_controllers.database.getReplayResultData(replayName)
			if replayData:
				arenaUniqueID = replayData.get('arenaUniqueID', 0)
				LOG_DEBUG("ActionsController.__showBattleResults => replayData: %s", replayData)
				if not self.battleResults.areResultsPosted(arenaUniqueID):
					rankedControllerABRWS = self.rankedController._RankedBattlesController__arenaBattleResultsWasShown
					if arenaUniqueID not in rankedControllerABRWS:
						rankedControllerABRWS.add(arenaUniqueID)
					self.battleResults.postResult(replayData, False)
				g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BATTLE_RESULTS, getViewName(VIEW_ALIAS.BATTLE_RESULTS, str(arenaUniqueID)), ctx={'arenaUniqueID': arenaUniqueID}), EVENT_BUS_SCOPE.LOBBY)
				LOG_DEBUG('ActionsController.__showBattleResults => replayName: %s' % replayName)
		except:
			LOG_ERROR('ActionsController.__showBattleResults')
			LOG_CURRENT_EXCEPTION()
	
	def __playBattleReplay(self, replayName):
		try:
			LOG_DEBUG('ActionsController.__playBattleReplay => isReplayPlayed: %s' % self.__isReplayPlayed)
			if self.__isReplayPlayed or not self.__tryToPlay(replayName):
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
			else:
				g_eventsManager.onNeedToClose()
		except:
			LOG_ERROR('ActionsController.__playBattleReplay')
			LOG_CURRENT_EXCEPTION()
	
	def __uploadBattleReplay(self, replayName):
		try:
				
			replayData = g_controllers.database.getReplayCommonData(replayName)
			if replayData:
				data = {
					'replayName': replayName,
					'userId': str(replayData.get('playerID')),
					'userName': str(replayData.get('playerName'))
				}
				noError = g_controllers.uploader.prepare(replayName, replayData.get('playerID'), replayData.get('playerName'))
				if noError:
					g_appLoader.getDefLobbyApp().loadView(ViewLoadParams(REPLAYS_MANAGER_UPLOADER_ALIAS, REPLAYS_MANAGER_UPLOADER_ALIAS))
				else:
					
					def getErrorInfoDialogMeta():
						buttons = InfoDialogButtons(l10n('ui.popup.button.close'))
						return SimpleDialogMeta(message=l10n('ui.uploader.status%s' % g_controllers.uploader.status), title=l10n('ui.uploader.statusErrorOccure'), buttons=buttons)
					DialogsInterface.showDialog(getErrorInfoDialogMeta(), lambda *args: None)
		
		except:
			LOG_ERROR('ActionsController.__uploadBattleReplay')
			LOG_CURRENT_EXCEPTION()
	
	def __setReplayFavorite(self, replayName, isFavorite):
		try:
			g_controllers.database.setReplayFavorite(replayName, isFavorite)
			g_eventsManager.onNeedToUpdateReplaysList()
		except:
			LOG_ERROR('ActionsController.__setReplayFavorite')
			LOG_CURRENT_EXCEPTION()
	
	def __removeBattleReplay(self, replayName):
		
		def getConfirmDialogMeta():
			buttons = CustomDialogButtons(l10n('ui.popup.button.yes'), l10n('ui.popup.button.no'))
			return SimpleDialogMeta(message=l10n('ui.popup.delete.message') % replayName, title=l10n('ui.popup.delete.title'), buttons=buttons)
			
		def dialogCallback(result):
			if result:
				try:
					os.remove(REPLAYS_PATH + replayName)
				except:
					LOG_ERROR('ActionsController.__removeBattleReplay dialogCallback os.remove')
					LOG_CURRENT_EXCEPTION()
				g_eventsManager.onNeedToUpdateReplaysList()
		
		DialogsInterface.showDialog(getConfirmDialogMeta(), dialogCallback)
	
	def __tryToPlay(self, replayName):
		import SafeUnpickler
		import cPickle
		unpickler = SafeUnpickler.SafeUnpickler()
		cPickle.loads = unpickler.loads		
		if BattleReplay.g_replayCtrl._BattleReplay__replayCtrl.startPlayback(REPLAYS_PATH + replayName): 
			BattleReplay.g_replayCtrl._BattleReplay__playbackSpeedIdx = BattleReplay.g_replayCtrl._BattleReplay__playbackSpeedModifiers.index(1.0)
			BattleReplay.g_replayCtrl._BattleReplay__savedPlaybackSpeedIdx = BattleReplay.g_replayCtrl._BattleReplay__playbackSpeedIdx  
			self.__isReplayPlayed = True
			return True
		else:
			return False

class ReplayContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

	def __init__(self, cmProxy, ctx = None):
		super(ReplayContextMenuHandler, self).__init__(cmProxy, ctx, self._getHandlers())

	def fini(self):
		super(ReplayContextMenuHandler, self).fini()
		
	def showResults(self):
		LOG_DEBUG('ReplayContextMenuHandler.showResults')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.SHOW_RESULTS, self._replayName)
		
	def playReplay(self):
		LOG_DEBUG('ReplayContextMenuHandler.playReplay')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.PLAY, self._replayName)
		
	def uploadReplay(self):
		LOG_DEBUG('ReplayContextMenuHandler.uploadReplay')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.UPLOAD, self._replayName)
		
	def replayAddFavorite(self):
		LOG_DEBUG('ReplayContextMenuHandler.replayAddFavorite')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.FAVORITE_ADD, self._replayName)
		
	def replayRemoveFavorite(self):
		LOG_DEBUG('ReplayContextMenuHandler.replayRemoveFavorite')
		g_controllers.actions.handleAction(REPLAY_ACTIONS.FAVORITE_REMOVE, self._replayName)
		
	def removeReplay(self):
		LOG_DEBUG('ReplayContextMenuHandler.removeReplay')
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
	
	def _generateOptions(self, ctx = None):
		options = [
			self._makeItem(REPLAY_ACTIONS.SHOW_RESULTS, l10n('ui.action.showResults'), {'enabled': self._hasBattleResults and self._canShowBattleResults}), 
			self._makeItem(REPLAY_ACTIONS.PLAY, l10n('ui.action.play')),
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
		if self._isFavorite:
			return [self._makeItem(REPLAY_ACTIONS.FAVORITE_REMOVE, l10n('ui.action.favoriteDelete'))]
		else:
			return [self._makeItem(REPLAY_ACTIONS.FAVORITE_ADD, l10n('ui.action.favoriteAdd'))]
		
	def _initFlashValues(self, ctx):
		self._replayName = str(ctx.replayName)
		self._isFavorite = bool(ctx.isFavorite)
		self._hasBattleResults  = bool(ctx.hasBattleResults)
		self._canShowBattleResults = bool(ctx.canShowBattleResults)

	def _clearFlashValues(self):
		self._replayName = None
		self._isFavorite = None
		self._hasBattleResults = None
		self._canShowBattleResults = None
