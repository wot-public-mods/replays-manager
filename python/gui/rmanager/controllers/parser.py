
import json
import struct
import time
from datetime import datetime

from constants import ARENA_GUI_TYPE
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from items import vehicles as core_vehicles
from nations import INDICES as nationsIndices

from gui.rmanager.rmanager_constants import RESULTS_SUPPORTED_VERSION, REPLAY_SUPPORTED_VERSION
from gui.rmanager.utils import byteify, versionTuple, getTankType

__all__ = ('ParserController', )

class ParserController(object):

	def init(self):
		pass

	def fini(self):
		pass

	@staticmethod
	def parseReplay(file_path, file_name):

		if file_name == 'temp.wotreplay':
			return None

		result_blocks = dict()
		result_blocks['data'] = dict()

		with open(file_path, 'rb') as f:
			try:
				f.seek(4)
				numofblocks = struct.unpack('I', f.read(4))[0]
				blockNum = 1
				datablockPointer = {}
				datablockSize = {}
				startPointer = 8
			except: #NOSONAR
				LOG_ERROR('ParserController.parseReplay %s' % file_name)
				LOG_CURRENT_EXCEPTION()
				return None

			if numofblocks == 0:
				LOG_DEBUG('File %s has unknown file structure. (numofblocks == 0)' % file_name)
				return None
			if numofblocks > 4:
				LOG_DEBUG('File %s has unknown file structure. (numofblocks > 4)' % file_name)
				return None

			while numofblocks >= 1:
				try:
					f.seek(startPointer)
					size = f.read(4)
					datablockSize[blockNum] = struct.unpack('I', size)[0]
					datablockPointer[blockNum] = startPointer + 4
					startPointer = datablockPointer[blockNum] + datablockSize[blockNum]
					blockNum += 1
					numofblocks -= 1
					for i in datablockSize:
						f.seek(datablockPointer[i])
						myblock = f.read(int(datablockSize[i]))
						blockdict = dict()
						if 'arenaUniqueID' not in str(myblock):
							blockdict = byteify(json.loads(myblock))
							blockdict['vehicleInfo'] = ParserController.getVehicleInfo(blockdict)
							result_blocks['data']['common'] = blockdict
						else:
							blockdict = byteify(json.loads(myblock))
							result_blocks['data']['result_data'] = blockdict[0]
				except: #NOSONAR
					LOG_ERROR('ParserController.parseReplay %s' % file_name)
					LOG_CURRENT_EXCEPTION()
					return None

			result = ParserController.getProcessedReplayData(result_blocks, file_name)
			return result

	@staticmethod
	def getProcessedReplayData(result_blocks, file_name):
		result_dict = dict()
		if 'common' in result_blocks['data']:
			clientVersionFromExe = versionTuple(result_blocks['data']['common']['clientVersionFromExe'])
			if clientVersionFromExe < REPLAY_SUPPORTED_VERSION and clientVersionFromExe != (0, 0, 0, 0):
				return None
			date_string = result_blocks['data']['common']['dateTime']
			timestamp = int(time.mktime(datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S").timetuple()))
			result_dict['replay_data'] = result_blocks
			result_dict['common_data'] = dict()
			result_dict['common_data']['label'] = file_name
			result_dict['common_data']['favorite'] = 0
			result_dict['common_data']['dateTime'] = date_string
			result_dict['common_data']['timestamp'] = timestamp
			result_dict['common_data']['mapName'] = result_blocks['data']['common']['mapName']
			result_dict['common_data']['mapDisplayName'] = result_blocks['data']['common']['mapDisplayName']
			result_dict['common_data']['playerVehicle'] = result_blocks['data']['common']['playerVehicle']
			result_dict['common_data']['tankInfo'] = result_blocks['data']['common']['vehicleInfo']
			result_dict['common_data']['battleType'] = result_blocks['data']['common']['battleType']
			result_dict['common_data']['canShowBattleResults'] = clientVersionFromExe == (0, 0, 0, 0) or clientVersionFromExe >= RESULTS_SUPPORTED_VERSION
		else:
			return None

		hasBattleResults = False
		if 'result_data' in result_blocks['data']:
			personal_block = None
			for key in result_blocks['data']['result_data']['personal']:
				if key != 'avatar':
					personal_block = result_blocks['data']['result_data']['personal'].get(key).copy()
					pVehicle = result_dict['replay_data']['data']['result_data']['personal'][key]
					pVehicle['premiumCreditsFactor100'] = pVehicle.get('premiumCreditsFactor100', 100)
					pVehicle['appliedPremiumCreditsFactor100'] = pVehicle.get('appliedPremiumCreditsFactor100', 100)
					pVehicle['premiumXPFactor100'] = pVehicle.get('premiumXPFactor100', 100)
					pVehicle['appliedPremiumXPFactor100'] = pVehicle.get('appliedPremiumXPFactor100', 100)
					pVehicle['additionalXPFactor10'] = pVehicle.get('additionalXPFactor10', 10)
					pVehicle['originalCreditsToDraw'] = pVehicle.get('originalCreditsToDraw', \
																				pVehicle.get('creditsToDraw', 0))
					# 1.5 fixes
					pVehicle['piggyBank'] = pVehicle.get('piggyBank', 0)
					pVehicle['premiumPlusXPFactor100'] = pVehicle.get('premiumPlusXPFactor100', 100)
					pVehicle['premiumPlusCreditsFactor100'] = pVehicle.get('premiumPlusCreditsFactor100', 100)
					pVehicle['premSquadCreditsFactor100'] = pVehicle.get('premSquadCreditsFactor100', 100)
					pVehicle['originalPremSquadCredits'] = pVehicle.get('originalPremSquadCredits', 0)
					pVehicle['originalCreditsPenaltySquad'] = pVehicle.get('originalCreditsPenaltySquad', 0)
					pVehicle['originalCreditsContributionOutSquad'] = pVehicle.get('originalCreditsContributionOutSquad', 0)
					pVehicle['originalCreditsContributionInSquad'] = pVehicle.get('originalCreditsContributionInSquad', 0)
					pVehicle['originalCreditsToDrawSquad'] = pVehicle.get('originalCreditsToDrawSquad', 0)

			# 1.5 fixes
			if 'vehicles' in result_blocks['data']['result_data']:
				for _, vehicleData in result_blocks['data']['result_data']['vehicles'].iteritems():
					vehicleData[0]['xpPenalty'] = vehicleData[0].get('xpPenalty', 0)

			result_dict['common_data']['battleType'] = result_blocks['data']['result_data']['common']['guiType']

			result_dict['common_data']['xp'] = int(personal_block.get('xp'))
			result_dict['common_data']['credits'] = int(personal_block.get('credits'))
			result_dict['common_data']['damage'] = int(personal_block.get('damageDealt'))
			result_dict['common_data']['kills'] = int(personal_block.get('kills'))
			result_dict['common_data']['damageAssistedRadio'] = int(personal_block.get('damageAssistedRadio'))
			result_dict['common_data']['spotted'] = int(personal_block.get('spotted'))
			playerTeam = int(personal_block.get('team'))

			winnerTeam = int(result_blocks['data']['result_data']['common']['winnerTeam'])
			result_dict['common_data']['winnerTeam'] = int(winnerTeam)
			result_dict['common_data']['isWinner'] = 1 if winnerTeam == playerTeam else 0
			if winnerTeam == 0:
				result_dict['common_data']['isWinner'] = -5

			hasBattleResults = True
		else:
			hasBattleResults = False

		result_dict['common_data']['hasBattleResults'] = hasBattleResults

		if not hasBattleResults:
			result_dict['common_data']['hasBattleResults'] = False
			result_dict['common_data']['xp'] = -10
			result_dict['common_data']['credits'] = -10
			result_dict['common_data']['damage'] = -10
			result_dict['common_data']['isWinner'] = -10
			result_dict['common_data']['kills'] = -10
			result_dict['common_data']['damageAssistedRadio'] = -10
			result_dict['common_data']['spotted'] = -10

		if result_dict['common_data']['battleType'] not in ARENA_GUI_TYPE.RANGE:
			result_dict['common_data']['battleType'] = ARENA_GUI_TYPE.RANDOM

		return result_dict

	@staticmethod
	def getVehicleInfo(data):
		try:
			vFullName = data['playerVehicle'].replace('-', ':', 1)
			vNation = vFullName.split(':', 1)[0]
			nationIdx = nationsIndices[vNation]
			itemID = core_vehicles.g_list.getIDsByName(vFullName)[1]
			vItem = core_vehicles.g_cache.vehicle(nationIdx, itemID)
			return {
				'vehicleNation': int(nationIdx),
				'vehicleLevel': int(vItem.level),
				'vehicleType': getTankType(vItem.tags),
				'userString': vItem.userString,
				'shortUserString': vItem.shortUserString
			}
		except: #NOSONAR
			LOG_ERROR('getVehicleInfo')
			LOG_CURRENT_EXCEPTION()
			return {
				'vehicleNation': 0,
				'vehicleLevel': 1,
				'vehicleType': 'unknown',
				'userString': 'unknown',
				'shortUserString': 'unknown'
			}
