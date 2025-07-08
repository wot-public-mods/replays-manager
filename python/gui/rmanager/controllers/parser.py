# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import json
import os
import struct
import time
from datetime import datetime

from BattleReplay import REPLAY_FILE_EXTENSION, AUTO_RECORD_TEMP_FILENAME, FIXED_REPLAY_FILENAME
from constants import ARENA_GUI_TYPE
from items import vehicles as core_vehicles
from nations import INDICES as nationsIndices
from soft_exception import SoftException

from .._constants import (RESULTS_SUPPORTED_VERSION, REPLAY_SUPPORTED_VERSION,\
							PROCESS_SUPPORTED_VERSION, DEFAULT_PACK_SIZE)
from ..utils import byteify, versionTuple, getTankType, fixBadges, getLogger

logger = getLogger(__name__)

__all__ = ('ParserController', )

class ParserController(object):

	def init(self):
		pass

	def fini(self):
		pass

	@staticmethod
	def parseReplay(file_path, file_name):

		# skip autorecord
		if file_name == AUTO_RECORD_TEMP_FILENAME + REPLAY_FILE_EXTENSION:
			return None

		# skip last battle record
		if file_name == FIXED_REPLAY_FILENAME + REPLAY_FILE_EXTENSION:
			return None

		result_blocks = dict()
		result_blocks['data'] = dict()

		with open(file_path, 'rb') as fh:
			try:
				# get blocks count
				offset = DEFAULT_PACK_SIZE
				fh.seek(DEFAULT_PACK_SIZE)
				blocks_count = struct.unpack('I', fh.read(DEFAULT_PACK_SIZE))[0]
				offset += DEFAULT_PACK_SIZE
			except:
				logger.exception('ParserController.parseReplay %s', file_name)
				return None

			if blocks_count == 0:
				logger.debug('File %s has unknown file structure. (blocks_count == 0)', file_name)
				return None
			elif blocks_count > 2:
				logger.debug('File %s has unknown file structure. (blocks_count > 2)', file_name)
				return None

			# iter blocks
			has_common = False
			for _ in range(blocks_count):
				fh.seek(offset)
				block_size = struct.unpack('I', fh.read(DEFAULT_PACK_SIZE))[0]
				offset += DEFAULT_PACK_SIZE
				fh.seek(offset)
				data = fh.read(block_size)
				offset += block_size
				try:
					blockdict = byteify(json.loads(data))
					if not has_common:
						vehicleInfo = ParserController.getVehicleInfo(blockdict)
						if not vehicleInfo:
							return None
						blockdict['vehicleInfo'] = vehicleInfo
						result_blocks['data']['common'] = blockdict
						has_common = True
					else:
						result_blocks['data']['result_data'] = fixBadges(blockdict[0])
				except:
					logger.exception('parseReplay %s', file_name)
					return None

			result = ParserController.getProcessedReplayData(result_blocks, file_name)
			return result

	@staticmethod
	def getProcessedReplayData(result_blocks, file_name):
		result_dict = dict()
		if 'common' in result_blocks['data']:
			exeVer = versionTuple(result_blocks['data']['common']['clientVersionFromExe'])
			if exeVer < PROCESS_SUPPORTED_VERSION and exeVer != (0, 0, 0, 0):
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
			result_dict['common_data']['canShowBattleResults'] = exeVer == (0, 0, 0, 0) or exeVer >= RESULTS_SUPPORTED_VERSION
			result_dict['common_data']['canPlay'] = exeVer == (0, 0, 0, 0) or exeVer >= REPLAY_SUPPORTED_VERSION
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
			result_dict['common_data']['assist'] = int(personal_block.get('damageAssistedRadio', 0)) + int(personal_block.get('damageAssistedTrack', 0)) + int(personal_block.get('damageAssistedStun', 0))
			result_dict['common_data']['spotted'] = int(personal_block.get('spotted'))
			result_dict['common_data']['originalXP'] = int(personal_block.get('originalXP'))
			playerTeam = int(personal_block.get('team'))

			winnerTeam = int(result_blocks['data']['result_data']['common']['winnerTeam'])
			result_dict['common_data']['winnerTeam'] = int(winnerTeam)
			result_dict['common_data']['isWinner'] = 1 if winnerTeam == playerTeam else 0
			if winnerTeam == 0:
				result_dict['common_data']['isWinner'] = -5

			# 1.25.1 fixes
			common_data = result_blocks['data']['result_data']['common']
			if 'bonusCapsOverrides' in common_data:
				for override in common_data['bonusCapsOverrides'].values():
					for opeartor in override.keys():
						override[opeartor] = set(override[opeartor])
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
			result_dict['common_data']['assist'] = -10
			result_dict['common_data']['spotted'] = -10
			result_dict['common_data']['originalXP'] = -10

		if result_dict['common_data']['battleType'] not in ARENA_GUI_TYPE.RANGE:
			result_dict['common_data']['battleType'] = ARENA_GUI_TYPE.RANDOM

		return result_dict

	@staticmethod
	def getVehicleInfo(data):
		try:
			vFullName = data['playerVehicle'].replace('-', ':', 1)
			vNation = vFullName.split(':', 1)[0]
			nationIdx = nationsIndices[vNation]
			try:
				itemID = core_vehicles.g_list.getIDsByName(vFullName)[1]
			except SoftException:
				return
			vItem = core_vehicles.g_cache.vehicle(nationIdx, itemID)
			return {
				'vehicleNation': int(nationIdx),
				'vehicleLevel': int(vItem.level),
				'vehicleType': getTankType(vItem.tags),
				'userString': vItem.userString,
				'shortUserString': vItem.shortUserString
			}
		except:
			logger.exception('getVehicleInfo')

	@staticmethod
	def getReplayHash(file_path):
		return str(os.path.getmtime(file_path))
