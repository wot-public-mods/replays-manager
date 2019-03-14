package com.kmalyshev.rmanager.utils
{
	import scaleform.clik.controls.ScrollingList;
	import scaleform.clik.constants.DirectionMode;
	import scaleform.clik.data.DataProvider;
	
	import net.wg.gui.components.advanced.ViewStack;
	import net.wg.gui.components.advanced.ContentTabBar;
	import net.wg.gui.components.controls.DropDownImageText;
	import net.wg.gui.components.controls.DropdownMenu;
	import net.wg.gui.cyberSport.controls.CSVehicleButton;
	
	import com.kmalyshev.rmanager.components.LabelButtonBar;
	import com.kmalyshev.rmanager.lang.STRINGS;
	import com.kmalyshev.rmanager.ui.ReplayItemRendererUI;
	
	public class Helpers
	{
		public static var WOTREPLAYS_API_STATUS:Boolean = false;
		public static var REPLAYS:String = "com.kmalyshev.rmanager.ui.ReplaysViewUI";
		public static var REPLAY_CM_HANDLER_TYPE:String = "replayCMHandler";
		
		public static const SORTING_BUTTONS:Array = [
			{label: STRINGS.RMANAGER_SORTING_BY_TIME, selected: true, ascending: false, key: "timestamp"}, 
			{label: STRINGS.RMANAGER_SORTING_BY_CREDITS, selected: false, ascending: false, key: "credits"},
			{label: STRINGS.RMANAGER_SORTING_BY_XP, selected: false, ascending: false, key: "xp"}, 
			{label: STRINGS.RMANAGER_SORTING_BY_KILLS, selected: false, ascending: false, key: "kills"},
			{label: STRINGS.RMANAGER_SORTING_BY_DAMAGE, selected: false, ascending: false, key: "damage"}, 			
			{label: STRINGS.RMANAGER_SORTING_BY_SPOTTED, selected: false, ascending: false, key: "spotted"}, 
			{label: STRINGS.RMANAGER_SORTING_BY_ASSIST, selected: false, ascending: false, key: "damageAssistedRadio"}
		];
		
		public static const DATE_BUTTONS:Array = [{label: STRINGS.RMANAGER_DATE_FILTER_TODAY, selected: false, key: "today"}, {label: STRINGS.RMANAGER_DATE_FILTER_WEEK, selected: false, key: "week"}, {label: STRINGS.RMANAGER_DATE_FILTER_MONTH, selected: false, key: "month"}, {label: STRINGS.RMANAGER_DATE_FILTER_ALL_TIME, selected: true, key: "all"}];		
		public static const VEHICLE_TYPES:Array = [{label: STRINGS.RMANAGER_FILTER_TAB_VEHICLE_TYPE_ALL, data: "", icon: "../maps/icons/filters/tanks/all.png"}, {label: STRINGS.RMANAGER_FILTER_TAB_VEHICLE_TYPE_HEAVY, data: "heavyTank", icon: "../maps/icons/filters/tanks/heavyTank.png"}, {label: STRINGS.RMANAGER_FILTER_TAB_VEHICLE_TYPE_MEDIUM, data: "mediumTank", icon: "../maps/icons/filters/tanks/mediumTank.png"}, {label: STRINGS.RMANAGER_FILTER_TAB_VEHICLE_TYPE_LIGHT, data: "lightTank", icon: "../maps/icons/filters/tanks/lightTank.png"}, {label: STRINGS.RMANAGER_FILTER_TAB_VEHICLE_TYPE_AT_SPG, data: "AT-SPG", icon: "../maps/icons/filters/tanks/AT-SPG.png"}, {label: STRINGS.RMANAGER_FILTER_TAB_VEHICLE_TYPE_SPG, data: "SPG", icon: "../maps/icons/filters/tanks/SPG.png"}];
		public static const BATTLE_RESULT:Array = [
			{label: STRINGS.RMANAGER_FILTER_TAB_ANY, data: -100}, 
			{label: STRINGS.RMANAGER_BATTLE_RESULT_VICTORY, data: 1}, 
			{label: STRINGS.RMANAGER_BATTLE_RESULT_DEFEAT, data: 0}, 
			{label: STRINGS.RMANAGER_BATTLE_RESULT_DRAW, data: -5}
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
			list.label = STRINGS.RMANAGER_SORTING_LABEL;
			list.direction = DirectionMode.HORIZONTAL;
			list.itemRendererName = "com.kmalyshev.rmanager.ui.TextLinkSortButtonUI";
			list.spacing = 5;
			list.autoSize = "left";
		}
		
		public static function ConfigureDateFilterMenu(list:LabelButtonBar):void
		{
			list.label = STRINGS.RMANAGER_DATE_FILTER_LABEL;
			list.direction = DirectionMode.HORIZONTAL;
			list.itemRendererName = "com.kmalyshev.rmanager.ui.TextLinkButtonUI";
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
			var _nations:* = App.utils.nations;
			var _nationsData:Array = _nations.getNationsData();
			var _fn:Array = [{label: STRINGS.RMANAGER_FILTER_TAB_ALL, data: -1, icon: "../maps/icons/filters/nations/all.png"}];
			var i:uint = 0;
			while (i < _nationsData.length)
			{
				_nationsData[i]["icon"] = "../maps/icons/filters/nations/" + _nations.getNationName(_nationsData[i]["data"]) + ".png";
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
			_fl.push({label: STRINGS.RMANAGER_FILTER_TAB_ALL, data: -1, icon: "../maps/icons/filters/levels/level_all.png"});
			for (var i:uint = 1; i <= 10; i++)
			{
				_fl.push({label: i + " " + STRINGS.RMANAGER_FILTER_TAB_VEHICLE_LEVEL, data: i, icon: "../maps/icons/filters/levels/level_" + i + ".png"});
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
			var _fl:Array = new Array();
			_fl.push({label: STRINGS.RMANAGER_FILTER_TAB_ALL, data: -1});
			for (var i:int = 0; i < MENU.LOADING_BATTLETYPES_ENUM.length; i++)
			{
				var labelText:String = Utils.getBattleTypeLocalString(i.toString());
				if(labelText != "") {
					_fl.push({label: labelText, data: i});
				}				
			}
			
			menu.focusable = false;
			menu.itemRenderer = "DropDownListItemRendererSound";
			menu.dropdown = "DropdownMenu_ScrollingList";
			menu.rowCount = _fl.length;
			menu.dataProvider = new DataProvider(_fl);
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