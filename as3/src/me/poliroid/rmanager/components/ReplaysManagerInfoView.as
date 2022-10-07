package me.poliroid.rmanager.components
{
	
	import scaleform.clik.events.FocusHandlerEvent;

	import net.wg.gui.components.controls.CheckBox;
	import net.wg.gui.components.controls.LabelControl;
	import net.wg.gui.components.controls.TextInput;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.infrastructure.base.UIComponentEx;
	import net.wg.gui.messenger.data.ContactsShared;
	
	import me.poliroid.rmanager.data.UploaderLocalizationVO;
	
	public class ReplaysManagerInfoView extends UIComponentEx
	{
		public var startUpload:SoundButton;
		
		public var titleInput:TextInput;
		public var descriptionInput:TextInput;
		public var isSecret:CheckBox;
		
		public function ReplaysManagerInfoView()
		{
			super();
		}
		
		override protected function configUI() : void
		{
			super.configUI();
			configTextInput(titleInput);
			configTextInput(descriptionInput);
			descriptionInput.height = 95;
			descriptionInput.textField.multiline = true;
			descriptionInput.textField.wordWrap = true;
		}
		
		public function localization(localization:UploaderLocalizationVO) : void
		{
			startUpload.label = localization.buttonStartUpload;
			titleInput.defaultText = localization.inputTitle;
			descriptionInput.defaultText = localization.inputDescription;
			isSecret.label = localization.checkBoxIsSecretLabel;
			isSecret.toolTip = localization.checkBoxIsSecretInfo;
		}
		
		private function configTextInput(textInput:TextInput) : void
		{
			textInput.defaultTextFormat.color = ContactsShared.INVITE_PROMPT_DEFAULT_TEXT_COLOR;
			textInput.textField.textColor = ContactsShared.INVITE_PROMPT_DEFAULT_TEXT_COLOR;
			textInput.defaultTextFormat.italic = false;
			textInput.addEventListener(FocusHandlerEvent.FOCUS_IN, onTxtInpFocusInHandler, false, 0, true);
		}

		private function onTxtInpFocusInHandler(e:FocusHandlerEvent) : void
		{
			(e.target as TextInput).textField.textColor = ContactsShared.INVITE_INPUT_TEXT_COLOR;
		}
	}
}