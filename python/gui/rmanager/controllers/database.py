import BigWorld
import glob
import os
import shelve
import time
import json
from operator import itemgetter
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION

from gui.rmanager.controllers import g_controllers
from gui.rmanager.events import g_eventsManager
from gui.rmanager.rmanager_constants import REPLAYS_PATH, DB_FILENAME, DB_VERSION, DATABASE_STATES
from gui.rmanager.utils import convertData, versionTuple

__all__ = ('DataBaseController', )

class DataBaseController(object):
	
	currentState = property(lambda self: self.__state)

	def __init__(self):
		self.__replayFiles = []
		self.__database = None
	
	def init(self):
		self.__replayFiles = []
		self.__database = None
		self.__state = DATABASE_STATES.INITED  
	
	def fini(self):
		self.__database = None
		self.__replayFiles = None
		self.__state = DATABASE_STATES.FINI
	
	def prepareDataBase(self):
		LOG_DEBUG('DataBaseController.prepareDataBase')
		g_eventsManager.onUpdatingDatabaseStart()
		try:
			dbfolder = DB_FILENAME.replace("/database", "")
			if not os.path.exists(dbfolder):
				os.makedirs(dbfolder)
			self.__replayFiles = [os.path.basename(x) for x in glob.iglob(REPLAYS_PATH + '*.wotreplay')]
			self.__state = DATABASE_STATES.PARSING
			result = False
			if not os.path.exists(DB_FILENAME + '.dat'):
				result = self.__createEmptyDataBase()
			else:
				self.__database = shelve.open(DB_FILENAME, protocol=2)
				if self.__database['db_version'] != DB_VERSION:
					self.__database.close()
					result = self.__createEmptyDataBase()
				else:
					result = self.__updateDataBase()
			self.__state = DATABASE_STATES.READY
			return result
		except Exception as e:
			self.__state = DATABASE_STATES.ERROR
			LOG_ERROR('DataBaseController.prepareDataBase')
			LOG_CURRENT_EXCEPTION()
		finally:
			g_eventsManager.onUpdatingDatabaseStop()
	
	def __createEmptyDataBase(self):
		LOG_DEBUG('DataBaseController.__createEmptyDataBase')
		self.__database = shelve.open(DB_FILENAME, flag='n', protocol=2)
		self.__database['db_version'] = DB_VERSION
		self.__database['corrupted_replays'] = list()
		self.__database['existing_replays'] = list()
		self.__database['replays_data'] = dict()
		self.__database.close()
		result = self.__updateDataBase()
		return result
		
	def __updateDataBase(self):
		LOG_DEBUG('DataBaseController.__updateDataBase')
		replaysToParse = list()
		replaysToRemove = list()
		
		self.__database = shelve.open(DB_FILENAME, flag='w', protocol=2, writeback=True)
		for replayName in self.__replayFiles:
			if replayName in self.__database['corrupted_replays']:
				continue
			if replayName in self.__database['existing_replays']:
				continue
			else:
				replaysToParse.append(replayName)

		for replayName in self.__database['existing_replays']:		   
			if not(replayName in self.__replayFiles):
				replaysToRemove.append(replayName)
		
		LOG_DEBUG('DataBaseController.__updateDataBase removing replays', replaysToRemove)
		if replaysToRemove:
			self.__removeFromDataBase(replaysToRemove)
			
		result = self.__parseToDataBase(replaysToParse)
		self.__database.close()
		return result
			
	def __removeFromDataBase(self, replays):
		for replayName in replays:
			if replayName in self.__database['existing_replays']:
				self.__database['existing_replays'].remove(replayName)
			if replayName in self.__database['corrupted_replays']:
				self.__database['corrupted_replays'].remove(replayName)
			if self.__database['replays_data'].has_key(replayName):
				del self.__database['replays_data'][replayName]
	
	def __parseToDataBase(self, replays):
		try:
			replays_count = len(replays)
			for idx, replayName in enumerate(replays):
				g_eventsManager.onParsingReplay(idx, replays_count)
				replayData = g_controllers.parser.parseReplay(REPLAYS_PATH + replayName, replayName)
				LOG_DEBUG('DataBaseController.__parseToDataBase: %s' % replayName)
				if replayData:
					self.__database['replays_data'][replayName] = replayData
					self.__database['existing_replays'].append(replayName)
				else:
					self.__database['corrupted_replays'].append(replayName)
			return True
		except:
			LOG_ERROR('DataBaseController.__parseToDataBase')
			LOG_CURRENT_EXCEPTION()
			return False
			
	def getReplaysData(self, settings):
		LOG_DEBUG('DataBaseController.getReplaysData')
		replaysCommonData = self.__getReplaysCommonData()
		filteredList = self.__filterReplays(settings['filters'], replaysCommonData)
		sortedList = self.__sortReplays(filteredList, settings['sorting'])
		expandedNumbers = self.__expandNumbers(sortedList)
		return expandedNumbers

	def getReplayResultData(self, replayName):
		LOG_DEBUG('DataBaseController.getReplayResultData %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			result = convertData(self.__database['replays_data'][replayName]['replay_data']['data']['result_data'])
			s = json.dumps(result)
		finally:
			self.__database.close()
			if result:
				return result
			else:
				return None
				
	def getReplayCommonData(self, replayName):
		LOG_DEBUG('DataBaseController.getReplayCommonData %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			result = convertData(self.__database['replays_data'][replayName]['replay_data']['data']['common'])
		finally:
			self.__database.close()
			if result:
				return result
			else:
				return None
				
	def getReplayHasBattleResults(self, replayName):
		LOG_DEBUG('DataBaseController.getReplayHasBattleResults %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			return self.__database['replays_data'][replayName]['common_data']['hasBattleResults']
		finally:
			self.__database.close()
			
				
	def getReplayFavorite(self, replayName):
		LOG_DEBUG('DataBaseController.getReplayFavorite %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			return self.__database['replays_data'][replayName]['common_data']['favorite']
		finally:
			self.__database.close()
				
	def setReplayFavorite(self, replayName, isFavorite):
		LOG_DEBUG('DataBaseController.setReplayFavorite %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='w', protocol=2, writeback=True)
		try:
			self.__database['replays_data'][replayName]['common_data']['favorite'] = 1 if isFavorite else 0
		finally:			
			self.__database.close()
			
	def __getReplaysCommonData(self):
		result = list()
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		for _, replay_data in self.__database['replays_data'].iteritems():
			result.append(convertData(replay_data['common_data']))
		self.__database.close()
		return result
		
	def __filterReplays(self, settings, replaysCommonData):
		filteredList = filter(lambda item: replayFilterFunc(item, settings), replaysCommonData)
		return filteredList

	def __sortReplays(self, list, settings):
		list.sort(key=itemgetter(settings['key']), reverse=settings['reverse'])
		return list
	
	def __expandNumbers(self, items):
		for item in items:
			for key in ['damageAssistedRadio', 'damage', 'credits', 'xp']:
				item[key] = BigWorld.wg_getIntegralFormat(item[key])	
		return items












def datetime_to_timestamp(dt):
	return int(time.mktime(dt.timetuple()))
	
def _dateBetween(startDate, endDate, date):		
	start = datetime_to_timestamp(startDate)
	end = datetime_to_timestamp(endDate)
	if start <= date <= end:
		return True
	else:
		return False
	
def _filterByDate(timestamp, dateKey):
	from datetime import datetime, timedelta, time
	if dateKey == 'today':
		today = datetime.utcnow()
		tomorrow = today + timedelta(1)
		today_start = datetime.combine(today, time())			
		today_end = datetime.combine(tomorrow, time())
		return _dateBetween(today_start, today_end, timestamp)
	if dateKey == 'week':
		today = datetime.utcnow()
		tomorrow = today + timedelta(1)					  
		today_end = datetime.combine(tomorrow, time())
		week = today - timedelta(7)
		week_start = datetime.combine(week, time())
		return _dateBetween(week_start, today_end, timestamp)
	if dateKey == 'month':
		today = datetime.utcnow()
		tomorrow = today + timedelta(1)					  
		today_end = datetime.combine(tomorrow, time())
		month = today - timedelta(30)
		month_start = datetime.combine(month, time())
		return _dateBetween(month_start, today_end, timestamp)
	return True
	
def replayFilterFunc(item, settings):
	result = (
				(item['isWinner'] == settings['isWinner'] or settings['isWinner'] == -100) and
				(item['favorite'] == settings['favorite'] or settings['favorite'] == -1) and
				(item['battleType'] == settings['battleType'] or settings['battleType'] == -1) and
				(item['mapName'] == settings['mapName'] or settings['mapName'] == '') and
				(item['tankInfo']['vehicleNation'] == settings['tankInfo']['vehicleNation'] or settings['tankInfo']['vehicleNation'] == -1) and
				(item['tankInfo']['vehicleLevel'] == settings['tankInfo']['vehicleLevel'] or settings['tankInfo']['vehicleLevel'] == -1) and
				(item['tankInfo']['vehicleType'] == settings['tankInfo']['vehicleType'] or settings['tankInfo']['vehicleType'] == '') and
				(_filterByDate(item['timestamp'], settings['dateTime']))
			)
	return result
	