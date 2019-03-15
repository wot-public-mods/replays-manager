package com.kmalyshev.rmanager.components
{
	import flash.display.MovieClip;
	import net.wg.gui.components.controls.SoundButton;
	import scaleform.clik.constants.InvalidationType;
	
	public class TextLinkButton extends SoundButton
	{
		
		public var bg_mc:MovieClip;
		private const NORMAL_COLOR:uint = 0x999999;
		private const SELECTED_COLOR:uint = 0xEEEEEE;
		
		public function TextLinkButton()
		{
			return;
		}
		
		override protected function draw():void
		{
			
			if (isInvalid(InvalidationType.DATA))
			{
				
				this.textField.text = this._label;
				this.textField.width = this.textField.textWidth + 5;
				
				if (this.data)
				{
					this.selected = this.data["selected"] != undefined ? this.data["selected"] : false;
				}
				
				invalidate(InvalidationType.SIZE);
			}
			
			if (isInvalid(InvalidationType.SIZE))
			{
				resizeButton();
			}
			
			if (isInvalid(InvalidationType.STATE))
			{
				if (this.state == "over" || this.selected)
				{
					this.textField.textColor = SELECTED_COLOR;
				}
				else
				{
					this.textField.textColor = NORMAL_COLOR;
				}
			}
		}
		
		override protected function calculateWidth():Number
		{
			return this.textField.width;
		}
		
		protected function resizeButton():void
		{
			var newWidth = calculateWidth();
			if (newWidth != this.bg_mc.width)
			{
				this.bg_mc.width = this.hitMc.width = this.width = newWidth; //resize all layers (bg, hitMc)
			}
		}
	}

}