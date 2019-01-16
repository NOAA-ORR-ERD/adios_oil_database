define([
    'jquery',
    'underscore',
    'backbone',
    'sweetalert',
    'toastr',
    'text!templates/default/menu.html',
    'views/modal/about',
    'views/modal/hotkeys',
    'bootstrap'
 ], function($, _, Backbone, swal, toastr,
             MenuTemplate, AboutModal, HotkeysModal) {
    'use strict';
    //
    // `MenuView` handles the drop-down menus on the top of the page.
    // The object listens for click events on menu items and fires
    // specialized events, like RUN_ITEM_CLICKED, which an `AppView` object
    // listens for.
    //
    // Most of these functions exist elsewhere in the application and `AppView`
    // calls the appropriate method for whatever functionality the user invoked.
    //

    var menuView = Backbone.View.extend({
        tagName: 'nav',
        className: 'navbar navbar-default navbar-fixed-top',

        initialize: function() {
            this.render();
            this.contextualize();
            this.listenTo(weboillib.router, 'route', this.contextualize);
        },

        events: {
            'click a.debugView': 'debugView',
            'click .navbar-brand': 'home',

            // "new" menu
            //'click .locations': 'locations',

            // "Save" optional menu items
            //'click .save': 'save',

            //"help" menu
            'click .about': 'about',
            'click .doc': 'doc',
            'click .faq': 'faq',
            'click .hotkeys': 'hotkeys',

            //export menu
            //'click .netcdf': 'netcdf',

            'click .app-menu-link': 'openAppMenu',
            'click .app-menu-close': 'closeAppMenu',

            'click .view-toggle .view': 'toggleView'
        },

        toggleView: function(e){
            var view;

            if (_.isObject(e)) {
                view = this.$(e.target).attr('class').replace('view ', '');
                this.$('.view-toggle .switch').attr('class', 'switch ' + view);

                weboillib.router.navigate(view, true);
            } else {
                view = e;
                this.$('.view-toggle .switch').attr('class', 'switch ' + e);
            }

            this.$('.view-toggle .switch').attr('data-original-title',
                                                this.$('.view-toggle .' + view)
                                                    .data('original-title'));
        },

        openAppMenu: function(event){
            event.preventDefault();
            this.$('.app-menu').addClass('open');
            this.$('.app-menu-close').addClass('open');
            this.$('.app-menu').focus();
        },

        closeAppMenu: function(){
            this.$('.app-menu').removeClass('open');
            this.$('.app-menu-close').removeClass('open');
        },

        nothing: function(event){
            event.preventDefault();
        },

        home: function(event){
            event.preventDefault();
            weboillib.router.navigate('', true);
        },

        debugView: function(event){
            event.preventDefault();
            var checkbox = this.$('input[type="checkbox"]');
            if (checkbox.prop('checked')) {
                checkbox.prop('checked', false);
            } else {
                checkbox.prop('checked', true);
                //this.trigger('debugTreeOn');
            }
            this.trigger('debugTreeToggle');
        },

        about: function(event){
            event.preventDefault();
            new AboutModal().render();
        },

        doc: function(event){
            event.preventDefault();
            window.open("doc/");
        },

        faq: function(event){
            event.preventDefault();
            window.open("#faq");
        },

        hotkeys: function(event){
            event.preventDefault();
            new HotkeysModal().render();
        },

        enableMenuItem: function(item){
            this.$el.find('.' + item).show();
        },

        disableMenuItem: function(item){
            this.$el.find('.' + item).hide();
        },

        contextualize: function(){
            this.enableMenuItem('save');
            this.enableMenuItem('edit');
        },

        render: function(){
            var compiled = _.template(MenuTemplate);
            $('body').append(this.$el.html(compiled({'can_persist': weboillib.config.can_persist})));

            this.$('a').tooltip({
                placement: 'right',
                container: 'body'
            });

            this.$('.view-toggle .view').tooltip({
                placement: 'bottom',
                container: 'body'
            });

            this.$('.view-toggle .switch').tooltip({
                placement: 'bottom'
            });
        },

        close: function(){
            $('.sweet-overlay').remove();
            $('.sweet-alert').remove();

            Backbone.View.prototype.close.call(this);
        }
    });

    return menuView;
});
