if (!core.LayoutMgr) {
    core.LayoutMgr = new function(){

        this.adaptDateFieldsVisibility = function(){
			var dateselectval = Ext.ComponentMgr.get('datefilterselect').getValue() ;
			var fromEnabled = (dateselectval == "createdafter") || (dateselectval == "createdbetween") ;
			var toEnabled = (dateselectval == "createdbefore") || (dateselectval == "createdbetween") ;
			Ext.ComponentMgr.get('fromdatefield').setDisabled(!fromEnabled) ;
			Ext.ComponentMgr.get('todatefield').setDisabled(!toEnabled) ;
		};

		// there has to be a better way but for now ...
        this.hidemenus = function(){
			var l = Ext.ComponentMgr.get('fromdatefield').menu
			if (l)
				l.hide() ;
			l = Ext.ComponentMgr.get('todatefield').menu ;
			if (l)
				l.hide() ;
			l = Ext.ComponentMgr.get('datefilterselect').list ;
			if (l)
				l.hide() ;
			l = Ext.ComponentMgr.get('textfilterselect').list ;
			if (l)
				l.hide() ;
		}; 
		
		// there has to be a better way but for now ...
        this.doLayout = function(){
			this.viewport.doLayout() ;
		}; 

		this.connectFilterResize = function(id) {
			Ext.ComponentMgr.get(id).on('collapse', this.doLayout, this) ;
			Ext.ComponentMgr.get(id).on('expand', this.doLayout, this) ;
			Ext.ComponentMgr.get(id).on('hide', this.doLayout, this) ;
			Ext.ComponentMgr.get(id).on('show', this.doLayout, this) ;
		};

	
        this.init = function(){
            // page global layout ( == slocums panels and buttons)
            this.globalLayoutInit();
			
		    Ext.get('simplefilter_apply_btn').on('click', core.FilterMgr.applysimplebtnclick, core.FilterMgr) ;
			Ext.get('advfilter_apply_btn').on('click', core.FilterMgr.applyadvbtnclick, core.FilterMgr) ;

			Ext.get('simplefilter_view_comments').on('click', core.FilterMgr.applyallbtnclick, core.FilterMgr) ;
			Ext.get('advfilter_view_comments').on('click', core.FilterMgr.applyallbtnclick, core.FilterMgr) ;
			Ext.get('tagcloud_view_comments').on('click', core.FilterMgr.applyallbtnclick, core.FilterMgr) ;

			Ext.get('view_all_comments').on('click', core.FilterMgr.applyallbtnclick, core.FilterMgr,{'preventDefault':true, 'stopPropagation':true}) ;
			
			Ext.get('mail_sub').on('click', core.TextMgr.onMailSubscribe, core.TextMgr,{'preventDefault':true, 'stopPropagation':true}) ;

			// Ext.get('textsearchfor').addKeyListener(Ext.EventObject.ENTER, core.FilterMgr.applyfilterbtnclick, core.FilterMgr);

			Ext.ComponentMgr.get('datefilterselect').on('select', this.adaptDateFieldsVisibility, this, true);
			
            this.infoMsgElt = Ext.get('info_msg');
            this.errorMsgElt = Ext.get('error_msg');
            
            var elt = Ext.get('addattach');
            if (elt) 
                elt.setVisible(true);
            elt = Ext.get('editattach');
            if (elt) 
                elt.setVisible(true);
            
            this.activateAttachListTab();
            this.hideEditAttachTab();
            
            var elt = YAHOO.util.Dom.get("current_sel");
            this._initialSelectionContent = (elt) ? elt.innerHTML : null;
			
            this.doLayout() ;

			this.connectFilterResize('datefieldset') ;
			this.connectFilterResize('textfieldset') ;
			this.connectFilterResize('statefieldset') ;
			
			this.updateMailLnk();
						
        };
        
        this.globalLayoutInit = function(){
            //Ext.state.Manager.setProvider(new Ext.state.CookieProvider());
            
            var attachsPanel = new Ext.Panel({
                title: gettext('List'),
                id: 'attachsPanel'
            });
            this.attachsTabPanel = new Ext.TabPanel({
                region: 'north',
                height: 250,
                border: false,
                split: true,
                activeTab: 0,
                defaults: {
                    autoScroll: true
                },
                items: [attachsPanel]
            });
            if (null != YAHOO.util.Dom.get("editattach")) {
                new Ext.Button({
					id : "edit_btn",
                    renderTo: "edit_",
                    text: gettext("save changes")
                });
				
                new Ext.Button({
					id : "edit_cancel_btn",
                    renderTo: "edit_cancel",
                    text: gettext("cancel")
                });
				
                var editAttachPanel = new Ext.Panel({
                    contentEl: 'editattach',
                    title: gettext('Edit'),
                    id: 'editAttachPanel'
                });
                this.attachsTabPanel.add(editAttachPanel);
            }
            
            if (null != YAHOO.util.Dom.get("addattach")) {
                new Ext.Button({
					id : "add_btn",
                    renderTo: "add_",
                    text: gettext("add comment")
                });
				
                var addAttachPanel = new Ext.Panel({
                    contentEl: 'addattach',
                    title: gettext('Add'),
                    id: 'addAttachPanel'
                });
                this.attachsTabPanel.add(addAttachPanel);
                
                coment.util.setValue("add_author", core.User.getCookieAuthor());
                coment.util.setValue("add_email", core.User.getCookieEMail());
            }
            
            var datesearchtypestore = new Ext.data.SimpleStore({
                fields: ['datesearchtypeid', 'datesearchtype'],
                data: [['createdbefore', gettext('before')],['createdafter', gettext('after')],['createdbetween', gettext('between')],['',gettext('no date criteria')]]
            });
            var textsearchtypestore = new Ext.data.SimpleStore({
                fields: ['textsearchtypeid', 'textsearchtype'],
                data: [['text_and_title', gettext('comments\' text and title')],['user',gettext('comments\' authors')]]
            });
			
			var statefilterselect = new Ext.ux.Multiselect({
				id	              :  'statefilterselect',
				name              :  'statefilterselect',
				fieldLabel        :  gettext('States'),
				dataFields        :  ['stateid', 'statename'], 
				data              :  core.TextMgr.getWorkflowStates(),
				valueField        :  'stateid',
				displayField      :  'statename',
				width             :  150,
				height            :  60,
				allowBlank        :  true
			});
			
            var datefilterselect = new Ext.form.ComboBox({
				id:'datefilterselect',
                valueField: 'datesearchtypeid',
                store: datesearchtypestore,
                displayField: 'datesearchtype',
                typeAhead: true,
                mode: 'local',
                triggerAction: 'all',
                emptyText: gettext('Choose...'),
                labelSeparator: '',
				editable:false,
                width: 180
            });
			
            var textfilterselect = new Ext.form.ComboBox({
				id:'textfilterselect',
                valueField: 'textsearchtypeid',
                store: textsearchtypestore,
                displayField: 'textsearchtype',
                typeAhead: true,
                mode: 'local',
                triggerAction: 'all',
                hideLabel: true,
				editable:false,
				width:230
            });
			
            var fromdatefield = new Ext.form.DateField({
				id:'fromdatefield',
                format: gettext('m/d/Y'),
                cancelText: gettext('cancel'),
                fieldLabel: gettext('From'),
                name: 'fromDate',
				disabled:true
            });
            
            var todatefield = new Ext.form.DateField({
				id:'todatefield',
                format: gettext('m/d/Y'),
                fieldLabel: gettext('To'),
                name: 'toDate',
				disabled:true
            });
			
            var tagcloud = new Ext.Panel({
                id: 'tagcloud',
                title: '',
                bodyStyle: 'background-color:#EBEBEB;padding:5px;margin:10px;text-align:center;	border:1px solid #D0D0D0;', 
                html: 'tag cloud goes here'
			}) ; 
			
            var tagcloudresetfilterbtn = new Ext.Panel({
				id:'tagcloudreset',
                layout: 'column',
                border: false,
                title: '',
	                    items: [{
	                        columnWidth: .40,
	                        html: '&nbsp;',
	                        border: false
	                    }, {
	                        columnWidth: .20,
	                        layout: 'form',
	                        border: false,
	                        items: [{
	                            xtype: 'button',
	                            id: 'tagcloud_view_comments',
			                    text: gettext("All comments")
	                        }]
	                    }, {
	                        columnWidth: .40,
	                        html: '&nbsp;',
	                        border: false
	                    }]
			}) ;
			
            var filter = new Ext.FormPanel({
                id: 'filterform',
                frame: false,
                title: '',
                bodyStyle: 'padding:5px 5px 0", //;border:none;',
                items: 
					[{
	                    xtype: 'fieldset',
	                    id: 'textfieldset',
	                    title: gettext('Text'),
	                    collapsible: false,
	                    autoHeight: true,
	                    items: [{
                        layout: 'table',
                        border: false,
                        items: [
							{	html: gettext('Search') + '&nbsp;',border: false},
							{
                                xtype: 'textfield',
                                name: 'home1',
								id:'textsearchfor',
								hideLabel:true,
                                width: 170
                            },
							{	html: '&nbsp;' + gettext('in') + '&nbsp;',border: false},
							textfilterselect, 
	                        {
                                xtype: 'button',
                                id: 'simplefilter_apply_btn',
                                text: gettext("Apply Filter")
	                        },
							{	html: '&nbsp;',border: false},
							{
	                            xtype: 'button',
	                            id: 'simplefilter_view_comments',
			                    text: gettext("All comments")
	                        }
						]}
					]}, 
					{
	                    xtype: 'fieldset',
	                    id: 'datefieldset',
	                    title: gettext('Date'),
	                    collapsible: false,
	                    autoHeight: true,
	                    layout: 'column',
	                    border: true,
	                    items: [{
		                        columnWidth: .34,
		                        layout: 'form',
		                        border: false,
								labelWidth: 10,
		                        items: [datefilterselect]
	                    	}, {
		                        columnWidth: .33,
		                        layout: 'form',
		                        border: false,
		                        items: [fromdatefield]
							}, {
								columnWidth: .33,
								layout: 'form',
								border: false,
								items: [todatefield]
							}
						]
	                }, {
	                    xtype: 'fieldset',
	                    id: 'statefieldset',
	                    title: gettext('States'),
	                    collapsible: false,
	                    autoHeight: true,
	                    layout: 'column',
	                    border: true,
	                    items: [{
	                        columnWidth: .25,
	                        layout: 'form',
	                        border: false,
	                        html: '&nbsp;'
	                    }, {
	                        columnWidth: .5,
	                        layout: 'form',
	                        border: false,
	                        items: [statefilterselect]
	                   }, {
	                        columnWidth: .25	,
	                        layout: 'form',
	                        border: false,
	                        html: '&nbsp;'
	                    }]
	                }, {id : 'adv_btn_section',
	                    layout: 'column',
	                    border: false,
	                    items: [{
	                        columnWidth: .35,
	                        html: '&nbsp;',
	                        border: false
	                    }, {
	                        columnWidth: .4,
	                        layout: 'table',
							layoutConfig: {columns: 3},							
	                        border: false,
	                        items: [{
	                            xtype: 'button',
	                            id: 'advfilter_apply_btn',
	                            text: gettext("Apply Filter")
	                        },{html: '&nbsp;',border: false},
							{
	                            xtype: 'button',
	                            id: 'advfilter_view_comments',
			                    text: gettext("All comments")
	                        }]
	                    }, {
	                        columnWidth: .25,
	                        html: '&nbsp;',
	                        border: false
	                    }]
	                }
				]
            });
            
            var autoHeight_embeded = true ;
            var attachsWidth_embeded = 360 ;
            var filterheight_embeded = 'auto' ;
            var collapsed_embeded = false ;
            if (sv_embeded) {
	            filterheight_embeded = 0 ;
	            attachsWidth_embeded = 250 ;
	            autoHeight_embeded = false ;
            	collapsed_embeded = true ;
	        }
            
            this.viewport = new Ext.Viewport({
                layout: 'border',
                border: false,
                items: [new Ext.BoxComponent({
                    region: 'north',
                    border: false,
                    el: 'client_header',
                    margins: '0 0 0 0',
                    height: 22
                }), {
                    layout: 'border',
                    region: 'center',
                    listeners: this.LinkInterceptor,
                    border: false,
                    items: [  {
                        id: 'filter_top',
                        region: 'north',
                        height:filterheight_embeded,
                        autoHeight:autoHeight_embeded,
                        margins: '0 0 0 0',
                        layout: 'column',
                        items: [{
                           id: "filter_left_col",
                             columnWidth: .5
                        }, {
                            width: 800,
                            border: false,
                            items: [tagcloud, filter, tagcloudresetfilterbtn]
                        
                        }, {
                            id: "filter_right_col",
                            columnWidth: .5
                        }]
                    },{
                        title: gettext('Comments')+'&nbsp;&nbsp;<a id="view_all_comments" href="#">'+gettext('View all')+'</a>&nbsp;&nbsp;<a id="mail_sub" href="#" title=""></a>',
                        id:'attachsregion',
                        border: false,
                        collapsible: true,
                        floatable:false,
                        collapsed:collapsed_embeded,
                        region: 'west',
                        split: true,
                        margins: '0 0 0 0',
                        width: attachsWidth_embeded,
                        minSize: 100,
                        maxSize: 500,
                        layout: 'fit',
                        //items:[{region:'north', minHeight:50, border:false, split:true, items:[tabs2]}, {region:'center', border:false, split:true, items:[tabs3]}]
                        items: [this.attachsTabPanel]
                    
                    }, {
                        id:'text_frame',
                        region: 'center',
                        border: false,
                        margins: '0 0 0 0',
                        layout: 'fit',
                        contentEl: 'frameContainer'
                    }]
                }]
            });
			
            Ext.ComponentMgr.get('fromdatefield').setValue(new Date('1/1/2007'));
            Ext.ComponentMgr.get('todatefield').setValue(new Date('1/1/2100'));
			
			statefilterselect.setValue(core.TextMgr.getWorkflowStateValues()) ;
			textfilterselect.setValue('text_and_title') ;
			//this.showSimpleFilter() ;
			this.showNoFilter() ;
        };
			
        this.activateAttachListTab = function(){
            core.LayoutMgr.attachsTabPanel.setActiveTab('attachsPanel');
        };
        
        this.activateAddAttachTab = function(){
            core.LayoutMgr.attachsTabPanel.setActiveTab('addAttachPanel');
        };
        
        this.hideEditAttachTab = function(){
	        if (Ext.ComponentMgr.get('editAttachPanel')) {        
				this.attachsTabPanel.hideTabStripItem('editAttachPanel') ;
				Ext.ComponentMgr.get('editAttachPanel').hide() ;
				// hum...
				this.activateAttachListTab() ;
			}
        };
		
        this.unhideEditAttachTab = function(){
	        if (Ext.ComponentMgr.get('editAttachPanel')) {        
				this.attachsTabPanel.unhideTabStripItem('editAttachPanel') ;
				Ext.ComponentMgr.get('editAttachPanel').show() ;
				// hum...
				this.activateEditAttachTab() ;
			}
        };
		
        this.activateEditAttachTab = function(){
            core.LayoutMgr.attachsTabPanel.setActiveTab('editAttachPanel');
        };
        
        this.updatePanelTitle = function(id, title){
			var panel = Ext.ComponentMgr.get(id)
            if (panel) 
            if (panel) {
                panel.setTitle(title);
            }
        };
        
        this.changeButtonHandler = function(pref, handler, scope){
			var btnId = pref + "_btn" ;
			var btn = Ext.ComponentMgr.get(btnId) ;
            if (btn) 
                btn.setHandler(handler, scope);
        };
        
        this.displayInfoMsg = function(txt){
            if (this.opt) {
                if (this.opt.anim.isAnimated()) 
                    this.opt.anim.stop();
            }
            else {
                this.opt = {
                    duration: 6,
                    method: 'easeInSTrong',
                    scope: this
                };
            }
            
            this.infoMsgElt.setStyle({
                'background-color': '#3BE620'
            });
            
            this.infoMsgElt.update(txt);
            this.infoMsgElt.setVisible(true);
            this.infoMsgElt.setVisible(false, this.opt);
        };
        
        this.displayErrorMsg = function(txt){
            if (this.erroropt) {
                if (this.erroropt.anim.isAnimated()) 
                    this.erroropt.anim.stop();
            }
            else {
                this.erroropt = {
                    duration: 6,
                    method: 'easeInSTrong',
                    scope: this
                };
            }
            
            this.errorMsgElt.setStyle({
                'background-color': '#F00'
            });
            
            this.errorMsgElt.update(txt);
            this.errorMsgElt.setVisible(true);
            this.errorMsgElt.setVisible(false, this.erroropt);
        };
        
        this.showNoFilter = function(isSimple){
	        this.showSimpleOrAdvanceFilter(true) ;
			
			Ext.ComponentMgr.get('textfieldset').setVisible(false) ;
			
			this.doLayout(); 
		};
		
        this.showSimpleFilter = function(){
			this.showSimpleOrAdvanceFilter(true) ;

			this.doLayout(); 
		};
		
        this.showAdvanceFilter = function(){
			this.showSimpleOrAdvanceFilter(false) ;

			this.doLayout(); 
		};
		
        this.showTagCloudFilter = function(){
			this.showTagCloudOrFilter(true) ;
						
			Ext.ComponentMgr.get('textfieldset').setVisible(false) ;
			
			this.doLayout(); 
		};
		
        this.showTagCloudOrFilter = function(isTagCloud){
			Ext.ComponentMgr.get('filterform').setVisible(!isTagCloud) ;

			Ext.ComponentMgr.get('tagcloud').setVisible(isTagCloud) ;
			Ext.ComponentMgr.get('tagcloudreset').setVisible(isTagCloud) ;
		};
		
        this.showSimpleOrAdvanceFilter = function(isSimple){
			this.showTagCloudOrFilter(false) ;
						
			Ext.ComponentMgr.get('textfieldset').setVisible(true) ;

			Ext.ComponentMgr.get('simplefilter_apply_btn').setVisible(isSimple) ;
			Ext.ComponentMgr.get('simplefilter_view_comments').setVisible(isSimple) ;

			Ext.ComponentMgr.get('adv_btn_section').setVisible(!isSimple) ;
			Ext.ComponentMgr.get('datefieldset').setVisible(!isSimple) ;
			
			if (sv_manageComPerm)
				Ext.ComponentMgr.get('statefieldset').setVisible(!isSimple) ;
			else 
				Ext.ComponentMgr.get('statefieldset').setVisible(false) ;
		};
		
        this.getInitialSelectionContent = function(){
            return this._initialSelectionContent;
        };
        
        this.updateMailLnk = function(){
        	if (sv_loggedIn) {
		        var mailSubTxt = (!sv_mailsub) ? gettext('Subscribe'):gettext('Unsubscribe');
		        var mailSubTitle = (!sv_mailsub) ? gettext('Click to receive email notifications when this text is changed or when a comment is added'):gettext('Click to unsubscribe from email notifications');
		        var elt = Ext.get('mail_sub') ;
		        elt.update(mailSubTxt) ;
		        elt.set({'title':mailSubTitle}) ;
        	}
        };
        
        // for links in comments content
        this.LinkInterceptor = {
            render: function(p){
                p.body.on({
                    'mousedown': function(e, t){ // try to intercept the easy way
                        t.target = '_blank';
                    },
                    'click': function(e, t){ // if they tab + enter a link, need to do it old fashioned way
                        if (String(t.target).toLowerCase() != '_blank') {
                            e.stopEvent();
                            window.open(t.href);
                        }
                    },
                    delegate: 'a'
                });
            }
        };
    }
}
