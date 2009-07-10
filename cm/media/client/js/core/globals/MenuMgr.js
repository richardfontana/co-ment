if (!core.MenuMgr) {
    core.MenuMgr = new function() {
		this.init = function(){

// translations :

			util.setInnerHTML("viewItemBar", gettext("View")) ;
			util.setInnerHTML("viewFilter", gettext("Filter")) ;
			util.setInnerHTML("viewFilterNone", gettext("None")) ;
			util.setInnerHTML("viewFilterSimple", gettext("Simple")) ;
			util.setInnerHTML("viewFilterAdvanced", gettext("Advanced")) ;
			util.setInnerHTML("viewFilterTags", gettext("Tag cloud")) ;

			util.setInnerHTML("actionItemBar", gettext("Actions")) ;
			
			util.setInnerHTML("editAction", gettext("Edit")) ;
			util.setInnerHTML("sharingAction", gettext("Sharing and moderation")) ;
			util.setInnerHTML("embedAction", gettext("Embed")) ;
			util.setInnerHTML("feedsAction", gettext("Feeds")) ;
			
			util.setInnerHTML("printAction", gettext("Print")) ;
			util.setInnerHTML("printActionTextAndCommentsItem", gettext("Text with (filtered) comments")) ;
			util.setInnerHTML("printActionTextOnlyItem", gettext("Text only")) ;

			util.setInnerHTML("printActionTextOnlyAsPdf", gettext("As Portable Document Format")) ;
			util.setInnerHTML("printActionTextOnlyFromBrow", gettext("From Browser")) ;

			util.setInnerHTML("printActionTextAndCommentsAsPdf", gettext("As Portable Document Format")) ;
			util.setInnerHTML("printActionTextAndCommentsFromBrow", gettext("From Browser")) ;
			
			util.setInnerHTML("advancedAction", gettext("Advanced")) ;
			util.setInnerHTML("advancedActionApplyAmendments", gettext("Apply amendments")) ;

			util.setInnerHTML("exportAction", gettext("Export")) ;
		 	util.setInnerHTML("exportActionTextAndComments", gettext("Text with (filtered) comments")) ;
			util.setInnerHTML("exportActionTextOnly", gettext("Text only")) ;
			
			util.setInnerHTML("exportActionTextOnlyAsPdf", gettext("As Portable Document Format")) ;
			util.setInnerHTML("exportActionTextOnlyAsRtf", gettext("As Rich Text Format")) ;
			util.setInnerHTML("exportActionTextOnlyAsOdt", gettext("As Open Document Text")) ;
			util.setInnerHTML("exportActionTextOnlyAsDoc", gettext("As Microsoft Word 97/2000/XP")) ;
			util.setInnerHTML("exportActionTextOnlyAsTxt", gettext("As Text Format")) ;

			util.setInnerHTML("exportActionTextAndCommentsAsPdf", gettext("As Portable Document Format")) ;
			util.setInnerHTML("exportActionTextAndCommentsAsRtf", gettext("As Rich Text Format")) ;
			util.setInnerHTML("exportActionTextAndCommentsAsOdt", gettext("As Open Document Text")) ;
			util.setInnerHTML("exportActionTextAndCommentsAsDoc", gettext("As Microsoft Word 97/2000/XP")) ;
			util.setInnerHTML("exportActionTextAndCommentsAsTxt", gettext("As Text Format")) ;
			
            // Initialize the root menu bar

            var oMenuBar = new YAHOO.widget.MenuBar("menudiv") ;
            // with these settings the menu will hide after some time(keep it as an example)
            // var oMenuBar = new YAHOO.widget.MenuBar("menudiv", { autosubmenudisplay:true, hidedelay:750, lazyload:false });

			// view filter
			var viewFilterSubMenu = YAHOO.widget.MenuManager.getMenu("viewFilterSubMenu") ;
			this.viewFilterNoneItem = viewFilterSubMenu.getItem(0) ;
			this.viewFilterSimpleItem = viewFilterSubMenu.getItem(1) ;
			this.viewFilterAdvancedItem = viewFilterSubMenu.getItem(2) ;
			this.viewFilterTagCloudItem = viewFilterSubMenu.getItem(3) ;
            onViewFilterNoneClick = function (p_sType, p_aArgs, p_oValue) {
            	core.LayoutMgr.showNoFilter() ;
                this.parent.hide();
                core.MenuMgr.checkCurrentFilterView(0) ;
            } ;
            onViewFilterSimpleClick = function (p_sType, p_aArgs, p_oValue) {
            	core.LayoutMgr.showSimpleFilter() ;
                this.parent.hide();
                core.MenuMgr.checkCurrentFilterView(1) ;
            } ;
            onViewFilterAdvancedClick = function (p_sType, p_aArgs, p_oValue) {
            	core.LayoutMgr.showAdvanceFilter() ;
                this.parent.hide();
                core.MenuMgr.checkCurrentFilterView(2) ;
            } ;
            onViewFilterTagCloudClick = function (p_sType, p_aArgs, p_oValue) {
            	core.LayoutMgr.showTagCloudFilter() ;
                this.parent.hide();
                core.MenuMgr.checkCurrentFilterView(3) ;
            } ;
            this.checkCurrentFilterView = function (itemNb) {
                core.MenuMgr.viewFilterNoneItem.cfg.setProperty("checked", (itemNb == 0)) ;
                core.MenuMgr.viewFilterSimpleItem.cfg.setProperty("checked", (itemNb == 1)) ;
                core.MenuMgr.viewFilterAdvancedItem.cfg.setProperty("checked", (itemNb == 2)) ;
                core.MenuMgr.viewFilterTagCloudItem.cfg.setProperty("checked", (itemNb == 3)) ;
            };

			this.viewFilterNoneItem.cfg.setProperty("onclick", { fn:onViewFilterNoneClick, scope : this.viewFilterNoneItem }) ;
			this.viewFilterSimpleItem.cfg.setProperty("onclick", { fn:onViewFilterSimpleClick, scope : this.viewFilterSimpleItem }) ;
			this.viewFilterAdvancedItem.cfg.setProperty("onclick", { fn:onViewFilterAdvancedClick, scope : this.viewFilterAdvancedItem }) ;
			this.viewFilterTagCloudItem.cfg.setProperty("onclick", { fn:onViewFilterTagCloudClick, scope : this.viewFilterTagCloudItem }) ;
			
			// view all comments
			this.viewAllCommentsAction = YAHOO.widget.MenuManager.getMenuItem("viewAllCommentsAction") ;
			this.viewAllCommentsAction.cfg.setProperty("onclick", { fn:core.FilterMgr.applyallbtnclick, scope : core.FilterMgr }) ;
			
			// view versions
			this.viewVersionsSubMenu = YAHOO.widget.MenuManager.getMenu("viewVersionsSubMenu") ;
            this.checkCurrentVersion = function (version_id) {
				var cpt = 0 ;
				var item = null ;
				while (item = this.viewVersionsSubMenu.getItem(cpt++)) {
					if (item.element.id == "verm_" + sv_versionId)
	                	item.cfg.setProperty("checked", true) ;
				} ;
			};

			// print
			var printTextOnlySubMenu = YAHOO.widget.MenuManager.getMenu("printActionTextOnlySubMenu") ;
			this.printTextOnlyAsPdf = printTextOnlySubMenu.getItem(0) ;
			var printTextOnlyFromBrow = printTextOnlySubMenu.getItem(1) ;

			var printTextAndCommentsSubMenu = YAHOO.widget.MenuManager.getMenu("printActionTextAndCommentsSubMenu") ;
			this.printTextAndCommentsAsPdf = printTextAndCommentsSubMenu.getItem(0) ;
			var printTextAndCommentsFromBrow = printTextAndCommentsSubMenu.getItem(1) ;

			onPrintTextAndCommentsFromBrowClick = function (p_sType, p_aArguments) {    
				core.PrintMgr.onPrintTextAndCommentsClick() ;
			}
			printTextAndCommentsFromBrow.clickEvent.subscribe(onPrintTextAndCommentsFromBrowClick); 			
			
			onPrintTextOnlyFromBrowClick = function (p_sType, p_aArguments) {    
				core.PrintMgr.onPrintTextOnlyItemClick() ;
			}
			printTextOnlyFromBrow.clickEvent.subscribe(onPrintTextOnlyFromBrowClick);
			
			// editVersion
			var editVersionSubMenu = YAHOO.widget.MenuManager.getMenu("advancedActionSubMenu") ;
			if (editVersionSubMenu) {
				var editVersionApplyAmendments = editVersionSubMenu.getItem(0) ;
				onEditVersionApplyAmendmentsClick = function (p_sType, p_aArguments) {
					core.TextMgr.applyAmendments() ;    
				}
				editVersionApplyAmendments.clickEvent.subscribe(onEditVersionApplyAmendmentsClick);
			} 			

			// export
			var exportTextOnlySubMenu = YAHOO.widget.MenuManager.getMenu("exportActionTextOnlySubMenu") ;
			this.exportTextOnlyAsPdf = exportTextOnlySubMenu.getItem(0) ;
			this.exportTextOnlyAsRtf = exportTextOnlySubMenu.getItem(1) ;
			this.exportTextOnlyAsOdt = exportTextOnlySubMenu.getItem(2) ;
			this.exportTextOnlyAsDoc = exportTextOnlySubMenu.getItem(3) ;
			this.exportTextOnlyAsTxt = exportTextOnlySubMenu.getItem(4) ;
			
            onExportTextOnlyAs = function (p_sType, p_aArgs, format) {
				core.ExportMgr.onExportTextOnlyClick(format) ;
            } ;
			this.exportTextOnlyAsPdf.cfg.setProperty("onclick", { fn:onExportTextOnlyAs, obj:"pdf" }) ;
			this.printTextOnlyAsPdf.cfg.setProperty("onclick", { fn:onExportTextOnlyAs, obj:"pdf" }) ;
			this.exportTextOnlyAsRtf.cfg.setProperty("onclick", { fn:onExportTextOnlyAs, obj:"rtf" }) ;
			this.exportTextOnlyAsOdt.cfg.setProperty("onclick", { fn:onExportTextOnlyAs, obj:"odt" }) ;
			this.exportTextOnlyAsDoc.cfg.setProperty("onclick", { fn:onExportTextOnlyAs, obj:"doc" }) ;
			this.exportTextOnlyAsTxt.cfg.setProperty("onclick", { fn:onExportTextOnlyAs, obj:"text" }) ;

			var exportTextAndCommentsSubMenu = YAHOO.widget.MenuManager.getMenu("exportActionTextAndCommentsSubMenu") ;
			this.exportTextAndCommentsAsPdf = exportTextAndCommentsSubMenu.getItem(0) ;
			this.exportTextAndCommentsAsRtf = exportTextAndCommentsSubMenu.getItem(1) ;
			this.exportTextAndCommentsAsOdt = exportTextAndCommentsSubMenu.getItem(2) ;
			this.exportTextAndCommentsAsDoc = exportTextAndCommentsSubMenu.getItem(3) ;
			this.exportTextAndCommentsAsTxt = exportTextAndCommentsSubMenu.getItem(4) ;
			
            onExportTextAndCommentsAs = function (p_sType, p_aArgs, format) {
				core.ExportMgr.onExportTextAndCommentsClick(format) ;
            } ;
			this.exportTextAndCommentsAsPdf.cfg.setProperty("onclick", { fn:onExportTextAndCommentsAs, obj:"pdf" }) ;
			this.printTextAndCommentsAsPdf.cfg.setProperty("onclick", { fn:onExportTextAndCommentsAs, obj:"pdf" }) ;
			this.exportTextAndCommentsAsRtf.cfg.setProperty("onclick", { fn:onExportTextAndCommentsAs, obj:"rtf" }) ;
			this.exportTextAndCommentsAsOdt.cfg.setProperty("onclick", { fn:onExportTextAndCommentsAs, obj:"odt" }) ;
			this.exportTextAndCommentsAsDoc.cfg.setProperty("onclick", { fn:onExportTextAndCommentsAs, obj:"doc" }) ;
			this.exportTextAndCommentsAsTxt.cfg.setProperty("onclick", { fn:onExportTextAndCommentsAs, obj:"text" }) ;

			this.checkCurrentFilterView(0) ;
			this.checkCurrentVersion() ;
            // Render the menu bar
            oMenuBar.render();
		};
	};
};
	