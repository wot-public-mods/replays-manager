package com.kmalyshev.rmanager.components
{
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.controls.ButtonBar;
	import scaleform.clik.interfaces.IListItemRenderer;
	
	import net.wg.gui.interfaces.IGroupedControl;
	import net.wg.gui.interfaces.ISoundButtonEx;
	
	public class LabelButtonBar extends ButtonBar implements IGroupedControl
	{
		
		public var textField:TextField;
		private var _label:String;
		
		public function get label():String
		{
			return this._label;
		}
		
		public function set label(value:String):void
		{
			if (this._label != value)
			{
				this._label = value;
				this.invalidate(InvalidationType.SETTINGS);
			}
		}
		
		public function get selectedRenderer():IListItemRenderer
		{
			if (_selectedIndex >= 0)
			{
				return _renderers[_selectedIndex];
			}
			return null;
		}
		
		public function get selectedButton() :ISoundButtonEx
		{
			if (_selectedIndex >= 0)
			{
				return _renderers[_selectedIndex];
			}
			return null;
		}
		
		public function LabelButtonBar()
		{
			super();
			
		}
		
		override protected function draw():void
		{
			super.draw();
			if (isInvalid(InvalidationType.SETTINGS))
			{
				this.textField.text = this.label;
				this.textField.autoSize = TextFieldAutoSize.LEFT;
				this.textField.width = this.textField.textWidth;
			}
			
			this.container.x = this.textField.x + this.textField.width + this.spacing;
			this.width = this.actualWidth;
		}
	}

}