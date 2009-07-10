if (!core.PrintMgr) {
    core.PrintMgr = new function() {
	    this.onPrintTextAndCommentsClick = function(){
			this._printIt(0) ;
		}, 
		
		this.onPrintTextOnlyItemClick = function(){
			this._printIt(1) ;
		}, 
		
		this._printIt = function(txtOnly) {
			// although versionId might already be there add it for the so_ case
			core.FilterMgr.updateFormFromFilterData("printFilterHiddenForm", {'txtOnly' : txtOnly, 'versionId':sv_versionId, 'versionId':sv_versionId}) ;
			core.FilterMgr.submitHiddenFilterForm("printFilterHiddenForm") ;
		}
	};
};
	