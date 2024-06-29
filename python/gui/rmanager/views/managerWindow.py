# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Andrii Andrushchyshyn

import ArenaType
import BigWorld
import json

from adisp import adisp_process
from constants import ARENA_GUI_TYPE
from helpers import i18n
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

from ..lang import l10n, allFields
from ..controllers import g_controllers
from ..events import g_eventsManager
from .._constants import DEFAULT_SETTINGS, WAITING_DELAY

__all__ = ('ReplaysManagerWindow', )

class ReplaysManagerWindowMeta(AbstractWindowView):

	def as_initFiltersS(self, maps, battleTypes):
		if self._isDAAPIInited():
			return self.flashObject.as_initFilters(maps, battleTypes)

	def as_updateWaitingS(self, message):
		if self._isDAAPIInited():
			self.flashObject.as_updateWaiting(message)

	def as_setLangDataS(self, langData):
		if self._isDAAPIInited():
			return self.flashObject.as_setLangData(langData)

	def as_setAPIStatusS(self, status):
		if self._isDAAPIInited():
			return self.flashObject.as_setAPIStatus(status)

	def as_setReplaysDataS(self, sortedList, listLength):
		if self._isDAAPIInited():
			self.flashObject.as_setReplaysData(sortedList, listLength)

	def as_isModalS(self):
		if self._isDAAPIInited():
			return False

	def onWindowClose(self):
		self.destroy()

class ReplaysManagerWindow(ReplaysManagerWindowMeta):

	def __init__(self, ctx=None):
		super(ReplaysManagerWindow, self).__init__()
		self._settings = DEFAULT_SETTINGS
		self._sortedList = None

	def _populate(self):
		self.__populateLanguage()
		super(ReplaysManagerWindow, self)._populate()
		self.__populateFilters()
		self.__prepareDataBase()
		g_eventsManager.onNeedToUpdateReplaysList += self.__prepareDataBase
		g_eventsManager.onUpdatingDatabaseStop += self.__onUpdatingDatabaseStop
		self.__getAPIStatus()
		g_eventsManager.onParsingReplay += self.__onParsingReplay

	def _dispose(self):
		g_eventsManager.onNeedToUpdateReplaysList -= self.__prepareDataBase
		g_eventsManager.onUpdatingDatabaseStop -= self.__onUpdatingDatabaseStop
		g_eventsManager.onParsingReplay -= self.__onParsingReplay
		super(ReplaysManagerWindow, self)._dispose()

	def updateReplaysList(self, settings, paging=False):
		self._settings = json.loads(settings)
		self.as_showWaitingS(l10n('ui.waiting.updatingList'), {})
		BigWorld.callback(WAITING_DELAY, lambda: self.__updateReplaysList(paging))

	def onReplayAction(self, actionType, replayName):
		g_controllers.actions.handleAction(actionType, replayName)

	@adisp_process
	def __getAPIStatus(self):
		status = yield g_controllers.uploader.apiStatus()
		self.as_setAPIStatusS(status)

	def __onParsingReplay(self, idx, lenght):
		self.as_updateWaitingS(l10n('ui.waiting.prepareDB') + str(' %s / %s' % (str(idx), str(lenght))))

	def __processReplaysData(self, sortedList, listLength):
		self._sortedList = sortedList

		# fix list for login window state (cant show battle results window)
		account = BigWorld.player()
		if not account:
			for item in self._sortedList:
				item['canShowBattleResults'] = False

		pageNum = self._settings['paging']['page']
		pageSize = self._settings['paging']['pageSize']
		endIndex = pageNum * pageSize
		if endIndex > listLength:
			endIndex = listLength
		startIndex = endIndex - pageSize
		if startIndex < 0:
			startIndex = 0
		return sortedList[startIndex:endIndex], listLength

	def __updateReplaysList(self, paging):
		if self._sortedList and paging:
			pageNum = self._settings['paging']['page']
			pageSize = self._settings['paging']['pageSize']
			endIndex = pageNum * pageSize
			listLength = len(self._sortedList)
			if endIndex > listLength:
				endIndex = listLength
			startIndex = endIndex - pageSize
			if startIndex < 0:
				startIndex = 0
			self.as_setReplaysDataS(self._sortedList[startIndex:endIndex], listLength)
		else:
			replaysData = g_controllers.database.getReplaysData(self._settings)
			pagedData, length = self.__processReplaysData(replaysData, len(replaysData))
			self.as_setReplaysDataS(pagedData, length)
		self.as_hideWaitingS()

	def __onUpdatingDatabaseStop(self):
		self.as_hideWaitingS()
		self.as_showWaitingS(l10n('ui.waiting.updatingList'), {})
		BigWorld.callback(WAITING_DELAY, lambda: self.__updateReplaysList(False))

	def __prepareDataBase(self):
		self.as_showWaitingS(l10n('ui.waiting.prepareDB'), {})
		BigWorld.callback(WAITING_DELAY, g_controllers.database.prepareDataBase)

	def __populateFilters(self):
		maps = list()
		for _, arenaType in ArenaType.g_cache.iteritems():
			if arenaType.explicitRequestOnly:
				continue
			maps.append({'label': arenaType.name, 'data': arenaType.geometryName})

		def filterMaps(maps):
			ids = []
			result = []
			for _map in maps:
				if _map['data'] not in ids:
					ids.append(_map['data'])
					result.append(_map)
			return result

		maps = filterMaps(maps)

		btypes = [{'label': l10n('ui.window.filterTab.vehicleTypeAll'), 'data': -1}]
		for gui_type in ARENA_GUI_TYPE.RANGE:
			label = i18n.makeString('#menu:loading/battleTypes/{}'.format(gui_type))
			if 'loading/battleTypes' in label:
				continue
			btypes.append({'label': label, 'data': gui_type})

		self.as_initFiltersS(maps, btypes)

	def __populateLanguage(self):
		self.as_setLangDataS(allFields())
