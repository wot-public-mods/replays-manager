
from BattleReplay import BattleReplay
import BigWorld
from gui.app_loader.loader import g_appLoader, _AppLoader
from gui.app_loader.settings import APP_NAME_SPACE
from gui.lobby_context import LobbyContext
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import AppealCMHandler, USER
from gui.Scaleform.daapi.view.login.LoginView import LoginView
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils.requesters.ItemsRequester import ItemsRequester
from helpers.server_settings import _ClanProfile, RoamingSettings, _SpgRedesignFeatures
from debug_utils import LOG_DEBUG, LOG_ERROR
from Event import Event

from gui.modsListApi import g_modsListApi

from gui.rmanager import __version__
from gui.rmanager.events import g_eventsManager
from gui.rmanager.lang import l10n
from gui.rmanager.utils import override
from gui.rmanager.rmanager_constants import  REPLAYS_MANAGER_WINDOW_ALIAS

__all__ = ( )

# adding menu item to modslist
def showManager():
	"""fire load popover view on button click"""
	app = g_appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
	if not app:
		return
	app.loadView(SFViewLoadParams(REPLAYS_MANAGER_WINDOW_ALIAS), {})

g_modsListApi.addModification(id = 'rmanager', name = l10n('modsListApi.name'), description = l10n('modsListApi.description'), \
	enabled = True, callback = showManager, login = True, lobby = True, icon = 'gui/maps/rmanager/modsListApi.png' )


# app finished
@override(_AppLoader, 'fini')
def hooked_fini(baseMethod, baseObject):
	g_eventsManager.onAppFinish()
	baseMethod(baseObject)

# app login populated
@override(LoginView, '_populate')
def populate(baseMethod, baseObject):
	baseMethod(baseObject)
	g_eventsManager.onLoginViewLoaded()

# context menu fixes
@override(LobbyContext, 'getPlayerFullName')
def getPlayerFullName(baseMethod, baseObject, pName, clanInfo = None, clanAbbrev = None, regionCode = None, pDBID = None):
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
def getOptions(baseMethod, baseObject, ctx = None):
	if baseObject.prbDispatcher:
		options = baseMethod(baseObject, ctx)
		return options
	else:
		options = [ baseObject._makeItem(USER.COPY_TO_CLIPBOARD, MENU.contextmenu(USER.COPY_TO_CLIPBOARD)) , 
					baseObject._makeItem(USER.VEHICLE_INFO, MENU.contextmenu(USER.VEHICLE_INFO)) ]
		return options


# track stat
from gui.rmanager.data_collector import g_dataCollector
g_dataCollector.addSoloMod('replays_manager', __version__)


from gui.game_control.epic_meta_game_ctrl import EpicBattleMetaGameController
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







# Add missing battle result fields (creditsReplay, xpReply, freeXpReplay, goldReplay, fortResource, crystalReplay)
# See BattleReplay.py onBattleResultsReceived method

import struct
from battle_results_shared import VEH_FULL_RESULTS
from ValueReplay import ValueReplay, ValueReplayConnector
from gui.battle_results.reusable.personal import _EconomicsRecordsChains

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

def genCreditsReplay(results = {}):
	replay = []
	replay.append(makeStepCompDescr(ValueReplay.SET, makeIndex(nameToIndex('originalCredits'), 0, 0)))
	if 'appliedPremiumCreditsFactor10' in results and results['appliedPremiumCreditsFactor10'] != 10:
		replay.append(makeStepCompDescr(ValueReplay.MUL, makeIndex(nameToIndex('appliedPremiumCreditsFactor10'), 0, 0)))
	replay.append(makeStepCompDescr(ValueReplay.SUBCOEFF, makeIndex(nameToIndex('originalCreditsPenalty'), 0, nameToIndex('squadXPFactor100'))))
	replay.append(makeStepCompDescr(ValueReplay.SUBCOEFF, makeIndex(nameToIndex('originalCreditsContributionOut'), 0, nameToIndex('squadXPFactor100'))))
	replay.append(makeStepCompDescr(ValueReplay.ADDCOEFF, makeIndex(nameToIndex('originalCreditsContributionIn'), 0, nameToIndex('appliedPremiumCreditsFactor10'))))
	replay.append(makeStepCompDescr(ValueReplay.TAG, makeIndex(nameToIndex('subtotalCredits'), 0, 0)))
	if 'boosterCreditsFactor100' in results and results['boosterCreditsFactor100'] != 0:
		replay.append(makeStepCompDescr(ValueReplay.FACTOR, makeIndex(nameToIndex('boosterCreditsFactor100'), 0, 0)))
	return pack(replay)

def genXPReplay(results = {}):
	replay = []
	replay.append(makeStepCompDescr(ValueReplay.SET, makeIndex(nameToIndex('originalXP'), 0, 0)))
	if 'appliedPremiumXPFactor10' in results and results['appliedPremiumXPFactor10'] != 10:
		replay.append(makeStepCompDescr(ValueReplay.MUL, makeIndex(nameToIndex('appliedPremiumXPFactor10'), 0, 0)))
	replay.append(makeStepCompDescr(ValueReplay.SUBCOEFF, makeIndex(nameToIndex('originalXPPenalty'), 0, nameToIndex('premiumVehicleXPFactor100'))))
	replay.append(makeStepCompDescr(ValueReplay.TAG, makeIndex(nameToIndex('subtotalXP'), 0, 0)))
	if 'dailyXPFactor10' in results and results['dailyXPFactor10'] != 10:
		replay.append(makeStepCompDescr(ValueReplay.MUL, makeIndex(nameToIndex('dailyXPFactor10'), 0, 0)))
	replay.append(makeStepCompDescr(ValueReplay.FACTOR, makeIndex(nameToIndex('premiumVehicleXPFactor100'), 0, 0)))
	if 'boosterXPFactor100' in results and results['boosterXPFactor100'] != 0:
		replay.append(makeStepCompDescr(ValueReplay.FACTOR, makeIndex(nameToIndex('boosterXPFactor100'), 0, 0)))
	return pack(replay)

def genFreeXPReplay(results = {}):
	replay = []
	replay.append(makeStepCompDescr(ValueReplay.SET, makeIndex(nameToIndex('originalFreeXP'), 0, 0)))
	if 'appliedPremiumXPFactor10' in results and results['appliedPremiumXPFactor10'] != 10:
		replay.append(makeStepCompDescr(ValueReplay.MUL, makeIndex(nameToIndex('appliedPremiumXPFactor10'), 0, 0)))
	replay.append(makeStepCompDescr(ValueReplay.TAG, makeIndex(nameToIndex('subtotalFreeXP'), 0, 0)))
	if 'dailyXPFactor10' in results and results['dailyXPFactor10'] != 10:
		replay.append(makeStepCompDescr(ValueReplay.MUL, makeIndex(nameToIndex('dailyXPFactor10'), 0, 0)))
	if 'boosterFreeXPFactor100' in results and results['boosterFreeXPFactor100'] != 0:
		replay.append(makeStepCompDescr(ValueReplay.FACTOR, makeIndex(nameToIndex('boosterFreeXPFactor100'), 0, 0)))
	return pack(replay)

def genGoldReplay(results = {}):
	replay = []
	replay.append(makeStepCompDescr(ValueReplay.SET, makeIndex(nameToIndex('originalGold'), 0, 0)))
	return pack(replay)

def genFortResourceReplay(results = {}):
	replay = []
	replay.append(makeStepCompDescr(ValueReplay.SET, makeIndex(nameToIndex('originalFortResource'), 0, 0)))
	replay.append(makeStepCompDescr(ValueReplay.TAG, makeIndex(nameToIndex('subtotalFortResource'), 0, 0)))
	return pack(replay)

def genCrystalReplay(results = {}):
	replay = []
	replay.append(makeStepCompDescr(ValueReplay.SET, makeIndex(nameToIndex('originalCrystal'), 0, 0)))
	return pack(replay)

@override(_EconomicsRecordsChains, "_addMoneyResults")
def _EconomicsRecordsChains_addMoneyResults(baseMethod, baseObject, connector, results):
	if 'creditsReplay' in results and not results['creditsReplay']:
		results['creditsReplay'] = genCreditsReplay(results)
	if 'goldReplay' in results and not results['goldReplay']:
		results['goldReplay'] = genGoldReplay(results)
	if 'originalCreditsToDraw' not in results:
		results['originalCreditsToDraw'] = results['creditsToDraw']
	return baseMethod(baseObject, connector, results)

@override(_EconomicsRecordsChains, "_addXPResults")
def _EconomicsRecordsChains_addXPResults(baseMethod, baseObject, connector, results):
	if 'xpReplay' in results and not results['xpReplay']:
		results['xpReplay'] = genXPReplay(results)
	if 'freeXPReplay' in results and not results['freeXPReplay']:
		results['freeXPReplay'] = genFreeXPReplay(results)
	return baseMethod(baseObject, connector, results)

@override(_EconomicsRecordsChains, "_addCrystalResults")
def _EconomicsRecordsChains_addCrystalResults(baseMethod, baseObject, connector, results):
	if 'crystalReplay' in results and not results['crystalReplay']:
		results['crystalReplay'] = genCrystalReplay(results)
	return baseMethod(baseObject, connector, results)

#@override(_EconomicsRecordsChains, "_addFortResourceResults")
#def _EconomicsRecordsChains_addFortResourceResults(baseMethod, baseObject, connector, results):
#	if 'fortResourceReplay' in results and not results['fortResourceReplay']:
#		results['fortResourceReplay'] = genFortResourceReplay(results)
#	return baseMethod(baseObject, connector, results)
