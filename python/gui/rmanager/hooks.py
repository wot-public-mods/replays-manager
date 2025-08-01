# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import struct

from BattleReplay import BattleReplay
from battle_results import g_config as battle_results_config
from gui.shared.personality import ServicesLocator
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_results.service import BattleResultsService
from gui.lobby_context import LobbyContext
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import AppealCMHandler, USER
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils.requesters.ItemsRequester import ItemsRequester
from soft_exception import SoftException
from ValueReplay import ValueReplay as op, ValueReplayConnector

from .lang import l10n
from .utils import override, safeImport, getParentWindow, getLogger
from ._constants import  REPLAYS_MANAGER_WINDOW_ALIAS, REPLAYS_MANAGER_UPLOADER_ALIAS

logger = getLogger(__name__)

# normal client codebase
_EconomicsRecordsChains = safeImport('gui.battle_results.reusable.personal', '_EconomicsRecordsChains')

# waffantrager event codebase
if not _EconomicsRecordsChains:
	_EconomicsRecordsChains = safeImport('gui.battle_results.reusable.economics', '_EconomicsRecordsChains')

# WoT 1.25.1 codebase
if not _EconomicsRecordsChains:
	_EconomicsRecordsChains = safeImport('gui.battle_results.reusable.economics_records', 'EconomicsRecordsChains')

if not _EconomicsRecordsChains:
	raise SoftException('cant import EconomicsRecordsChains')

__all__ = ()

def showManager():
	"""fire load popover view on button click"""
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(REPLAYS_MANAGER_WINDOW_ALIAS, parent=getParentWindow()))

def showUploader():
	"""fire load popover view on button click"""
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(REPLAYS_MANAGER_UPLOADER_ALIAS, parent=getParentWindow()))

@override(BattleReplay, 'getAutoStartFileName')
def getAutoStartFileName(baseMethod, baseObject):
	from . import g_controllers
	replay_filename = g_controllers.player.getReplayFileName()
	return replay_filename or baseMethod(baseObject)

# context menu fixes
@override(LobbyContext, 'getPlayerFullName')
def getPlayerFullName(baseMethod, baseObject, pName, clanInfo=None, clanAbbrev=None, regionCode=None, pDBID=None):
	if clanAbbrev:
		clanAbbrev = str(clanAbbrev)
	return baseMethod(baseObject, str(pName), clanInfo, clanAbbrev, regionCode, pDBID)

@override(ItemsRequester, 'getItemByCD')
def getItemByCD(baseMethod, baseObject, typeCompDescr):
	try:
		result = baseMethod(baseObject, typeCompDescr)
		return result
	except:
		return 0

@override(AppealCMHandler, 'getOptions')
def getOptions(baseMethod, baseObject, ctx=None):
	if baseObject.prbDispatcher:
		return baseMethod(baseObject, ctx) or []
	return [
		baseObject._makeItem(USER.COPY_TO_CLIPBOARD, MENU.contextmenu(USER.COPY_TO_CLIPBOARD)),
		baseObject._makeItem(USER.VEHICLE_INFO, MENU.contextmenu(USER.VEHICLE_INFO))
	]

# modsListApi
g_modsListApi = None
try:
	from gui.modsListApi import g_modsListApi
except ImportError:
	logger.error('modsListApi not installed')
if g_modsListApi:
	g_modsListApi.addModification(id='rmanager', name=l10n('modsListApi.name'), enabled=True,
		description=l10n('modsListApi.description'), icon='gui/maps/rmanager/modsListApi.png',
		callback=showManager, login=True, lobby=True)

# Data Collect
g_dataCollector = None
try:
	from .data_collector import g_dataCollector
except ImportError:
	logger.error('datacollector broken')
if g_dataCollector:
	from gui.mods.mod_rmanager import __version__
	g_dataCollector.addSoloMod('replays_manager', __version__)

# Add missing battle result fields (creditsReplay, xpReply, freeXpReplay, goldReplay, fortResource, crystalReplay)
# See BattleReplay.py onBattleResultsReceived method

def makeIndex(paramIndex, paramSubIndex, secondParamIndex):
	if not ValueReplayConnector._bitCoder.checkFit(0, paramIndex):
		raise AssertionError
	if not ValueReplayConnector._bitCoder.checkFit(1, paramSubIndex):
		raise AssertionError
	if not ValueReplayConnector._bitCoder.checkFit(2, secondParamIndex):
		raise AssertionError
	return ValueReplayConnector._bitCoder.emplace(paramIndex, paramSubIndex, secondParamIndex)

def nameToIndex(name):
	return battle_results_config['allResults'].indexOf(name)

def makeStepCompDescr(operator, index):
	return (index << 4) + (operator & 15)

def pack(value):
	size = len(value)
	return struct.pack(('<H%sI' % size), size, *value)

def genCreditsReplay(results):
	replay = []
	replay.append(makeStepCompDescr(op.SET, makeIndex(nameToIndex('originalCredits'), 0, 0)))
	replay.append(makeStepCompDescr(op.MUL, makeIndex(nameToIndex('appliedPremiumCreditsFactor100'), 0, 0)))
	replay.append(makeStepCompDescr(op.SUBCOEFF, makeIndex(nameToIndex('originalCreditsPenalty'), 0,
															nameToIndex('appliedPremiumCreditsFactor100'))))
	replay.append(makeStepCompDescr(op.SUBCOEFF, makeIndex(nameToIndex('originalCreditsContributionOut'), 0,
															nameToIndex('appliedPremiumCreditsFactor100'))))
	replay.append(makeStepCompDescr(op.ADDCOEFF, makeIndex(nameToIndex('originalCreditsContributionIn'), 0,
															nameToIndex('appliedPremiumCreditsFactor100'))))
	replay.append(makeStepCompDescr(op.ADDCOEFF, makeIndex(nameToIndex('originalCreditsToDraw'), 0,
															nameToIndex('appliedPremiumCreditsFactor100'))))
	replay.append(makeStepCompDescr(op.TAG, makeIndex(nameToIndex('subtotalCredits'), 0, 0)))
	if 'premSquadCreditsFactor100' in results and results['premSquadCreditsFactor100'] != 0:
		replay.append(makeStepCompDescr(op.ADD, makeIndex(nameToIndex('originalPremSquadCredits'), 0, 0)))
		replay.append(makeStepCompDescr(op.SUBCOEFF, makeIndex(nameToIndex('originalCreditsPenaltySquad'), 0,
																nameToIndex('premSquadCreditsFactor100'))))
		replay.append(makeStepCompDescr(op.SUBCOEFF, makeIndex(nameToIndex('originalCreditsContributionOutSquad'), 0,
																nameToIndex('premSquadCreditsFactor100'))))
		replay.append(makeStepCompDescr(op.ADDCOEFF, makeIndex(nameToIndex('originalCreditsContributionInSquad'), 0,
																nameToIndex('premSquadCreditsFactor100'))))
		replay.append(makeStepCompDescr(op.ADDCOEFF, makeIndex(nameToIndex('originalCreditsToDrawSquad'), 0,
																nameToIndex('premSquadCreditsFactor100'))))
	if 'boosterCreditsFactor100' in results and results['boosterCreditsFactor100'] != 0:
		replay.append(makeStepCompDescr(op.FACTOR, makeIndex(nameToIndex('boosterCreditsFactor100'), 0, 0)))
	if results['eventCreditsList']:
		for x in range(len(results['eventCreditsList'])):
			replay.append(makeStepCompDescr(op.ADD, makeIndex(nameToIndex('eventCreditsList'), x + 1, 0)))
	return pack(replay)

def genXPReplay(results):
	replay = []
	replay.append(makeStepCompDescr(op.SET, makeIndex(nameToIndex('originalXP'), 0, 0)))
	replay.append(makeStepCompDescr(op.MUL, makeIndex(nameToIndex('appliedPremiumXPFactor100'), 0, 0)))
	replay.append(makeStepCompDescr(op.SUBCOEFF, makeIndex(nameToIndex('originalXPPenalty'), 0,
															nameToIndex('appliedPremiumXPFactor100'))))
	replay.append(makeStepCompDescr(op.TAG, makeIndex(nameToIndex('subtotalXP'), 0, 0)))
	if 'dailyXPFactor10' in results and results['dailyXPFactor10'] != 10:
		replay.append(makeStepCompDescr(op.MUL, makeIndex(nameToIndex('dailyXPFactor10'), 0, 0)))
		replay.append(makeStepCompDescr(op.FACTOR, makeIndex(nameToIndex('additionalXPFactor10'), 0, 0)))
	replay.append(makeStepCompDescr(op.FACTOR, makeIndex(nameToIndex('premiumVehicleXPFactor100'), 0, 0)))
	if 'squadXPFactor100' in results and results['squadXPFactor100'] != 0:
		replay.append(makeStepCompDescr(op.FACTOR, makeIndex(nameToIndex('squadXPFactor100'), 0, 0)))
	if 'boosterXPFactor100' in results and results['boosterXPFactor100'] != 0:
		replay.append(makeStepCompDescr(op.FACTOR, makeIndex(nameToIndex('boosterXPFactor100'), 0, 0)))
	if results['eventXPList']:
		for x in range(len(results['eventXPList'])):
			replay.append(makeStepCompDescr(op.ADD, makeIndex(nameToIndex('eventXPList'), x + 1, 0)))
	return pack(replay)

def genFreeXPReplay(results):
	replay = []
	replay.append(makeStepCompDescr(op.SET, makeIndex(nameToIndex('originalFreeXP'), 0, 0)))
	replay.append(makeStepCompDescr(op.MUL, makeIndex(nameToIndex('appliedPremiumXPFactor100'), 0, 0)))
	replay.append(makeStepCompDescr(op.TAG, makeIndex(nameToIndex('subtotalFreeXP'), 0, 0)))
	if 'dailyXPFactor10' in results and results['dailyXPFactor10'] != 10:
		replay.append(makeStepCompDescr(op.MUL, makeIndex(nameToIndex('dailyXPFactor10'), 0, 0)))
		replay.append(makeStepCompDescr(op.FACTOR, makeIndex(nameToIndex('additionalXPFactor10'), 0, 0)))
	if 'boosterFreeXPFactor100' in results and results['boosterFreeXPFactor100'] != 0:
		replay.append(makeStepCompDescr(op.FACTOR, makeIndex(nameToIndex('boosterFreeXPFactor100'), 0, 0)))
	if results['eventFreeXPList']:
		for x in range(len(results['eventFreeXPList'])):
			replay.append(makeStepCompDescr(op.ADD, makeIndex(nameToIndex('eventFreeXPList'), x + 1, 0)))
	return pack(replay)

def genGoldReplay(results):
	replay = []
	replay.append(makeStepCompDescr(op.SET, makeIndex(nameToIndex('originalGold'), 0, 0)))
	if results['eventGoldList']:
		for x in range(len(results['eventGoldList'])):
			replay.append(makeStepCompDescr(op.ADD, makeIndex(nameToIndex('eventGoldList'), x + 1, 0)))
	return pack(replay)

def genCrystalReplay(results):
	replay = []
	replay.append(makeStepCompDescr(op.SET, makeIndex(nameToIndex('originalCrystal'), 0, 0)))
	if results['eventCrystalList']:
		for x in range(len(results['eventCrystalList'])):
			replay.append(makeStepCompDescr(op.ADD, makeIndex(nameToIndex('eventCrystalList'), x + 1, 0)))
	return pack(replay)

def battle_royale_fix(results):
	if 'currencies' in results and 'brcoin' in results['currencies']:
		if not results['currencies']['brcoin']['replay']:
			del results['currencies']['brcoin']
	return results

@override(_EconomicsRecordsChains, "addResults")
def _EconomicsRecordsChains_addResults(baseMethod, baseObject, intCD, results):
	if 'creditsReplay' in results and not results['creditsReplay']:
		results['creditsReplay'] = genCreditsReplay(results)
	if 'goldReplay' in results and not results['goldReplay']:
		results['goldReplay'] = genGoldReplay(results)
	if 'xpReplay' in results and not results['xpReplay']:
		results['xpReplay'] = genXPReplay(results)
	if 'freeXPReplay' in results and not results['freeXPReplay']:
		results['freeXPReplay'] = genFreeXPReplay(results)
	if 'crystalReplay' in results and not results['crystalReplay']:
		results['crystalReplay'] = genCrystalReplay(results)

	# TODO replay value rebuild
	results = battle_royale_fix(results)

	return baseMethod(baseObject, intCD, results)

@override(BattleResultsService, "_BattleResultsService__postStatistics")
def _postStatistics(baseMethod, baseObject, reusableInfo, result):
	from . import g_controllers
	if g_controllers.actions.skip_statistics:
		return
	return baseMethod(baseObject, reusableInfo, result)
