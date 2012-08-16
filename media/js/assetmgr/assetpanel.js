var AssetPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    
    self.el = el;
    self.panel = panel;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    
    djangosherd.storage.json_update(panel.context);
    
    jQuery(self.el).find("div.tabs").tabs();
    
    jQuery(window).resize(function () {
        self.resize();
    });
    
    // Fired by CollectionList & AnnotationList
    jQuery(window).bind('asset.on_delete', { 'self': self },
        function (event, asset_id) { event.data.self.onDeleteItem(asset_id); });

    //jQuery(window).bind('asset.edit', { 'self': self }, self.dialog);
    //jQuery(window).bind('annotation.create', { 'self': self }, self.dialog);
    //jQuery(window).bind('annotation.edit', { 'self': self }, self.dialog);
    
    
    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': "asset-workspace-videoclipbox",
        'presentation': "medium",
        'clipform': true,
        'autoplay': false,
        'winHeight': function () {
            var elt = jQuery(self.el).find("div.asset-view-published")[0];
            return jQuery(elt).height() -
                (jQuery(elt).find("div.annotation-title").height() + jQuery(elt).find("div.asset-title").height() + 15);
        }
    });
    
    if (self.panel.show_collection) {
        self.collectionList = new CollectionList({
            'parent': self.el,
            'template': 'gallery',
            'template_label': "media_gallery",
            'create_annotation_thumbs': false,
            'create_asset_thumbs': true,
            'space_owner': self.space_owner,
            'view_callback': function () {
                jQuery(self.el).find("a.asset-title-link").bind("click", { self: self }, self.onClickAssetTitle);
                jQuery(self.el).find("a.edit-asset-inplace").bind("click", { self: self }, self.editItem);
                
                var container = jQuery(self.el).find('div.asset-table')[0];
                jQuery(container).masonry({
                    itemSelector : '.gallery-item',
                    columnWidth: 25
                });
                
                jQuery(window).trigger("resize");
            }
        });
    }
    
    if (self.panel.current_asset) {
        self.showAsset(self.panel.current_asset, self.panel.current_annotation);
    }
    
    jQuery(window).trigger("resize");
};

AssetPanelHandler.prototype.closeDialog = function (event) {
    var self = event.data.self;
    
};

AssetPanelHandler.prototype.dialog = function (event, assetId, annotationId) {
    var self = event.data.self;
    
    var element = jQuery("#asset-workspace-panel-container")[0];
    
    var title = "Edit Item";
    if (event.type === "annotation") {
        if (event.namespace === "create") {
            title = "Create Selection";
        } else {
            title = "Edit Selection";
        }
    }
        
    self.dialog = jQuery(element).dialog({
        open: function () {
            self.citationView.openCitationById(null, assetId, annotationId);
            
            // Setup the edit view
            AnnotationList.init({
                "asset_id": assetId,
                "annotation_id": annotationId,
                "edit_state": event.type === "annotation" && event.namespace === "create" ? "new" : "",
                "update_history": false
            });
        },
        title: title,
        draggable: true,
        resizable: false,
        modal: true,
        width: 934,
        position: "top",
        zIndex: 10000
    });
    
    return false;
};


AssetPanelHandler.prototype.showAsset = function (asset_id, annotation_id) {
    var self = this;
    
    self.current_asset = parseInt(asset_id, 10);
    
    jQuery(self.el).find('td.panel-container.collection').removeClass('maximized').addClass('minimized');
    jQuery(self.el).find('td.pantab-container').removeClass('maximized').addClass('minimized');
    jQuery(self.el).find('div.pantab.collection').removeClass('maximized').addClass('minimized');
    jQuery(self.el).find('td.panel-container.asset').removeClass("closed").addClass("open");
    jQuery(self.el).find('td.panel-container.asset').show();
    jQuery(self.el).find('td.panel-container.asset-details').show();
    
    self.citationView.openCitationById(null, asset_id, annotation_id);
    
    jQuery(self.el).find("a.filterbyclasstag").unbind();

    // Setup the edit view
    AnnotationList.init({
        "asset_id": asset_id,
        "annotation_id": annotation_id,
        "update_history": self.panel.update_history,
        "view_callback": function () {
            jQuery(self.el).find("a.filterbyclasstag").bind("click", { self: self }, self.onFilterByClassTag);
            
            jQuery(self.el).find("div.tabs").fadeIn("fast", function () {
                PanelManager.verifyLayout(self.el);
                jQuery(window).trigger("resize");
            });
        }
    });
};

AssetPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();

    visible -= 10;
    
    // Resize the collections box, subtracting its header elements
    var collectionHeight = visible - jQuery(self.el).find("div.filter-widget").height();
    jQuery(self.el).find('div.collection-assets').css('height', collectionHeight + "px");
    
    visible -= jQuery("div.asset-view-title").height();
    jQuery(self.el).find('div.asset-view-container').css('height', (visible) + "px");
    jQuery(self.el).find('div.asset-view-published').css('height', (visible + 4) + "px");
    jQuery(self.el).find('div.asset-view-tabs').css('height', (visible) + "px");
    
    visible -= jQuery('ul.ui-tabs-nav').height() + jQuery("div#asset-global-annotation").outerHeight() + 30;
    jQuery(self.el).find('div#annotations-organized').css('height', (visible) + "px");
    jQuery("div.accordion").accordion("resize");
};

AssetPanelHandler.prototype.onClickAssetTitle = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    
    var bits = srcElement.href.split('/');
    self.showAsset(bits[bits.length - 2]);
        
    return false;
};

AssetPanelHandler.prototype.editItem = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    
    var bits = srcElement.parentNode.href.split('/');
    self.showAsset(bits[bits.length - 2]);
    return false;
};

AssetPanelHandler.prototype.onDeleteItem = function (asset_id) {
    var self = this;
    
    // if the item being deleted was the current one, then close up shop & show the full asset view
    if (typeof asset_id === "string") {
        asset_id = parseInt(asset_id, 10);
    }
    
    if (asset_id === self.current_asset) {
        self.showAsset(self.current_asset);
    }
};

AssetPanelHandler.prototype.onFilterByClassTag = function (evt) {
    var self = evt.data.self;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var bits = srcElement.href.split("/");
    
    self.collectionList.filterByClassTag(bits[bits.length - 1]);
    
    return false;
};