package com.poliroid.gui.lobby.rmanager
{
	import flash.ui.Keyboard;
	import flash.events.TextEvent;
	
	import scaleform.clik.constants.InputValue;
	import scaleform.clik.events.ButtonEvent;
	import flash.geom.Rectangle;
	import scaleform.clik.events.InputEvent;
	import net.wg.infrastructure.base.AbstractWindowView;
	
	import com.poliroid.gui.lobby.rmanager.components.ReplaysManagerInfoView;
	import com.poliroid.gui.lobby.rmanager.components.ReplaysManagerStatusView;
	import com.poliroid.gui.lobby.rmanager.data.UploaderLocalizationVO;
	
	public class ReplaysManagerUpload extends AbstractWindowView
	{
		
		public var openURL:Function = null;
		public var upload:Function = null;
		
		public var info:ReplaysManagerInfoView;
		public var status:ReplaysManagerStatusView;
		
		private var l10n:UploaderLocalizationVO;
		
		public function ReplaysManagerUpload()
		{
			super();
			isCentered = true;
		}
		
		override protected function onPopulate():void
		{
			scrollRect = new Rectangle(0, 0, 440, 200);
			super.onPopulate();
			window.title = l10n.windowTitle;
			width = 440;
			height = 200;
			info.startUpload.addEventListener(ButtonEvent.CLICK, handleUploadClick);
		}
		
		override public function handleInput(event:InputEvent):void
		{
			if (event.details.code == Keyboard.ESCAPE && event.details.value == InputValue.KEY_DOWN && canClose)
				super.handleInput(event);
			else
				return;
		}
		
		public function as_setLocalization(localization:Object):void
		{
			l10n = new UploaderLocalizationVO(localization);
			info.localization(l10n);
			status.localization(l10n);
		}
		
		public function as_onUpdateProgress(total:Number, current:Number, percent:Number):void
		{
			status.onUpdateProgress(total, current, percent);
		}
		
		public function as_onUpdateStatus(newStatus:String):void
		{
			status.onUpdateStatus(newStatus);
		}
		
		public function as_onPopulateResponce(response:String):void
		{
			status.onResponce(App.utils.JSON.decode(response));
			status.responseTF.addEventListener(TextEvent.LINK, handleLinkClick);
		}
		
		private function handleUploadClick(e:ButtonEvent) : void
		{
			gotoAndPlay('upload');
			upload(info.titleInput.text, info.descriptionInput.text, info.isSecret.selected);
		}
		
		public function handleLinkClick(linkEvent:TextEvent):void
		{
			openURL(linkEvent.text);
		}
	}

}
