// removes the square border that IE
// insists on adding to checkboxes and radio
function removeCheckBoxBorders()
{
	var el = document.getElementsByTagName("input");
	for (i=0;i<el.length;i++) {
	  var type = el[i].getAttribute("type");
	  if((type=="checkbox")||(type=="radio")) {
	   el[i].style.border = "none";
	    }
	  }
} ;

Ext.MessageBox.buttonText.yes = gettext("yes");
Ext.MessageBox.buttonText.no = gettext("no");

function coment_confirm(message, fn){
		Ext.MessageBox.show({
		    title:gettext("Warning"),
		    msg: message,
		    buttons: Ext.MessageBox.YESNO,
		    fn: function (btn) { if (btn == "yes") fn.apply() ;},
		    icon: Ext.MessageBox.QUESTION
		});
} ;

function putYahooButtons() {
	$(".high_button").each(function (o) {            
	    var oPushButton1 = new YAHOO.widget.Button(this); 
	});
} ;

function dynamicMessage() {
	var msgCt = Ext.get('message_container') ;
	if (msgCt){ 
		//var s = String.format.apply(String, Array.prototype.slice.call(arguments, 1));
		var m = Ext.DomHelper.append('dynamic_message_container', {html:'<div>'+msgCt.dom.innerHTML+'</div>'}, true);
		m.alignTo("topbar", "bl");
		m.slideIn('t').pause(4).ghost("t", {remove:true});
	}
} ;

$(document).ready(function() {
	removeCheckBoxBorders() ;
	putYahooButtons() ;
	dynamicMessage() ;
});
