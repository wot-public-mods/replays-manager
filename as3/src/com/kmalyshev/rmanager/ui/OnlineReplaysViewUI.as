package com.kmalyshev.rmanager.ui
{
	import flash.display.InteractiveObject;
	import flash.text.TextField;
	import flash.text.TextFieldAutoSize;
	
	import scaleform.clik.core.UIComponent;
	
	import net.wg.infrastructure.interfaces.IViewStackContent;
	
	import com.kmalyshev.rmanager.lang.STRINGS;
	
	dynamic public class OnlineReplaysViewUI extends UIComponent implements IViewStackContent
	{
		
		public var textField:TextField;
		
		private var _data:Object = null;
		private var _viewId:String = "";
		
		public function OnlineReplaysViewUI()
		{
			super();
		}
		
		override protected function configUI():void
		{
			super.configUI();
			this.textField.text = STRINGS.RMANAGER_ONLINE_PLACEHOLDER;
			this.textField.autoSize = TextFieldAutoSize.CENTER;
		}
		
		public function getComponentForFocus():InteractiveObject
		{
			return null;
		}
		
		/*protected function setData(data: Object): void {
		   try {
		   this.replaysList.dataProvider = new DataProvider(data as Array);
		   this.replaysList.invalidate();
		
		   this.paginator.itemsCount = data.length;
		   } catch(err: Error) {
		   DebugUtils.LOG_ERROR("OwnReplaysViewUI::setData: " + err);
		   }
		 }*/
		
		public function update(value:Object):void
		{
			this._viewId = value.id;
			this._data = value.data;
			if (this.initialized)
			{
				//this.setData(this._data);				
			}
			return;
		}
		
		public function canShowAutomatically():Boolean
		{
			return true;
		}
	
	}

}
