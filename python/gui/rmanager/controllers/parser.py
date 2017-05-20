
import struct
import time
import nations
import json
from items import vehicles as core_vehicles
from datetime import datetime
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION

from gui.rmanager.rmanager_constants import CURRENT_GAME_VERSION
from gui.rmanager.utils import byteify, versionTuple, getTankType, convertKeys


__all__ = ('ParserController', )

class ParserController(object):
	
	def init(self):
		pass
	
	def fini(self):
		pass
	
	def parseReplay(self, file_path, file_name):
		
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
			except:
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
							blockdict['vehicleInfo'] = self.__getVehicleInfo(blockdict)
							result_blocks['data']['common'] = blockdict
						else:
							blockdict = byteify(json.loads(myblock))
							result_blocks['data']['result_data'] = blockdict[0]
				except:
					LOG_ERROR('ParserController.parseReplay %s' % file_name)
					LOG_CURRENT_EXCEPTION()
					return None
			
			result = self.__getProcessedReplayData(result_blocks, file_name)
			
			return result
	
	def processBattleResults(self, battle_results_dict):
		try:
			battle_results_dict['players'] = convertKeys(battle_results_dict['players'])
			battle_results_dict['vehicles'] = convertKeys(battle_results_dict['vehicles'])
			try:
				battle_results_dict['personal']['details'] = convertKeys(battle_results_dict['personal']['details'])
			except:
				battle_results_dict['personal'].values()[0]['details'] = convertKeys(battle_results_dict['personal'].values()[0]['details'])
			return battle_results_dict
		except:
			LOG_ERROR('ParserController.processBattleResults')
			LOG_CURRENT_EXCEPTION()
	
	def __getProcessedReplayData(self, result_blocks, file_name):
		result_dict = dict()
		try:
			if 'common' in result_blocks['data']:
				result_dict['replay_data'] = result_blocks
				result_dict['common_data'] = dict()
				result_dict['common_data']['label'] = file_name
				result_dict['common_data']['favorite'] = 0
				date_string = result_blocks['data']['common']['dateTime']
				result_dict['common_data']['dateTime'] = date_string		
				result_dict['common_data']['timestamp'] = int(time.mktime(datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S").timetuple()))
				result_dict['common_data']['mapName'] = result_blocks['data']['common']['mapName']
				result_dict['common_data']['mapDisplayName'] = result_blocks['data']['common']['mapDisplayName']			
				result_dict['common_data']['playerVehicle'] = result_blocks['data']['common']['playerVehicle']
				result_dict['common_data']['tankInfo'] = result_blocks['data']['common']['vehicleInfo']
				if result_blocks['data']['common']['battleType'] == 22:
					result_dict['common_data']['battleType'] = 17
				else:
					result_dict['common_data']['battleType'] = result_blocks['data']['common']['battleType']
				
				result_dict['common_data']['canShowBattleResults'] = versionTuple(result_blocks['data']['common']['clientVersionFromExe']) >= CURRENT_GAME_VERSION
			else:
				return None
			
			hasBattleResults = False
			if 'result_data' in result_blocks['data']:
				try:		 
					personal_block = None
					vehicleKey = None
					for key in result_blocks['data']['result_data']['personal']:
						if key != 'avatar':
							vehicleKey = key
							personal_block = result_blocks['data']['result_data']['personal'].get(key).copy()
					
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
				except:
					LOG_ERROR('ParserController.__getProcessedReplayData parser')
					LOG_CURRENT_EXCEPTION()
					hasBattleResults = False
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
				
			return result_dict
		except:
			LOG_ERROR('ParserController.__getProcessedReplayData')
			LOG_CURRENT_EXCEPTION()
			return None
	
	def __getVehicleInfo(self, common_dict):
		try:
			vFullName = common_dict['playerVehicle'].replace('-', ':', 1)
			vNation = vFullName.split(':', 1)[0]
			nationIdx = nations.INDICES[vNation]
			itemID = core_vehicles.g_list.getIDsByName(vFullName)[1]
			vItem = core_vehicles.g_cache.vehicle(nationIdx, itemID)
			return {'vehicleNation': int(nationIdx), 
					'vehicleLevel': int(vItem.level),
					'vehicleType': getTankType(vItem.tags),
					'userString': vItem.userString,
					'shortUserString': vItem.shortUserString}
					
		except:
			LOG_ERROR('ParserController.__getVehicleInfo')
			LOG_CURRENT_EXCEPTION()
			return {'vehicleNation': 0,
					'vehicleLevel': 1,
					'vehicleType': 'unknown',
					'userString': 'unknown',
					'shortUserString': 'unknown'}
