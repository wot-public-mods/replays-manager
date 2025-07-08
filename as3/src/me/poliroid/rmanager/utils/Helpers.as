package me.poliroid.rmanager.utils
{
	import scaleform.clik.controls.ScrollingList;
	import scaleform.clik.constants.DirectionMode;
	import scaleform.clik.data.DataProvider;
	
	import net.wg.gui.components.advanced.ViewStack;
	import net.wg.gui.components.advanced.ContentTabBar;
	import net.wg.gui.components.controls.DropDownImageText;
	import net.wg.gui.components.controls.DropdownMenu;
	import net.wg.gui.cyberSport.controls.CSVehicleButton;
	
	import me.poliroid.rmanager.components.LabelButtonBar;
	import me.poliroid.rmanager.lang.STRINGS;
	import me.poliroid.rmanager.ui.ReplayItemRendererUI;
	
	public class Helpers
	{
		public static var apiStatus:Boolean = false;

		public static const REPLAYS:String = "me.poliroid.rmanager.ui.ReplaysViewUI";
		public static const REPLAY_CM_HANDLER_TYPE:String = "replayCMHandler";

		public static const SORTING_BUTTONS:Array = [
			{label: STRINGS.l10n('ui.window.sorting.byTime'), selected: true, ascending: false, key: "timestamp"},
			{label: STRINGS.l10n('ui.window.sorting.byCredits'), selected: false, ascending: false, key: "credits"},
			{label: STRINGS.l10n('ui.window.sorting.byXp'), selected: false, ascending: false, key: "xp"},
			{label: STRINGS.l10n('ui.window.sorting.byKills'), selected: false, ascending: false, key: "kills"},
			{label: STRINGS.l10n('ui.window.sorting.byDamage'), selected: false, ascending: false, key: "damage"},
			{label: STRINGS.l10n('ui.window.sorting.bySpotted'), selected: false, ascending: false, key: "spotted"},
			{label: STRINGS.l10n('ui.window.sorting.byAssist'), selected: false, ascending: false, key: "assist"}
		];
		public static const DATE_BUTTONS:Array = [
			{label: STRINGS.l10n('ui.window.dateFilter.today'), selected: false, key: "today"},
			{label: STRINGS.l10n('ui.window.dateFilter.week'), selected: false, key: "week"},
			{label: STRINGS.l10n('ui.window.dateFilter.month'), selected: false, key: "month"},
			{label: STRINGS.l10n('ui.window.dateFilter.allTime'), selected: true, key: "all"}
		];
		public static const VEHICLE_TYPES:Array = [
			{label: STRINGS.l10n('ui.window.filterTab.vehicleTypeAll'), data: "", icon: "../maps/icons/filters/tanks/all.png"}, 
			{label: STRINGS.l10n('ui.window.filterTab.vehicleTypeHeavy'), data: "heavyTank", icon: "../maps/icons/filters/tanks/heavyTank.png"}, 
			{label: STRINGS.l10n('ui.window.filterTab.vehicleTypeMedium'), data: "mediumTank", icon: "../maps/icons/filters/tanks/mediumTank.png"}, 
			{label: STRINGS.l10n('ui.window.filterTab.vehicleTypeLight'), data: "lightTank", icon: "../maps/icons/filters/tanks/lightTank.png"}, 
			{label: STRINGS.l10n('ui.window.filterTab.vehicleTypeATSPG'), data: "AT-SPG", icon: "../maps/icons/filters/tanks/AT-SPG.png"}, 
			{label: STRINGS.l10n('ui.window.filterTab.vehicleTypeSPG'), data: "SPG", icon: "../maps/icons/filters/tanks/SPG.png"}
		];
		public static const BATTLE_RESULT:Array = [
			{label: STRINGS.l10n('ui.window.filterTab.any'), data: -100}, 
			{label: STRINGS.l10n('ui.window.battleResultVictory'), data: 1}, 
			{label: STRINGS.l10n('ui.window.battleResultDefeat'), data: 0}, 
			{label: STRINGS.l10n('ui.window.battleResultDraw'), data: -5}
		];

		public function Helpers()
		{
			return;
		}
		
		public static function ConfigureReplaysScrollingList(list:ScrollingList):void
		{
			list.width = 703;
			list.enabled = true;
			list.visible = true;
			list.itemRenderer = ReplayItemRendererUI;
			list.itemRendererInstanceName = "";
			list.margin = 0;
			list.rowHeight = 118;
			list.rowCount = 5;
			list.scrollBar = "ScrollBar";
			list.scrollPosition = 0;
		}
		
		public static function ConfigureSortingMenu(list:LabelButtonBar):void
		{
			list.label = STRINGS.l10n('ui.window.sorting.label');
			list.direction = DirectionMode.HORIZONTAL;
			list.itemRendererName = "me.poliroid.rmanager.ui.TextLinkSortButtonUI";
			list.spacing = 5;
			list.autoSize = "left";
		}
		
		public static function ConfigureDateFilterMenu(list:LabelButtonBar):void
		{
			list.label = STRINGS.l10n('ui.window.dateFilter.label');
			list.direction = DirectionMode.HORIZONTAL;
			list.itemRendererName = "me.poliroid.rmanager.ui.TextLinkButtonUI";
			list.spacing = 5;
			list.autoSize = "left";
		}
		
		public static function ConfigureViewStack(view:ViewStack):void
		{
			view.cache = true;
			view.enabled = true;
			view.enableInitCallback = false;
			view.visible = true;
		}
		
		public static function ConfigureTabsBar(tabs:LabelButtonBar):void
		{
			tabs.autoSize = "right";
			tabs.direction = "horizontal";
			tabs.enabled = true;
			tabs.enableInitCallback = false;
			tabs.focusable = false;
			tabs.itemRendererName = "TabButton";
			tabs.spacing = 0;
			tabs.visible = true;
		}
		
		public static function ConfigureContentTabBar(tabs:ContentTabBar):void
		{
			tabs.autoSize = "none";
			tabs.buttonWidth = 0;
			tabs.centerTabs = true;
			tabs.direction = "horizontal";
			tabs.enabled = true;
			tabs.enableInitCallback = false;
			tabs.focusable = false;
			tabs.itemRendererName = "ContentTabRendererUI";
			tabs.minRendererWidth = 110;
			tabs.paddingHorizontal = 0;
			tabs.showSeparator = false;
			tabs.spacing = 0;
			tabs.textPadding = 0;
			tabs.visible = true;
			tabs.focusable = false;
		}
		
		public static function ConfigureMapsList(list:ScrollingList):void
		{
			list.width = 235;
			list.focusable = false;
			list.itemRenderer = App.utils.classFactory.getClass("DropDownListItemRendererSound");
			list.itemRendererInstanceName = "";
			list.scrollBar = "ScrollBar";
			list.selectedIndex = 0;
		}
		
		public static function ConfigureVehicleNationsDropdown(menu:DropDownImageText):void
		{
			var _nationsData:Array = App.utils.nations.getNationsData();
			var _fn:Array = [{label: STRINGS.l10n('ui.window.filterTab.all'), data: -1, icon: "../maps/icons/filters/nations/all.png"}];
			var i:uint = 0;
			while (i < _nationsData.length)
			{
				_nationsData[i]["icon"] = "../maps/icons/filters/nations/" + App.utils.nations.getNationName(_nationsData[i]["data"]) + ".png";
				_fn.push(_nationsData[i]);
				i = i + 1;
			}
			menu.focusable = false;
			menu.menuWidth = 150;
			menu.itemRenderer = "ListItemRedererImageText";
			menu.dropdown = "DropdownMenu_ScrollingList";
			menu.rowCount = _fn.length;
			menu.dataProvider = new DataProvider(_fn);
			menu.selectedIndex = 0;
			menu.validateNow();
		}
		
		public static function ConfigureVehicleTypesDropdown(menu:DropDownImageText):void
		{
			menu.focusable = false;
			menu.menuWidth = 150;
			menu.itemRenderer = "ListItemRedererImageText";
			menu.dropdown = "DropdownMenu_ScrollingList";
			menu.rowCount = VEHICLE_TYPES.length;
			menu.dataProvider = new DataProvider(VEHICLE_TYPES);
			menu.selectedIndex = 0;
			menu.validateNow();
		}
		
		public static function ConfigureVehicleLevelsDropdown(menu:DropDownImageText):void
		{
			var _fl:Array = new Array();
			_fl.push({label: STRINGS.l10n('ui.window.filterTab.all'), data: -1, icon: "../maps/icons/filters/levels/level_all.png"});
			for (var i:uint = 1; i <= 10; i++)
			{
				_fl.push({label: i + " " + STRINGS.l10n('ui.window.filterTab.vehicleLevel'), data: i, icon: "../maps/icons/filters/levels/level_" + i + ".png"});
			}
			
			menu.focusable = false;
			menu.menuWidth = 150;
			menu.itemRenderer = "ListItemRedererImageText";
			menu.dropdown = "DropdownMenu_ScrollingList";
			menu.rowCount = _fl.length;
			menu.dataProvider = new DataProvider(_fl);
			menu.selectedIndex = 0;
			menu.validateNow();
		}
		
		public static function ConfigureBattleTypeDropdown(menu:DropdownMenu):void
		{
			menu.focusable = false;
			menu.itemRenderer = "DropDownListItemRendererSound";
			menu.dropdown = "DropdownMenu_ScrollingList";
			menu.width = 235;
			menu.selectedIndex = -1;
			menu.validateNow();
		}
		
		public static function ConfigureBattleResultDropdown(menu:DropdownMenu):void
		{			
			menu.focusable = false;
			menu.itemRenderer = "DropDownListItemRendererSound";
			menu.dropdown = "DropdownMenu_ScrollingList";
			menu.rowCount = BATTLE_RESULT.length;
			menu.dataProvider = new DataProvider(BATTLE_RESULT);
			menu.width = 235;
			menu.selectedIndex = -1;
			menu.validateNow();
		}
		
		public static function ConfigureVehicleButton(btn:CSVehicleButton):void
		{
			btn.enabled = false;
		}
	}

}