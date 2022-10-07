package me.poliroid.rmanager.components
{
	import flash.text.StyleSheet;
	import flash.text.TextField;
	import scaleform.clik.controls.StatusIndicator;
	
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.infrastructure.base.UIComponentEx;
	
	import me.poliroid.rmanager.data.UploaderLocalizationVO;
	
	
	public class ReplaysManagerStatusView extends UIComponentEx
	{
		public var uploadBar:StatusIndicator;
		
		public var uploadStats:TextField;
		public var uploadStatsPerc:TextField;
		public var statusTF:TextField;
		public var responseTF:TextField;
		
		private var l10n:UploaderLocalizationVO;
		
		public function ReplaysManagerStatusView()
		{
			super();
		}
		
		public function localization(localization:UploaderLocalizationVO) : void
		{
			l10n = localization;
		}
		
		override protected function configUI():void
		{
			uploadBar.width = 400;
			uploadBar.minimum = 0;
			uploadBar.maximum = 1;
			uploadBar.position = 0;
			
			super.configUI();
		}
		
		public function onUpdateProgress(total:Number, current:Number, percent:Number):void
		{
			var currentKb = Math.round(current / 1024);
			var totalKb = Math.round(total / 1024);
			uploadStats.text = currentKb + l10n.progressLabel.split("{{value}}").join(totalKb);
			uploadStatsPerc.text = percent.toString() + "%";
			uploadBar.position = Number(current / total);
			if (current / total == 1)
				onUpdateStatus("LoadingComplete");
		}
		
		public function onUpdateStatus(status:String) : void
		{
			statusTF.text = l10n.labelStatus + ": " + l10n["status" + status];
		}
		
		private function formatString(str:String):String
		{
			return "<font face='$FieldFont' size='12px'>" + str.split("<a href=\"").join("<a href=\"event:") + "</font>";
		}
		
		public function onResponce(response:Object):void
		{
			var myCSS:StyleSheet = new StyleSheet();
			myCSS.setStyle("a:link", {color: '#F25322', textDecoration: 'none'});
			myCSS.setStyle("a:hover", {color: '#FF7432', textDecoration: 'underline'});
			responseTF.styleSheet = myCSS;
			if (!response.result)
			{
				onUpdateStatus("ErrorOccure");
				switch (response.code)
				{
					case 0: 
						responseTF.htmlText = formatString(l10n.error0 + response.error.split(":")[1]);
						break;
					case 1: 
						responseTF.htmlText = formatString(l10n.error1 + response.error.split(":")[1]);
						break;
					case 2: 
						responseTF.htmlText = formatString(l10n.error2 + response.error.split(":")[1]);
						break;
					case 3: 
						responseTF.htmlText = formatString(l10n.error3 + response.error.split(":")[1]);
						break;
					case 4: 
						responseTF.htmlText = formatString(l10n.error4 + response.error.split(":")[1]);
						break;
					case 5: 
						responseTF.htmlText = formatString(l10n.error5 + response.error.split(":")[1]);
						break;
					case 6: 
						responseTF.htmlText = formatString(l10n.error6);
						break;
					default: 
						responseTF.htmlText = formatString(response.error);
						break;
				}
			}
			else
			{
				onUpdateStatus("Succes");
				var responseText:String = l10n.responceLabel;
				responseText = responseText.split("{{url}}").join("<a href=\"" + response.url + "\">" + l10n.linkLabel + "</a>");
				responseText = responseText.split("{{directLink}}").join("<a href=\"" + response.directLink + "\">" + l10n.linkLabel + "</a>");
				responseTF.htmlText = formatString(responseText);
			}
		}
	}
}