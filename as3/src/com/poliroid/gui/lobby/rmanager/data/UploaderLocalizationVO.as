package com.poliroid.gui.lobby.rmanager.data
{
	
	import net.wg.data.daapi.base.DAAPIDataClass;
	
	public class UploaderLocalizationVO extends DAAPIDataClass
	{
		
		public var windowTitle:String = "";
		public var labelStatus:String = "";
		public var statusNotFound:String = "";
		public var statusFound:String = "";
		public var statusLoading:String = "";
		public var statusErrorOccure:String = "";
		public var statusConnectionError:String = "";
		public var statusLoadingComplete:String = "";
		public var statusWrongAccount:String = "";
		public var statusNotAccount:String = "";
		public var statusSucces:String = "";
		public var linkLabel:String = "";
		public var progressLabel:String = "";
		public var responceLabel:String = "";
		public var error0:String = "";
		public var error1:String = "";
		public var error2:String = "";
		public var error3:String = "";
		public var error4:String = "";
		public var error5:String = "";
		public var error6:String = "";
		public var buttonStartUpload:String = "";
		public var inputTitle:String = "";
		public var inputDescription:String = "";
		public var checkBoxIsSecretLabel:String = "";
		public var checkBoxIsSecretInfo:String = "";
		
		public function UploaderLocalizationVO(data:Object) 
		{
			super(data);
		}
	}
}
