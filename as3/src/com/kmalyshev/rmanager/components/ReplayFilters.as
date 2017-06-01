package com.kmalyshev.rmanager.components
{
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	import flash.text.TextFormat;
	
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.controls.ScrollingList;
	import scaleform.clik.core.UIComponent;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.events.ListEvent;
	
	import net.wg.gui.components.controls.DropDownImageText;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.gui.components.controls.CheckBox;
	import net.wg.gui.components.controls.DropdownMenu;
	
	import com.kmalyshev.rmanager.events.FilterEvent;
	import com.kmalyshev.rmanager.lang.STRINGS;
	import com.kmalyshev.rmanager.utils.Helpers;
	import com.kmalyshev.rmanager.utils.Logger;
	import com.kmalyshev.rmanager.utils.Utils;
	
	public class ReplayFilters extends UIComponent
	{
		
		public var title:TextField;
		public var mapLabel:TextField;
		public var mapsList:ScrollingList;
		
		public var vehicleLabel:TextField;
		public var vehicleNation:DropDownImageText;
		public var vehicleType:DropDownImageText;
		public var vehicleLevel:DropDownImageText;
		
		public var battleTypeLabel:TextField;
		public var battleType:DropdownMenu;
		
		public var battleResultLabel:TextField;		
		public var battleResult:DropdownMenu;
		
		public var otherLabel:TextField;
		public var cbFavorite:CheckBox;
		
		public var btnApply:SoundButton;
		public var btnReset:SoundButton;				
		
		private var _data:Object;
		private var _selectedTF:TextFormat;
		
		public function ReplayFilters()
		{
			super();
		}
		
		override protected function configUI():void
		{
			super.configUI();
			try
			{
				this._selectedTF = new TextFormat();
				this._selectedTF.color = 0xFFFFFF;
				
				this.title.text = STRINGS.l10n('ui.window.filterTab.title');
				this.mapLabel.text = STRINGS.l10n('ui.window.filterTab.map');
				this.vehicleLabel.text = STRINGS.l10n('ui.window.filterTab.vehicle');
				this.vehicleLabel.autoSize = TextFieldAutoSize.LEFT;
				this.battleTypeLabel.text = STRINGS.l10n('ui.window.filterTab.battleType');
				
				Helpers.ConfigureMapsList(this.mapsList);
				this.mapsList.addEventListener(ListEvent.INDEX_CHANGE, this.handleMapsListIndexChange);
				
				Helpers.ConfigureVehicleNationsDropdown(this.vehicleNation);
				
				Helpers.ConfigureVehicleLevelsDropdown(this.vehicleLevel);
				
				Helpers.ConfigureVehicleTypesDropdown(this.vehicleType);
				//this.vehicleType.addEventListener(ListEvent.INDEX_CHANGE, this.handleVehicleTypeIndexChange);
				
				Helpers.ConfigureBattleTypeDropdown(this.battleType);				
				this.battleType.addEventListener(ListEvent.INDEX_CHANGE, this.handleBattleTypeIndexChange);
				this.battleType.selectedIndex = 0;
				
				this.battleResultLabel.text = STRINGS.l10n('ui.window.filterTab.battleResult');
				Helpers.ConfigureBattleResultDropdown(this.battleResult);
				this.battleResult.addEventListener(ListEvent.INDEX_CHANGE, this.handleBattleResultIndexChange);
				this.battleResult.selectedIndex = 0;
				
				this.otherLabel.text = STRINGS.l10n('ui.window.filterTab.otherLabel');
				this.cbFavorite.label = STRINGS.l10n('ui.window.filterTab.otherShowFavorite');
				
				this.btnApply.width = 235;
				this.btnApply.label = STRINGS.l10n('ui.window.buttonApply');
				this.btnApply.addEventListener(ButtonEvent.CLICK, this.handleBtnApplyClick);
				
				this.btnReset.width = 235;
				this.btnReset.label = STRINGS.l10n('ui.window.buttonReset');
				this.btnReset.addEventListener(ButtonEvent.CLICK, this.handleBtnResetClick);				
			}
			catch (err:Error)
			{
				Logger.Error("ReplayFilters::configUI " + err.getStackTrace());
			}
		}
		
		override protected function onDispose():void
		{
			this.mapsList.dataProvider.cleanUp();
			this.mapsList = null;
			this.vehicleLevel.dataProvider.cleanUp();
			this.vehicleLevel = null;
			this.vehicleNation.dataProvider.cleanUp();
			this.vehicleNation = null;
			this.vehicleType.dataProvider.cleanUp();
			this.vehicleType = null;
			this.battleType.removeEventListener(ListEvent.INDEX_CHANGE, this.handleBattleTypeIndexChange);
			this.battleType = null;
			this.btnApply.removeEventListener(ButtonEvent.CLICK, this.handleBtnApplyClick);
			this.btnApply = null;
			this.btnReset.removeEventListener(ButtonEvent.CLICK, this.handleBtnResetClick);
			this.btnReset = null;
			this._data = null;
			
			super.onDispose();
		}
		
		override protected function draw():void
		{
			super.draw();
			if (isInvalid(InvalidationType.DATA))
			{
				var mapsData:DataProvider = new DataProvider(this._data.maps);
				mapsData.unshift({label: STRINGS.l10n('ui.window.filterTab.mapAll'), data: ""});
				this.mapsList.dataProvider = mapsData;
				this.mapsList.validateNow();
				this.mapsList.rowCount = 6;
			}
		}
		
		protected function handleBtnApplyClick(event:ButtonEvent):void
		{
			this.dispatchFiltersData();
		}
		
		protected function handleBtnResetClick(event:ButtonEvent):void
		{
			this.mapsList.selectedIndex = 0;
			this.vehicleNation.selectedIndex = 0;
			this.vehicleLevel.selectedIndex = 0;
			this.vehicleType.selectedIndex = 0;
			this.battleType.selectedIndex = 0;
			this.battleResult.selectedIndex = 0;
			this.cbFavorite.selected = false;
			//this.dispatchFiltersData();
		}
		
		protected function handleBattleResultIndexChange(event:ListEvent):void
		{
			var startBlock:String = STRINGS.l10n('ui.window.filterTab.battleResult') + "  ";
			this.battleResultLabel.text = startBlock + event.itemData.label;
			this.battleResultLabel.setTextFormat(this._selectedTF, startBlock.length);
		}
		
		protected function handleMapsListIndexChange(event:ListEvent):void
		{
			var startBlock:String = STRINGS.l10n('ui.window.filterTab.map') + "  ";
			this.mapLabel.text = startBlock + event.itemData.label;
			this.mapLabel.setTextFormat(this._selectedTF, startBlock.length);
		}
		
		protected function handleBattleTypeIndexChange(event:ListEvent):void
		{
			var startBlock:String = STRINGS.l10n('ui.window.filterTab.battleType') + "  ";
			this.battleTypeLabel.text = startBlock + event.itemData.label;
			this.battleTypeLabel.setTextFormat(this._selectedTF, startBlock.length);
		}
		
		private function dispatchFiltersData():void
		{
			var data:Object = {
				mapName: Utils.getDataFromList(this.mapsList),
				isWinner: Utils.getDataFromList(this.battleResult),
				tankInfo: {
					vehicleNation: Utils.getDataFromList(this.vehicleNation), 
					vehicleLevel: Utils.getDataFromList(this.vehicleLevel), 
					vehicleType: Utils.getDataFromList(this.vehicleType)
				}, 
				battleType: Utils.getDataFromList(this.battleType), 
				favorite: this.cbFavorite.selected ? 1 : -1
			};
			dispatchEvent(new FilterEvent(FilterEvent.FILTERS_CHANGED, data));
		}
		
		public function setData(data:Object):void
		{
			if (data != null)
			{
				this._data = data;
				this.invalidate(InvalidationType.DATA);
			}
		}
	
	}

}
