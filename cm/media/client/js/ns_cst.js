YAHOO.namespace('coment');
coment = YAHOO.coment ;

YAHOO.namespace('coment.core');
YAHOO.namespace('coment.util');

core = coment.core ;
util = coment.util ;

YAHOO.namespace('coment.cst');
coment.cst = {
	framed : true,
	debug : false ,
	maxCallDuration : 5000 ,

	idsSeparator : "," ,

	textNodeId : "text" ,
	print_comments : "c_comments" ,
	
	textNodeCls : "text" ,
	
	textWordIdPref : "w_" ,
	dispIdPref : "disp_" ,
	textType : 'T', 
	
	dateType : 'D',	
	
	attachDDGroup : "attach_DD_group" ,
	
	attachPositionOffset : 3,
	
	pathToTarget : "/site_media/client",
	
	attachListInitialHeight : 420,
	westInitialWidth : 350,
	scrollbarWidth : 19, 	
	currentSelDispLength : 100,
	
	maxSelectedTxtLength : 2000, 

	colorizePacketSize : 10, 
	colorizePaintTimeout : 10 
	
} ;
