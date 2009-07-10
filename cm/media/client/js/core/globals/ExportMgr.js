if (!core.ExportMgr) {
    core.ExportMgr = new function() {
		this.onExportTextAndCommentsClick = function(format) {
			this._export(0, format) ;
		},
		
		this.onExportTextOnlyClick = function(format) {
			this._export(1, format) ;
		},
		
		this._export = function(txtOnly, format) {
			// although versionId might already be there add it for the so_ case
			core.FilterMgr.updateFormFromFilterData("exportFilterHiddenForm", {'txtOnly' : txtOnly, 'format':format}) ;
			core.FilterMgr.submitHiddenFilterForm("exportFilterHiddenForm") ;
		}
		
	};
}


