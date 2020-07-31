package com.kmalyshev.rmanager.components
{	
	import flash.display.MovieClip;
	import flash.display.InteractiveObject;
	
	import flash.events.MouseEvent;
	
	import scaleform.clik.controls.ScrollingList;
	import scaleform.clik.core.UIComponent;
	import scaleform.clik.events.ListEvent;
	import scaleform.clik.events.IndexEvent;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.motion.Tween;
	
	import net.wg.gui.components.controls.BlackButton;
	import net.wg.infrastructure.interfaces.IViewStackContent;
	
	import com.kmalyshev.rmanager.lang.STRINGS;
	import com.kmalyshev.rmanager.events.PagingEvent;
	import com.kmalyshev.rmanager.events.SortingEvent;
	import com.kmalyshev.rmanager.events.FilterEvent;
	import com.kmalyshev.rmanager.utils.Helpers;
	
	public class ReplaysView extends UIComponent implements IViewStackContent
	{
		
		public var replaysList:ScrollingList;
		public var sortingButtonBar:LabelButtonBar;
		public var dateFilterButtonBar:LabelButtonBar;
		public var paginator:Paginator;
		public var replayInfo:ReplayInfo;
		public var replayFilters:ReplayFilters;
		public var debug:MovieClip;
		
		public var btnFilters:BlackButton;
		
		private var _filtersToggle:Boolean = false;
		
		protected var _data:Object = null;
		protected var _viewId:String = "";
		
		public function ReplaysView()
		{
			super();
		}
		
		override protected function configUI():void
		{
			super.configUI();
			
			try
			{
				Helpers.ConfigureSortingMenu(this.sortingButtonBar);
				this.sortingButtonBar.dataProvider = new DataProvider(Helpers.SORTING_BUTTONS);
				this.sortingButtonBar.addEventListener(SortingEvent.SORT_KEY_CHANGED, this.handleSortingKeyChanged);
				
				Helpers.ConfigureReplaysScrollingList(this.replaysList);
				this.replaysList.addEventListener(ListEvent.ITEM_CLICK, this.handleReplaysItemClick);
				
				Helpers.ConfigureDateFilterMenu(this.dateFilterButtonBar);
				this.dateFilterButtonBar.dataProvider = new DataProvider(Helpers.DATE_BUTTONS);
				this.dateFilterButtonBar.addEventListener(IndexEvent.INDEX_CHANGE, this.handleDateFilterIndexChange);
				
				this.paginator.addEventListener(PagingEvent.PAGE_CHANGED, handlePaginatorPageChange);
				
				this.replayFilters.y = -this.replayFilters.height;
				
				this.btnFilters.allowDeselect = true;
				this.btnFilters.toggleEnable = true;
				this.btnFilters.toggleGlow.visible = false;
				this.btnFilters.addEventListener(MouseEvent.CLICK, this.handleFiltersButtonClick);
				this.btnFilters.label = STRINGS.l10n('ui.window.filterButtonLabel');
				this.btnFilters.width = 235;
				this.btnFilters.focusable = false;				
				this.btnFilters.iconSource = "../maps/rmanager/filter.png";				
				this.btnFilters.toggle = false;
				this.btnFilters.validateNow();
				
			}
			catch (err:Error)
			{
				DebugUtils.LOG_ERROR("ReplaysView::configUI " + err.getStackTrace());
			}
		}
		
		override protected function onDispose():void
		{
			try
			{
				this.sortingButtonBar.removeEventListener(SortingEvent.SORT_KEY_CHANGED, this.handleSortingKeyChanged);
				this.sortingButtonBar.dataProvider.cleanUp();
				this.sortingButtonBar = null;
				
				this.replaysList.removeEventListener(ListEvent.ITEM_CLICK, this.handleReplaysItemClick);
				this.replaysList.dataProvider.cleanUp();
				this.replaysList = null;
				
				this.dateFilterButtonBar.removeEventListener(IndexEvent.INDEX_CHANGE, this.handleDateFilterIndexChange);
				this.dateFilterButtonBar.dataProvider.cleanUp();
				this.dateFilterButtonBar = null;
				
				this.paginator.removeEventListener(PagingEvent.PAGE_CHANGED, handlePaginatorPageChange);
				
				this.btnFilters.removeEventListener(MouseEvent.CLICK, this.handleFiltersButtonClick);
				this.btnFilters = null;
				
				this.paginator = null;
				
				this._data = null;
				
				super.onDispose();
			}
			catch (err:Error)
			{
				DebugUtils.LOG_ERROR("ReplaysView::onDispose " + err.getStackTrace());
			}
		}
		
		protected function handlePaginatorPageChange(event:PagingEvent):void
		{
			this.replayInfo.setData(null);
		}
		
		protected function handleSortingKeyChanged(event:SortingEvent):void
		{
			this.replayInfo.setData(null);
		}
		
		protected function handleReplaysItemClick(event:ListEvent):void
		{
			var selectedData:Object = this.replaysList.dataProvider[event.index];
			this.replayInfo.setData(selectedData);
			if (this._filtersToggle)
				this.updateFiltersVisible(false);
			
			this.btnFilters.toggleIndicator.selected = this._filtersToggle;
			this.btnFilters.validateNow();
			
		}
		
		protected function handleDateFilterIndexChange(event:IndexEvent):void
		{
			var selectedData:Object = this.dateFilterButtonBar.dataProvider[event.index];
			var data:Object = {dateTime: selectedData["key"]};
			this.replayInfo.setData(null);
			dispatchEvent(new FilterEvent(FilterEvent.FILTERS_CHANGED, data));
		}
		
		protected function handleFiltersButtonClick(event:MouseEvent):void
		{
			this._filtersToggle = !this._filtersToggle;
			
			this.btnFilters.toggleIndicator.selected = this._filtersToggle;
			this.btnFilters.validateNow();
			
			this.updateFiltersVisible(this._filtersToggle);
		}
		
		private function updateFiltersVisible(show):void
		{
			this._filtersToggle = show;
			this.toggleInfoVisible(!show);
			this.toggleFiltersVisible(show);
		}
		
		private function toggleInfoVisible(show:Boolean):void
		{
			var hiddenY:Number = this.height;
			if (show)
			{
				this.replayInfo.y = hiddenY;
				new Tween(500, this.replayInfo, {y: 25}, {fastTransform: false});
			}
			else
			{
				new Tween(500, this.replayInfo, {y: hiddenY}, {fastTransform: false});
			}
		}
		
		private function toggleFiltersVisible(show:Boolean):void
		{
			var hiddenY:Number = -this.replayFilters.height;
			if (show)
			{
				this.replayFilters.y = hiddenY;
				new Tween(500, this.replayFilters, {y: 25}, {fastTransform: false});
			}
			else
			{
				new Tween(500, this.replayFilters, {y: hiddenY}, {fastTransform: false});
			}
		}
		
		protected function setData(data:Object):void
		{
			try
			{
				DebugUtils.LOG_DEBUG("ReplaysView::setData ", (data as Array).length);
				if (data != null)
				{
					this.replaysList.scrollPosition = 0;
					this.replaysList.dataProvider = new DataProvider(data as Array);
					this.replaysList.selectedIndex = -1;
					this.replaysList.invalidateData();
					this.replaysList.invalidateRenderers();
					this.replaysList.invalidate();
					this.replayInfo.setData(null);
				}
			}
			catch (err:Error)
			{
				DebugUtils.LOG_ERROR("ReplaysView::setData " + err.getStackTrace());
			}
		}
		
		public function setFiltersData(maps:Array):void
		{
			this.replayFilters.setData({maps: maps});
			this.replayFilters.validateNow();
		}
		
		public function update(value:Object):void
		{
			this._viewId = value.id;
			this._data = value.data;
			this.paginator.itemsCount = value.itemsCount;
			this.sortingButtonBar.enabled = value.itemsCount != 0;
			if (this.initialized)
			{
				this.setData(this._data);
			}
			return;
		}
		
		public function canShowAutomatically() : Boolean
		{
			return true;
		}
		
		public function getComponentForFocus() : InteractiveObject
		{
			return null;
		}
	}
}
