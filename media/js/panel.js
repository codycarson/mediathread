(function () {

    window.PanelFactory = new (function PanelFactoryAbstract() {
        this.create = function (el, parent, type, panels, space_owner) {
            // Instantiate the panel's handler
            var handler = null;
            if (type === "project") {
                handler = new ProjectPanelHandler(el, parent, panels, space_owner);
            } else if (type === "discussion") {
                handler = new DiscussionPanelHandler(el, parent, panels, space_owner);
            }
            
            return handler;
        };
    })();
    
    window.PanelManager = new (function PanelManagerAbstract() {
        var self = this;
      
        this.init = function (options, panels) {
            self.options = options;
            self.panelHandlers = [];
            self.el = jQuery("#" + options.container)[0];

            jQuery(self.el).ajaxStop(function () {
                jQuery(this).removeClass("ajaxLoading");
            });

            
            // Create an assetview.
            // @todo - We have potentially more than 1 assetview on the project page. The singleton nature in the
            // core architecture means the two views are really sharing the underlying code.
            // Consider how to resolve this contention. (It's a big change in the core.)
            
            // This may be DANGEROUS in any sense. The old assetview should be destroyed first?
            if (!djangosherd.assetview) {
                djangosherd.assetview = new Sherd.GenericAssetView({ clipform: false, clipstrip: true});
            }
            
            if (!djangosherd.storage) {
                djangosherd.storage = new DjangoSherd_Storage();
            }
            
            jQuery.ajax({
                url: options.url,
                dataType: 'json',
                cache: false, // Chrome && Internet Explorer has aggressive caching policies.
                success: function (json) {
                    self.panels = json.panels;
                    self.space_owner = json.space_owner;
                    self.loadTemplates(0);
                }
            });
            
            jQuery(window).resize(function () {
                self.resize();
            });
        };
        
        this.count = function() {
            return self.panelHandlers.length;
        };
        
        this.resize = function () {
            var visible = getVisibleContentHeight();
            jQuery(self.el).css('height', visible + "px");
        };
        
        this.loadTemplates = function (idx) {
            if (idx === self.panels.length) {
                // done. load content.
                self.loadContent();
                
            } else if (MediaThread.templates[self.panels[idx].template]) {
                // it's already cached
                self.loadTemplates(++idx);
            } else {
                // pull it off the wire
                jQuery.ajax({
                    url: '/site_media/templates/' + self.panels[idx].template + '.mustache?nocache=v3',
                    dataType: 'text',
                    cache: false, // Chrome && Internet Explorer have aggressive caching policies.
                    success: function (text) {
                        MediaThread.templates[self.panels[idx].template] = Mustache.template(self.panels[idx].template, text);
                        self.loadTemplates(++idx);
                    }
                });
            }
        };
        
        this.loadContent = function () {
            for (var i = 0; i < self.panels.length; i++) {
                var panel = self.panels[i];
                if (!panel.hasOwnProperty("loaded")) {
                 
                    // Add these new columns to the table, before the last column
                    // The last column is reserved for a placeholder td that eats space
                    // and makes the sliding UI work nicely
                    var lastCell = jQuery("#" + self.options.container + " tr:first td:last");
                    lastCell.before(Mustache.tmpl(panel.template, panel));
                    
                    var newCell = jQuery(lastCell).prev().prev()[0];
                    var handler = PanelFactory.create(newCell, self.el, self.panels[i].context.type, self.panels[i], self.space_owner);
                    self.panelHandlers.push(handler);
                    
                    // enable open/close controls on subpanel
                    jQuery(newCell).find(".pantab-container").bind('click',
                        { handler: handler, isSubpanel: true },
                        function (event) {
                            self.slidePanel(this, event);
                        }
                    );
                    
                    // enable open/close controls on parent panels
                    jQuery(newCell).next(".pantab-container").bind('click',
                        { handler: handler, isSubpanel: false },
                        function (event) {
                            self.slidePanel(this, event);
                        }
                    );
                    
                    // @todo -- update history to reflect this new view
                    
                    panel.loaded = true;
                    
                    self.verifyLayout(newCell);
                }
            }
        };
        
        this.slidePanel = function (pantab_container, event) {
            // Open/close this panhandle's panel
            var panel = jQuery(pantab_container).prevAll("td.panel-container")[0];
            
            var param = jQuery(panel).hasClass("open") ? "closed" : "open";
            jQuery(panel).toggleClass("open closed");
            jQuery(panel).trigger('panel_state_change', [ param ]);
            
            var panelTab = jQuery(pantab_container).children("div.pantab")[0];
            jQuery(panelTab).toggleClass("open closed");
            
            self.verifyLayout(panel);
            jQuery(window).trigger("resize");
            
            /** Fade
            if (jQuery(panel).hasClass("open")) {
                jQuery(panel).removeClass("open");
                jQuery(panel).fadeOut("slow", function () {
                    jQuery(panel).addClass("closed");
                });
            } else {
                jQuery(panel).removeClass("closed");
                jQuery(panel).fadeIn("slow", function () {
                    jQuery(panel).addClass("open");
                });
            }
            **/
            
            /** Real Sliding
            // Open/close this panhandle's panel
            var div = jQuery(panel).children('div.panel');
            var panelTab = jQuery(pantab_container).children("div.pantab")[0];
            
            if (jQuery(panel).hasClass("open")) {
                jQuery(panelTab).fadeOut();
                jQuery(panel).css("background-color", "white !important");
                jQuery(div).hide("slide", { direction: "left" }, 500, function () {
                    jQuery(panel).toggleClass("open closed");
                    jQuery(panelTab).toggleClass("open closed");
                    jQuery(panelTab).fadeIn("fast");
                });
            } else {
                jQuery(div).show("slide", { direction: "left" }, 1000, function () {
                    jQuery(panel).toggleClass("open closed");
                });
            }
            **/
        };
        
        this.openSubPanel = function (subpanel) {
            if (subpanel) {
                jQuery(subpanel).removeClass("closed").addClass("open");
                jQuery(subpanel).trigger('panel_state_change', [ 'open' ]);
                
                var container = jQuery(subpanel).nextAll("td.pantab-container");
                var panelTab = jQuery(container[0]).children("div.pantab");
                jQuery(panelTab[0]).removeClass("closed");
                jQuery(panelTab[0]).addClass("open");
                
                self.verifyLayout(subpanel);
                jQuery(window).trigger("resize");
            }
        };

        this.closeSubPanel = function (view) {
            var subpanel = jQuery(view.el).find("td.panel-container.open")[0];
            
            jQuery(subpanel).removeClass("open").addClass("closed");
            jQuery(subpanel).trigger('panel_state_change', [ 'closed' ]);
            
            var panelTab = jQuery(subpanel).next().next().children("div.pantab")[0];
            jQuery(panelTab).toggleClass("open closed");
            
            self.verifyLayout(subpanel);
            jQuery(window).trigger("resize");
        };
                
        this.verifyLayout = function (panel) {
            var screenWidth = jQuery(window).width();
            var tableWidth = jQuery(self.el).width();
            
            var elts = jQuery(panel).parents("td.panel-container.open");
            var parent = elts.length > 0 ? elts[0] : null;

            // Try closing the subpanels first
            var a = jQuery(self.el).find("table.panel-subcontainer tbody tr td.panel-container.open");
            for (var i = 0; i < a.length && tableWidth > screenWidth; i++) {
                var p = a[i];
                if (panel !== p) {
                    // close it
                    jQuery(p).removeClass("open").addClass("closed");
                    jQuery(p).trigger('panel_state_change', [ 'closed' ]);
                    
                    var container = jQuery(p).nextAll("td.pantab-container");
                    var panelTab = jQuery(container[0]).children("div.pantab");
                    jQuery(panelTab[0]).removeClass("open").addClass("closed");
                    
                    tableWidth = jQuery(self.el).width();
                }
            }
            
            // Then go for the parent panels
            a = jQuery(self.el).find("tr.sliding-content-row").children("td.panel-container.open");
            for (i = 0; i < a.length && tableWidth > screenWidth; i++) {
                
                if (a[i] !== panel && a[i] !== parent) {
                    // close it
                    jQuery(a[i]).removeClass("open").addClass("closed");
                    jQuery(a[i]).trigger('panel_state_change', [ 'closed' ]);
                    
                    var parentContainer = jQuery(a[i]).nextAll("td.pantab-container")[0];
                    var parentPanelTab = jQuery(parentContainer).children("div.pantab")[0];
                    jQuery(parentPanelTab).removeClass("open").addClass("closed");
                    
                    tableWidth = jQuery(self.el).width();
                }
            }
        };
        
        this.newPanel = function (options) {
            jQuery.ajax({
                type: 'POST',
                url: options.url,
                dataType: 'json',
                data: options.params,
                success: function (json) {
                    if (options.callback) {
                        options.callback(json);
                    } else {
                        var length = self.panels.push(json);
                        self.loadTemplates(length - 1);
                    }
                }
            });
        };
        
        this.openPanel = function (panel) {
            // Open this panel
            if (jQuery(panel).hasClass("closed")) {
                jQuery(panel).removeClass("closed").addClass("open");
                jQuery(panel).trigger('panel_state_change', [ 'open' ]);
                
                var panelTab = jQuery(panel).next().children("div.pantab")[0];
                jQuery(panelTab).toggleClass("open closed");
                
                self.verifyLayout(panel);
            }
        };

        
    })();
})();

