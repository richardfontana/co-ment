initAll = function(){
	return {
          init : function(){
			// ATTACHS IN ATTACH LIST PANEL
			var attachController = new core.AttachController();
           	core.Language.init() ;

        	// global layout
			core.LayoutMgr.init() ;
			
			Ext.ComponentMgr.get('text_frame').el.mask(Ext.get('loadingindicatormsg').dom.innerHTML,"x-mask-loading");
			
			var commentAttachMgr = new core.CommentAttachMgr(attachController) ;
			// the order of subscribtion do matter here ! (for so_ case)
		    core.FilterMgr.filterMgrApplyEvent.subscribe(commentAttachMgr.onFilterMgrApply, commentAttachMgr);
		    core.FilterMgr.filterMgrApplyEvent.subscribe(core.TextMgr.onFilterMgrApply, core.TextMgr);
			core.TextMgr.register(commentAttachMgr) ;
			
			Ext.ComponentMgr.get('attachsPanel').on('add', commentAttachMgr.updateAttachCount) ;
			Ext.ComponentMgr.get('attachsPanel').on('remove', commentAttachMgr.updateAttachCount) ;

			// It is important that this call remain after the LayoutMgr init
          	core.SelectionMgr.init() ;

        	core.MenuMgr.init() ;
			core.FilterMgr.init() ;
          	
			// here we wait for the text div to be loaded in frame 
			onTextAvailable = function(){
				var doc = util.getTextDocument() ;
				var done = false;
				if (doc) {
					var textNode = doc.getElementById("c_l_o_s_u_r_e") ;
					if (textNode) { // TRIGGER first filter apply :
						core.FilterMgr.applyallbtnclick() ;
						done = true;
						Ext.ComponentMgr.get('text_frame').el.unmask();
					}
				}
				if (coment.cst.framed) {
					if (!done)
						window.setTimeout(onTextAvailable, 10);
				}
				
			}
			onTextAvailable() ;
			
			// DO NOT replace by direct inline  src=... in viewandcomment.html because it would trigger twice the call to the server 
			Ext.get('frameContainer').update('<iframe src=' + sv_frameSrc + ' style="width:100%;height:100%;" scrolling="auto" frameborder="0" id="frameid" name="frameid"></iframe>') ;
			
			if (!sv_embeded)
				Ext.get("tmc").setVisible(false) ;
		}	
	}

}();


