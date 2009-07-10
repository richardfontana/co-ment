// core.TextMgr._attachMgr._attachController
// this class handles the list of attach in Attach List Panel

core.AttachController = function(){
	this._activeAttach = null ;

	// CUSTOM EVENT	
//	this.attachControllerAttachSelectEvent = new YAHOO.util.CustomEvent("attachControllerAttachSelect", this); 
	
	// CLIENT attach, indexed by attach.attach.id (id of server corresponding entity)
	this._attachs = {} ;
	
	// CLIENT discussionItem, indexed by discussionItem._sDiscussionItem.id (id of seam corresponding entity)
	this._discussionItems = {} ;
	
	this._computedResponseTitle = null ;
} ;

core.AttachController.prototype = {
	
	clear : function(me) {
		this.removeAttachs() ;
		this.setActiveAttach(null) ;
	},
	
	getAttachs : function() {
		return this._attachs ;
	},
	             
	getAttach: function(attachId){
		return this._attachs[attachId];
	},

	getDiscussionItem: function(discussionItemId){
		return this._discussionItems[discussionItemId];
	},
	
	getActiveAttach : function(){
		return this._activeAttach ;
	},
	
	/* if attach == null will unselect current selection */
	setActiveAttach : function(attach){
		// UNSELECT
		if (this._activeAttach) {
			Ext.fly(this._activeAttach.getPanelId()).removeClass('selectAtt2') ;
			this._showAttachTextPart(this._activeAttach, false) ;
			this._activeAttach = null ;	
		}

		// SELECT
		if (attach) {
			Ext.fly(attach.getPanelId()).addClass('selectAtt2') ;
			this._activeAttach = attach ;	
			this._showAttachTextPart(this._activeAttach, true) ;
		}
	},
	
/*	helpMsgInAttachList : function(attachList){
		var attL =  attachList ;
		if (!attL)
			var attL = YAHOO.util.Dom.get('attachlist');
		var helpmsgdiv = YAHOO.util.Dom.get("helpAttachList");
		util.displayYesNo(helpmsgdiv,(attL.childNodes.length == 1)) ;
	},*/
	
	addDiscussionItem : function(di) {
		this._discussionItems[di.getId()]=di;
	},
	
	removeDiscussionItem : function(discussionItemId) {
		di = this._discussionItems[discussionItemId] ;
		if (di) {
			delete this._discussionItems[discussionItemId];
		}
	},
	
	updateAttach : function(sAttach) {
		if (this._attachs[sAttach.id]) {
			this._attachs[sAttach.id].setAttach(sAttach) ;
		}
	},
	
	updateDiscussionItem : function(sDi) {
		this._discussionItems[sDi.id].setDiscussionItem(sDi) ;
	},
	
	addAttach : function(attach){
//		this.helpMsgInAttachList(attachList) ;
		this._attachs[attach.getId()]=attach;
	},
	
	removeAttach : function(attach) {
		if (this._activeAttach == attach) 
			this.setActiveAttach(null) ;
		
		// delete replies that have attach as parent
		for (var id in this._discussionItems) {
			if (this._discussionItems[id].getParentAttachId() == attach.getId())
				this.removeDiscussionItem(this._discussionItems[id]);
		}
		
		delete this._attachs[attach.getId()];
	},

	removeAttachs : function() {
		for (var id in this._attachs) {
			this.removeAttach(this._attachs[id]);
		}
		// this._attachs = {} ; // not sure this is usefull
	},
	
	// couleur 1 seul commentaire : FFF39A
	// 27F3C3 == (FFF39A - D7FFD7)
	_computeTextPartColor : function(node, show){
		var newcolor = parseInt(node.getColor('background-color', 'FFFFFF', ''),16) ;
		var isSelected = node.hasClass('selected_textpart');
		if ((isSelected && !show) || (!isSelected && show)) {
			if (isSelected)
				node.removeClass('selected_textpart');
			else 
				node.addClass('selected_textpart');
		
			var targetcolor = (show)?parseInt("-27F3C3",16):parseInt("27F3C3",16);
			newcolor = newcolor + targetcolor ;
		}
		var ret = newcolor.toString(16) ;
		while (ret.length < 6) {
			ret = "0" + ret ;
		}
		return '#'+ ret ;
	},
	
	_showAttachTextPart : function(attach, show){
		if (attach) {
			var startWord = attach.getStartWord() ;
			for (var word = startWord ; word < attach.getEndWord() + 1 ; word++) {
				var markerId = coment.util.fromWordToMarkerId(word) ;
				var node = util.getElt(markerId) ;
				if (show) {
					if (word == startWord) {
						var xy = node.getXY() ; 
						util.getTextWindow().scrollTo(xy[0], xy[1]-100) ;	// - 100 is for having a little text before comment to get the context				
					}
	
					//node.addClass('selected_textpart');
					var newcolor = 	this._computeTextPartColor(node, show) ;
					node.setStyle({'background-color':newcolor}) ;
				}
				else {
					//node.removeClass('selected_textpart');
					var newcolor = 	this._computeTextPartColor(node, show) ;
					node.setStyle({'background-color':newcolor}) ;
					//node.setStyle('text-decoration', '') ;
				}
			}
		}
	}
};
