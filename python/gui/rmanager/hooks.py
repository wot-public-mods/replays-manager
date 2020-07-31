
import struct

from ValueReplay import ValueReplay as op, ValueReplayConnector
import BigWorld
from Account import PlayerAccount
from battle_results_shared import VEH_FULL_RESULTS
from debug_utils import LOG_ERROR
from gui.shared.personality import ServicesLocator
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_results.reusable.personal import _EconomicsRecordsChains
from gui.battle_results.service import BattleResultsService
from gui.game_control.epic_meta_game_ctrl import EpicBattleMetaGameController
from gui.lobby_context import LobbyContext
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import AppealCMHandler, USER
from gui.Scaleform.daapi.view.login.LoginView import LoginView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils.requesters.ItemsRequester import ItemsRequester
from gui.rmanager.events import g_eventsManager
from gui.rmanager.lang import l10n
from gui.rmanager.utils import override
from gui.rmanager.rmanager_constants import  REPLAYS_MANAGER_WINDOW_ALIAS

__all__ = ()

def showManager():
	"""fire load popover view on button click"""
	app = ServicesLocator.appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(REPLAYS_MANAGER_WINDOW_ALIAS), {})

# app login populated
@override(LoginView, '_populate')
def populate(baseMethod, baseObject):
	baseMethod(baseObject)
	g_eventsManager.onLoginViewLoaded()

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
	except: #NOSONAR
		return 0

@override(AppealCMHandler, 'getOptions')
def getOptions(baseMethod, baseObject, ctx=None):
	options = []
	if baseObject.prbDispatcher:
		options.extend(baseMethod(baseObject, ctx))
	else:
		options.extend([
			baseObject._makeItem(USER.COPY_TO_CLIPBOARD, MENU.contextmenu(USER.COPY_TO_CLIPBOARD)),
			baseObject._makeItem(USER.VEHICLE_INFO, MENU.contextmenu(USER.VEHICLE_INFO))
		])
	return options

# modsListApi
g_modsListApi = None
try:
	from gui.modsListApi import g_modsListApi
except ImportError:
	LOG_ERROR('modsListApi not installed')
if g_modsListApi:
	g_modsListApi.addModification(id='rmanager', name=l10n('modsListApi.name'), enabled=True,
		description=l10n('modsListApi.description'), icon='gui/maps/rmanager/modsListApi.png',
		callback=showManager, login=True, lobby=True)

# Data Collect
g_dataCollector = None
try:
	from gui.rmanager import __version__
	from gui.rmanager.data_collector import g_dataCollector
except ImportError:
	LOG_ERROR('datacollector broken')
if g_dataCollector:
	g_dataCollector.addSoloMod('replays_manager', __version__)


@override(EpicBattleMetaGameController, '_EpicBattleMetaGameController__showBattleResults')
def __showBattleResults(baseMethod, baseObject, reusableInfo, composer):
	arenaBonusType = reusableInfo.common.arenaBonusType
	arenaUniqueID = reusableInfo.arenaUniqueID

	if not hasattr(baseObject, '_arenaBattleResultsWasShown'):
		baseObject._arenaBattleResultsWasShown = set()

	if arenaUniqueID not in baseObject._arenaBattleResultsWasShown:
		baseObject._arenaBattleResultsWasShown.add(arenaUniqueID)
		from constants import ARENA_BONUS_TYPE
		from gui.shared import event_dispatcher
		if arenaBonusType == ARENA_BONUS_TYPE.EPIC_BATTLE:
			event_dispatcher.showEpicBattlesAfterBattleWindow(reusableInfo)

# this one for open replays result window in login space
# its not the best solution, but its work
# one of solutions was remove replaysmanager from lign window
from gui.battle_results.components.personal import PremiumInfoBlock
@override(PremiumInfoBlock, 'getVO')
def __getVO(baseMethod, baseObject):
	if BigWorld.player() is None:
		class FakePlayer:
			def isInBattleQueue(self):
				return False
		realBWPlayer = BigWorld.player
		BigWorld.player = FakePlayer
		base = baseMethod(baseObject)
		BigWorld.player = realBWPlayer
	else:
		base =  baseMethod(baseObject)
	return base

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
	return VEH_FULL_RESULTS.indexOf(name)

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
	return baseMethod(baseObject, intCD, results)

@override(BattleResultsService, "_BattleResultsService__postStatistics")
def _postStatistics(baseMethod, baseObject, reusableInfo, result):
	playerAccount = BigWorld.player()
	if playerAccount is None or not isinstance(playerAccount, PlayerAccount):
		return
	return baseMethod(baseObject, reusableInfo, result)
