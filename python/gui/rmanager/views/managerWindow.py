
import ArenaType
import BigWorld
import json
from adisp import process
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

from gui.rmanager.lang import l10n, allFields
from gui.rmanager.controllers import g_controllers
from gui.rmanager.events import g_eventsManager
from gui.rmanager.rmanager_constants import DEFAULT_SETTINGS, DATABASE_STATES, WAITING_DELAY

__all__ = ('ReplaysManagerWindow', )

class ReplaysManagerWindowMeta(AbstractWindowView):

	def as_initFiltersS(self, mapping):
		if self._isDAAPIInited():
			return self.flashObject.as_initFilters(mapping)
	

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
	
	def __init__(self):
		super(ReplaysManagerWindow, self).__init__()
		self._settings = DEFAULT_SETTINGS
		self._sortedList = None
	
	def _populate(self):
		self.__populateLanguage()
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
	
	def __populateLanguage(self):
		self.as_setLangDataS(allFields())
		"""
		self.as_setLangDataS({
			'RMANAGER_WINDOW_TITLE': l10n('ui.window.title'),
			'RMANAGER_TABS_OWN': l10n('ui.window.tabsOwn'),
			'RMANAGER_PLACEHOLDER': l10n('ui.window.placeholder'),
			'RMANAGER_FRAGS': l10n('ui.window.frags'),
			'RMANAGER_DAMAGE': l10n('ui.window.damage'),
			'RMANAGER_CREDITS': l10n('ui.window.credits'),
			'RMANAGER_XP': l10n('ui.window.xp'),
			'RMANAGER_SPOTTED': l10n('ui.window.spotted'),
			'RMANAGER_ASSIST': l10n('ui.window.assist'),
			'RMANAGER_BATTLE_RESULT': l10n('ui.window.battleResult'),
			'RMANAGER_BATTLE_RESULT_VICTORY': l10n('ui.window.battleResultVictory'),
			'RMANAGER_BATTLE_RESULT_DEFEAT': l10n('ui.window.battleResultDefeat'),
			'RMANAGER_BATTLE_RESULT_DRAW': l10n('ui.window.battleResultDraw'),
			'RMANAGER_BTN_SHOW_RESULTS': l10n('ui.window.buttonShowResult'),
			'RMANAGER_BTN_PLAY': l10n('ui.window.buttonPlay'),
			'RMANAGER_BTN_UPLOAD': l10n('ui.window.buttonUpload'),
			'RMANAGER_BTN_REMOVE': l10n('ui.window.buttonRemove'),
			'RMANAGER_BTN_APPLY': l10n('ui.window.buttonApply'),
			'RMANAGER_BTN_RESET': l10n('ui.window.buttonReset'),
			'RMANAGER_INFO_PLACEHOLDER': l10n('ui.window.infoPlaceholder'),
			'RMANAGER_SORTING_LABEL': l10n('ui.window.sorting.label'),
			'RMANAGER_SORTING_BY_TIME': l10n('ui.window.sorting.byTime'),
			'RMANAGER_SORTING_BY_CREDITS': l10n('ui.window.sorting.byCredits'),
			'RMANAGER_SORTING_BY_DAMAGE': l10n('ui.window.sorting.byDamage'),
			'RMANAGER_SORTING_BY_RESULT': l10n('ui.window.sorting.byResults'),
			'RMANAGER_SORTING_BY_MAP': l10n('ui.window.sorting.byMap'),
			'RMANAGER_SORTING_BY_VEHICLE': l10n('ui.window.sorting.byVehicle'),
			'RMANAGER_SORTING_BY_XP': l10n('ui.window.sorting.byXp'),
			'RMANAGER_SORTING_BY_KILLS': l10n('ui.window.sorting.byKills'),
			'RMANAGER_SORTING_BY_SPOTTED': l10n('ui.window.sorting.bySpotted'),
			'RMANAGER_SORTING_BY_ASSIST': l10n('ui.window.sorting.byAssist'),
			'RMANAGER_DATE_FILTER_LABEL': l10n('ui.window.dateFilter.label'),
			'RMANAGER_DATE_FILTER_TODAY': l10n('ui.window.dateFilter.today'),
			'RMANAGER_DATE_FILTER_WEEK': l10n('ui.window.dateFilter.week'),
			'RMANAGER_DATE_FILTER_MONTH': l10n('ui.window.dateFilter.month'),
			'RMANAGER_DATE_FILTER_ALL_TIME': l10n('ui.window.dateFilter.allTime'),
			'RMANAGER_FILTER_BTN_LABEL': l10n('ui.window.filterButtonLabel'),
			'RMANAGER_FILTER_TAB_TITLE': l10n('ui.window.filterTab.title'),
			'RMANAGER_FILTER_TAB_ALL': l10n('ui.window.filterTab.all'),
			'RMANAGER_FILTER_TAB_ANY': l10n('ui.window.filterTab.any'),
			'RMANAGER_FILTER_TAB_MAP': l10n('ui.window.filterTab.map'),
			'RMANAGER_FILTER_TAB_MAP_ALL': l10n('ui.window.filterTab.mapAll'),
			'RMANAGER_FILTER_TAB_VEHICLE': l10n('ui.window.filterTab.vehicle'),
			'RMANAGER_FILTER_TAB_VEHICLE_TYPE_ALL': l10n('ui.window.filterTab.vehicleTypeAll'),
			'RMANAGER_FILTER_TAB_VEHICLE_TYPE_HEAVY': l10n('ui.window.filterTab.vehicleTypeHeavy'),
			'RMANAGER_FILTER_TAB_VEHICLE_TYPE_MEDIUM': l10n('ui.window.filterTab.vehicleTypeMedium'),
			'RMANAGER_FILTER_TAB_VEHICLE_TYPE_LIGHT': l10n('ui.window.filterTab.vehicleTypeLight'),
			'RMANAGER_FILTER_TAB_VEHICLE_TYPE_AT_SPG': l10n('ui.window.filterTab.vehicleTypeATSPG'),
			'RMANAGER_FILTER_TAB_VEHICLE_TYPE_SPG': l10n('ui.window.filterTab.vehicleTypeSPG'),
			'RMANAGER_FILTER_TAB_VEHICLE_LEVEL': l10n('ui.window.filterTab.vehicleLevel'),
			'RMANAGER_FILTER_TAB_BATTLE_TYPE': l10n('ui.window.filterTab.battleType'),
			'RMANAGER_FILTER_TAB_BATTLE_RESULT': l10n('ui.window.filterTab.battleResult'),
			'RMANAGER_FILTER_TAB_OTHER_LABEL': l10n('ui.window.filterTab.otherLabel'),
			'RMANAGER_FILTER_TAB_OTHER_SHOW_FAV': l10n('ui.window.filterTab.otherShowFavorite'),
			'RMANAGER_PAGINATOR_LABEL': l10n('ui.window.paginatorLabel'),
			'RMANAGER_PAGINATOR_PREV': l10n('ui.window.paginatorPrev'),
			'RMANAGER_PAGINATOR_NEXT': l10n('ui.window.paginatorNext'),
			'RMANAGER_PAGINATOR_FIRST': l10n('ui.window.paginatorFirst'),
			'RMANAGER_PAGINATOR_LAST': l10n('ui.window.paginatorLast'),
			'RMANAGER_TABS_FILTER': l10n('ui.window.tabsFilter'),
			'RMANAGER_TABS_INFO': l10n('ui.window.tabsInfo')
		})
		"""
		