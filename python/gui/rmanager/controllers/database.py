
import glob
import os
import shelve
import time
import json
from datetime import datetime, timedelta, time as datetime_time
from operator import itemgetter

import BigWorld
from adisp import async, process
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION

from gui.impl import backport
from gui.rmanager.controllers import g_controllers
from gui.rmanager.events import g_eventsManager
from gui.rmanager._constants import REPLAYS_PATH, DB_FILENAME, DB_VERSION, DATABASE_STATES
from gui.rmanager.utils import convertData

__all__ = ('DataBaseController', )

class DataBaseController(object):

	@property
	def currentState(self):
		return self.__state

	def __init__(self):
		self.__replayFiles = []
		self.__database = None
		self.__state = DATABASE_STATES.INITED

	def init(self):
		self.__replayFiles = []
		self.__database = None
		self.__state = DATABASE_STATES.INITED

	def fini(self):
		self.__database = None
		self.__replayFiles = None
		self.__state = DATABASE_STATES.FINI

	@process
	def prepareDataBase(self):
		LOG_DEBUG('DataBaseController.prepareDataBase')
		try:
			dbfolder = DB_FILENAME.replace("/database", "")
			if not os.path.exists(dbfolder):
				os.makedirs(dbfolder)
			self.__replayFiles = [os.path.basename(x) for x in glob.iglob(REPLAYS_PATH + '*.wotreplay')]
			self.__state = DATABASE_STATES.PARSING
			if not os.path.exists(DB_FILENAME + '.dat'):
				self.__createEmptyDataBase()
			else:
				self.__database = shelve.open(DB_FILENAME, protocol=2)
				if self.__database['db_version'] != DB_VERSION:
					self.__database.close()
					self.__createEmptyDataBase()
			yield self.__updateDataBase()
			self.__state = DATABASE_STATES.READY
		except Exception: #NOSONAR
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

	@async
	@process
	def __updateDataBase(self, callback=None):
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
			if replayName not in self.__replayFiles:
				replaysToRemove.append(replayName)

		LOG_DEBUG('DataBaseController.__updateDataBase removing replays', replaysToRemove)
		if replaysToRemove:
			self.__removeFromDataBase(replaysToRemove)

		result = True
		replaysCount = len(replaysToParse)
		for idx, replayName in enumerate(replaysToParse):
			g_eventsManager.onParsingReplay(idx, replaysCount)
			result = yield lambda callback: self.__parseReplayFile(replayName, callback)
		self.__database.close()

		callback(result)

	def __removeFromDataBase(self, replays):
		for replayName in replays:
			if replayName in self.__database['existing_replays']:
				self.__database['existing_replays'].remove(replayName)
			if replayName in self.__database['corrupted_replays']:
				self.__database['corrupted_replays'].remove(replayName)
			if self.__database['replays_data'].has_key(replayName):
				del self.__database['replays_data'][replayName]

	def __parseReplayFile(self, replayName, callback):
		def parseReplayFile():
			try:
				replayData = g_controllers.parser.parseReplay(REPLAYS_PATH + replayName, replayName)
				LOG_DEBUG('DataBaseController.parseReplayFile: %s' % replayName)
				if replayData:
					self.__database['replays_data'][replayName] = replayData
					self.__database['existing_replays'].append(replayName)
				else:
					self.__database['corrupted_replays'].append(replayName)
				callback(True)
			except: #NOSONAR
				LOG_ERROR('DataBaseController.parseReplayFile')
				LOG_CURRENT_EXCEPTION()
				callback(False)
		BigWorld.callback(0, parseReplayFile)

	def getReplaysData(self, settings):
		LOG_DEBUG('DataBaseController.getReplaysData')
		replaysCommonData = self.__getReplaysCommonData()
		filteredList = self.__filterReplays(settings['filters'], replaysCommonData)
		sortedList = self.__sortReplays(filteredList, settings['sorting'])
		expandedNumbers = self.__expandNumbers(sortedList)
		return expandedNumbers

	def getReplayResultData(self, replayName):
		result = None
		LOG_DEBUG('DataBaseController.getReplayResultData %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			result = convertData(self.__database['replays_data'][replayName]['replay_data']['data']['result_data'])
			json.dumps(result)
		except: #NOSONAR
			pass
		finally:
			self.__database.close()
		return result

	def getReplayCommonData(self, replayName):
		result = None
		LOG_DEBUG('DataBaseController.getReplayCommonData %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			result = convertData(self.__database['replays_data'][replayName]['replay_data']['data']['common'])
		finally:
			self.__database.close()
		return result

	def getReplayHasBattleResults(self, replayName):
		result = None
		LOG_DEBUG('DataBaseController.getReplayHasBattleResults %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			result = self.__database['replays_data'][replayName]['common_data']['hasBattleResults']
		finally:
			self.__database.close()
		return result

	def getReplayFavorite(self, replayName):
		result = None
		LOG_DEBUG('DataBaseController.getReplayFavorite %s' % replayName)
		self.__database = shelve.open(DB_FILENAME, flag='r', protocol=2)
		try:
			result = self.__database['replays_data'][replayName]['common_data']['favorite']
		finally:
			self.__database.close()
		return result

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

	@staticmethod
	def __filterReplays(settings, replaysCommonData):
		filteredList = [item for item in replaysCommonData if replayFilterFunc(item, settings)]
		return filteredList

	@staticmethod
	def __sortReplays(list, settings):
		list.sort(key=itemgetter(settings['key']), reverse=settings['reverse'])
		return list

	@staticmethod
	def __expandNumbers(items):
		for item in items:
			for key in 'damageAssistedRadio', 'damage', 'credits', 'xp':
				item[key] = backport.getIntegralFormat(item[key])
		return items


def datetime_to_timestamp(dt):
	return int(time.mktime(dt.timetuple()))

def _dateBetween(startDate, endDate, date):
	result = False
	start = datetime_to_timestamp(startDate)
	end = datetime_to_timestamp(endDate)
	if start <= date <= end:
		result = True
	return result

def _filterByDate(timestamp, dateKey):
	if dateKey == 'today':
		today = datetime.utcnow()
		tomorrow = today + timedelta(1)
		today_start = datetime.combine(today, datetime_time())
		today_end = datetime.combine(tomorrow, datetime_time())
		result = _dateBetween(today_start, today_end, timestamp)
	elif dateKey == 'week':
		today = datetime.utcnow()
		tomorrow = today + timedelta(1)
		today_end = datetime.combine(tomorrow, datetime_time())
		week = today - timedelta(7)
		week_start = datetime.combine(week, datetime_time())
		result = _dateBetween(week_start, today_end, timestamp)
	elif dateKey == 'month':
		today = datetime.utcnow()
		tomorrow = today + timedelta(1)
		today_end = datetime.combine(tomorrow, datetime_time())
		month = today - timedelta(30)
		month_start = datetime.combine(month, datetime_time())
		result = _dateBetween(month_start, today_end, timestamp)
	else:
		result = True
	return result

def replayFilterFunc(item, settings):
	tankInfo = settings['tankInfo']
	result = (
		(item['isWinner'] == settings['isWinner'] or settings['isWinner'] == -100) and
		(item['favorite'] == settings['favorite'] or settings['favorite'] == -1) and
		(item['battleType'] == settings['battleType'] or settings['battleType'] == -1) and
		(item['mapName'] == settings['mapName'] or settings['mapName'] == '') and
		(item['tankInfo']['vehicleNation'] == tankInfo['vehicleNation'] or tankInfo['vehicleNation'] == -1) and
		(item['tankInfo']['vehicleLevel'] == tankInfo['vehicleLevel'] or tankInfo['vehicleLevel'] == -1) and
		(item['tankInfo']['vehicleType'] == tankInfo['vehicleType'] or tankInfo['vehicleType'] == '') and
		(_filterByDate(item['timestamp'], settings['dateTime']))
	)
	return result
