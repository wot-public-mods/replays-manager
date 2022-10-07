package me.poliroid.rmanager.components
{
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.constants.DirectionMode;
	import scaleform.clik.core.UIComponent;
	import scaleform.clik.data.DataProvider;
	import scaleform.clik.events.ButtonEvent;
	import scaleform.clik.interfaces.IDataProvider;
	
	import me.poliroid.rmanager.events.PagingEvent;
	import me.poliroid.rmanager.lang.STRINGS;
	
	public class Paginator extends UIComponent
	{
		
		public static const PAGE_SIZE:Number = 10;
		
		public var pageSize:Number = PAGE_SIZE;
		public var visiblePages:Number = 5;
		public var buttonBar:LabelButtonBar;
		
		private var _itemsCount:Number = 0;
		private var _currentPage:Number = 1;
		private var _totalPages:Number = 1;
		
		public function get currentPage():Number
		{
			return this._currentPage;
		}
		
		public function get itemsCount():Number
		{
			return this._itemsCount;
		}
		
		public function set itemsCount(value:Number):void
		{
			if (this._itemsCount != value)
			{
				this._itemsCount = value;
				this._totalPages = Math.ceil(this._itemsCount / this.pageSize);
				if (this._totalPages < 1)
				{
					this._totalPages = 1;
				}
				if (this._currentPage > this._totalPages)
				{
					this._currentPage = 1;
				}
				this.invalidate(InvalidationType.DATA);
			}
		}
		
		public function get totalPages():Number
		{
			return this._totalPages;
		}
		
		public function Paginator()
		{
			super();
		}
		
		override protected function configUI():void
		{
			super.configUI();
			this.buttonBar.label = STRINGS.l10n('ui.window.paginatorLabel');
			this.buttonBar.itemRendererName = "me.poliroid.rmanager.ui.TextLinkButtonUI";
			this.buttonBar.direction = DirectionMode.HORIZONTAL;
			this.buttonBar.spacing = 5;
			this.buttonBar.autoSize = "left";
			this.buttonBar.selectedIndex = -1;
			this.buttonBar.focusable = false;
			
			this.buttonBar.addEventListener(ButtonEvent.CLICK, this.handleButtonClick);
		}
		
		override protected function draw():void
		{
			super.draw();
			this.buttonBar.visible = this.itemsCount != 0;
			if (isInvalid(InvalidationType.DATA))
			{
				this.redrawPaginator();
			}
		}
		
		private function setSelectedPage(pageNum:Number, data:IDataProvider):void
		{
			var pages:Array = data as Array;
			for (var i in pages)
			{
				var flag:Boolean = pages[i]["value"] == pageNum;
				pages[i]["selected"] = flag;
				if (flag)
				{
					this.buttonBar.selectedIndex = i;
				}
			}
			
			this.buttonBar.dataProvider = new DataProvider(pages);
			this.buttonBar.validateNow();
		}
		
		private function handleButtonClick(event:ButtonEvent):void
		{
			var target:TextLinkButton = event.target as TextLinkButton;
			if (target.data["value"] != null)
			{
				var num:int = int(target.data["value"]);
				if (this._currentPage != num)
				{
					this._currentPage = num;
				}
				else
				{
					return;
				}
				
			}
			else
			{
				if (target.data["key"] == "next")
				{
					this._currentPage = this._currentPage + 1;
				}
				else
				{
					this._currentPage = this._currentPage - 1;
				}
			}
			this.redrawPaginator();
			this.dispatchEvent(new PagingEvent(PagingEvent.PAGE_CHANGED, this._currentPage));
		}
		
		private function redrawPaginator():void
		{
			this.setSelectedPage(this._currentPage, this.getDataProvider());
		}
		
		private function getDataProvider():DataProvider
		{
			var arr:Array = new Array();
			var firstPage:Number = this._currentPage - int(this.visiblePages / 2);
			
			if (firstPage < 1)
			{
				firstPage = 1;
			}
			else
			{
				if (this.totalPages - firstPage < this.visiblePages)
				{
					firstPage = this.totalPages - this.visiblePages + 1;
					if (firstPage <= 1)
					{
						firstPage = 1;
					}
				}
			}
			
			var lastPage:Number = firstPage + this.visiblePages - 1;
			if (lastPage > this.totalPages)
			{
				lastPage = this.totalPages;
			}
			
			if (firstPage != 1)
			{
				arr.push({label: STRINGS.l10n('ui.window.paginatorFirst'), value: 1, selected: false});
				arr.push({label: STRINGS.l10n('ui.window.paginatorPrev'), value: null, key: "prev", selected: false});
			}
			
			for (var i:int = firstPage; i <= lastPage; i++)
			{
				arr.push({label: i, value: i, selected: false});
			}
			
			if (this._currentPage != this.totalPages)
			{
				arr.push({label: STRINGS.l10n('ui.window.paginatorNext'), value: null, key: "next", selected: false});
			}
			
			if (lastPage < this.totalPages)
			{
				arr.push({label: STRINGS.l10n('ui.window.paginatorLast'), value: this.totalPages, selected: false});
			}
			
			return new DataProvider(arr);
		}
	}
}
