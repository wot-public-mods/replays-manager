package com.kmalyshev.rmanager.components
{
	import flash.display.MovieClip;
	import flash.text.TextFieldAutoSize;
	
	import com.kmalyshev.rmanager.events.SortingEvent;
	
	public class TextLinkSortButton extends TextLinkButton
	{
		
		public var icon:MovieClip;
		private var _ascending:Boolean;
		private var _key:String;
		
		public function get ascending():Boolean
		{
			return this._ascending;
		}
		
		public function set ascending(value:Boolean):void
		{
			if (this._ascending != value)
			{
				this.data["ascending"] = value;
				this._ascending = value;
				this.setAscendingIco(this._ascending);
			}
		}
		
		public function TextLinkSortButton()
		{
			return;
		}
		
		override protected function configUI():void
		{
			super.configUI();
			this.ascending = this.data["ascending"];
			this._key = this.data["key"];
		}
		
		override protected function draw():void
		{
			super.draw();
			this.icon.alpha = this.selected ? (100) : (0);
		}
		
		override protected function calculateWidth():Number
		{
			return this.textField.width + this.icon.width + 5;
		}
		
		override protected function resizeButton():void
		{
			super.resizeButton();
			this.alignIconText();
		}
		
		override protected function handleClick(param1:uint = 0):void
		{
			if (this.selected)
			{
				this.ascending = !this.ascending;
			}
			dispatchEvent(new SortingEvent(SortingEvent.SORT_KEY_CHANGED, this._key, this._ascending));
			super.handleClick(param1);
		}
		
		private function alignIconText():void
		{
			var textIconWidth:Number = this.calculateWidth();
			switch (this._autoSize)
			{
				case TextFieldAutoSize.CENTER: 
					this.textField.x = Math.ceil((this.hitMc.width - textIconWidth) >> 1);
					break;
				case TextFieldAutoSize.LEFT: 
					this.textField.x = 0;
					break;
				default: 
					this.textField.x = 10;
					break;
			}
			
			this.icon.x = Math.ceil(this.textField.x + this.textField.width);
		}
		
		private function setAscendingIco(asc:Boolean):void
		{
			if (asc)
			{
				this.icon.gotoAndStop("asc");
			}
			else
			{
				this.icon.gotoAndStop("desc");
			}
		}
	}
}
