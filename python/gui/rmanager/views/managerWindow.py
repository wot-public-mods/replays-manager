
import ArenaType
import BigWorld
import json
from adisp import process
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

from gui.rmanager.lang import l10n
from gui.rmanager.controllers import g_controllers
from gui.rmanager.events import g_eventsManager
from gui.rmanager.rmanager_constants import DEFAULT_SETTINGS, DATABASE_STATES, WAITING_DELAY

__all__ = ('ReplaysManagerWindow', )

class ReplaysManagerWindowMeta(AbstractWindowView):

	def as_initFiltersS(self, mapping):
		if self._isDAAPIInited():
			return self.flashObject.as_initFilters(mapping)
	
	def as_setAPIStatusS(self, status):
		if self._isDAAPIInited():
			return self.flashObject.as_setAPIStatus(status)
	
	def as_setReplaysDataS(self, sortedList, listLength):
		if self._isDAAPIInited():
			self.flashObject.as_setReplaysData(sortedList, listLength)
	
class ReplaysManagerWindow(ReplaysManagerWindowMeta):
	
	def __init__(self):
		super(ReplaysManagerWindow, self).__init__()
		self._settings = DEFAULT_SETTINGS
		self._sortedList = None
	
	def _populate(self):
		super(ReplaysManagerWindow, self)._populate()
		self.__populateFilters()
		self.__prepareDataBase()
		g_eventsManager.onNeedToUpdateReplaysList += self.__prepareDataBase
		g_eventsManager.onNeedToClose += self.onWindowClose
		g_eventsManager.onUpdatingDatabaseStop += self.__onUpdatingDatabaseStop 
		self.__getAPIStatus()
	
	def _dispose(self):
		g_eventsManager.onNeedToUpdateReplaysList -= self.__prepareDataBase
		g_eventsManager.onNeedToClose -= self.onWindowClose
		g_eventsManager.onUpdatingDatabaseStop -= self.__onUpdatingDatabaseStop
		super(ReplaysManagerWindow, self)._dispose()
	
	def updateReplaysList(self, settings, paging=False):
		self._settings = json.loads(settings)
		self.as_showWaitingS(l10n('ui.waiting.updatingList'), {})
		BigWorld.callback(WAITING_DELAY, lambda: self.__updateReplaysList(paging))
	
	def onReplayAction(self, actionType, replayName):
		g_controllers.actions.handleAction(actionType, replayName)
	
	@process
	def __getAPIStatus(self):
		status = yield g_controllers.uploader.apiStatus()
		self.as_setAPIStatusS(status)
	
	def __processReplaysData(self, sortedList, listLength):
		self._sortedList = sortedList
		pageNum = self._settings['paging']['page']
		pageSize = self._settings['paging']['pageSize']
		endIndex = pageNum * pageSize
		if endIndex > listLength:
			endIndex = listLength
		startIndex = endIndex - pageSize
		if startIndex < 0:
			startIndex = 0		
		return (sortedList[startIndex:endIndex], listLength)
	
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
		for arenaTypeID, arenaType in ArenaType.g_cache.iteritems():
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
		self.as_initFiltersS(maps)
	
	def onWindowClose(self):
		self.destroy()
	
	def as_isModalS(self):
		if self._isDAAPIInited():
			return False
	
	