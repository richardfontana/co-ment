if (!core.FilterMgr) {
    core.FilterMgr = new function() {
		this._filterData = {} ;
		this._cachedFilterData = null ;
		
		// CUSTOM EVENTS
		this.filterMgrApplyEvent = new YAHOO.util.CustomEvent("filterMgrApply", this); 
	
		this.init = function() {
			this._filterData['simple'] = this._getFilterData() ;
			this._filterData['adv'] = this._getFilterData() ;
			this._filterData['all'] = this._getFilterData() ;
			this._filterData['tag'] = this._getFilterData() ;
		};
		
		this._applyfilter = function(filterData) {
			this.filterMgrApplyEvent.fire() ;
		};
		
		this.applyallbtnclick = function() {
			if (!core.ServerExchange.callIsInProgress()) {
				this._cachedFilterData = this._filterData['all'] ;
				this._applyfilter() ;
			}
		};
		
		this.applysimplebtnclick = function() {
			if (!core.ServerExchange.callIsInProgress()) {
				this._getSimpleOnlyFilterData(this._filterData['simple']) ;
				this._cachedFilterData = this._filterData['simple'] ;
				this._applyfilter() ;
			}
		};
		
		this.applyadvbtnclick = function() {
			if (!core.ServerExchange.callIsInProgress()) {
				this._getSimpleOnlyFilterData(this._filterData['adv']) ;
				this._getAdvOnlyFilterData(this._filterData['adv']) ;
				this._cachedFilterData = this._filterData['adv'] ;
				this._applyfilter() ;
			}
		};
		
		this.applytagbtnclick = function(tagId) {
			if (!core.ServerExchange.callIsInProgress()) {
				this._cachedFilterData = this._filterData['tag'] ;
				this._cachedFilterData['tagId'] = tagId ;
				this._applyfilter() ;
			}
		};
		
		this.getCachedFilterData = function() {
			return this._cachedFilterData ;
		};
		
		this.toggleTagMode = function(tagId) {
			
		};
		
		this._unsetCurrentTag = function(){
			var tagNodes = YAHOO.util.Dom.getElementsByClassName('current_tag', 'span', 'tagcloud');
			if (tagNodes.length >0)
				Ext.fly(tagNodes[0].id).removeClass('current_tag') ;
		};
		
		this._setCurrentTag = function(id){
			Ext.fly(id).addClass('current_tag') ;
		};
		
		this._getSimpleOnlyFilterData = function (filterData) {
			filterData['textfilterselect'] = Ext.ComponentMgr.get('textfilterselect').getValue() ;
			filterData['textsearchfor'] = Ext.ComponentMgr.get('textsearchfor').getValue() ;
		};
		
		this._getAdvOnlyFilterData = function (filterData) {
			filterData['datefilterselect'] = Ext.ComponentMgr.get('datefilterselect').getValue() ;
			filterData['fromdatefield'] = coment.util.dateToString(Ext.ComponentMgr.get('fromdatefield').getValue()) ;
			filterData['todatefield'] = coment.util.dateToString(Ext.ComponentMgr.get('todatefield').getValue()) ;
	
			filterData['statefilterselect'] = Ext.ComponentMgr.get('statefilterselect').getValue() ;
		};
		
		this._getFilterData = function () {
			var filterData = {} ;
				
			this._getSimpleOnlyFilterData(filterData) ;
	
			this._getAdvOnlyFilterData(filterData) ;
			
			filterData['tagId'] = -1 ;
			return filterData ;
		};
		
		this.updateFormFromFilterData = function (formId, toAppend) {
			//var form = _filterformtpl.applyTemplate({ target: addr}) ;
			var form = Ext.get(formId) ;
			var innerhtml = "" ;
			for (var id in this._cachedFilterData) {
				innerhtml = innerhtml + '<input type="hidden" name="' + id + '" value="' + this._cachedFilterData[id] + '">' ;
			}
			for (var id in toAppend) {
				innerhtml = innerhtml + '<input type="hidden" name="' + id + '" value="' + toAppend[id] + '">' ;
			}
			form.update(innerhtml) ; 
		};
		
		this.submitHiddenFilterForm = function(formId){
			document[formId].submit();			
		}; 
		
		
	};
}

