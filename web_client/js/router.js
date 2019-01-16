define([
    'jquery',
    'underscore',
    'backbone',
    'views/default/index',
    'views/default/menu',
    'views/default/footer',
    'views/default/overview',
    'views/default/faq',
    'views/default/notfound',
    'views/form/oil/library'
], function($, _, Backbone,
            IndexView, MenuView, FooterView,
            OverviewView, FAQView, NotFoundView,
            OilLibraryView) {
    'use strict';
    var Router = Backbone.Router.extend({
        views: [],
        name: 'Main',
        routes: {
            '': 'index',
            'config': 'config',
            'overview': 'overview',
            'faq': 'faq',
            'faq/:title': 'faq',
            
            'query': 'query',

            '*actions': 'notfound'
        },

        execute: function(callback, args) {
            for (var view in this.views) {
                $('.tooltip').remove();
                this.views[view].close();
            }
            this.views = [];

            if (callback) { callback.apply(this, args); }

            if (window.location.href.indexOf('trajectory') === -1 ||
                    weboillib.model.get('mode') === 'adios' ||
                    weboillib.model.get('mode') === 'roc') {
                this.views.push(new FooterView());
            }
        },

        index: function() {
            this.menu('remove');
            this.views.push(new IndexView());
        },

        overview: function(){
            this.menu('add');
            this.views.push(new OverviewView());
        },

        faq: function(title){
            this.menu('remove');
            if (!_.isUndefined(title)){
                this.views.push(new FAQView({topic: title}));
            } else {
                this.views.push(new FAQView());
            }
        },

        query: function(){
            this.menu('add');
            this.views.push(new OilLibraryView());
        },

        notfound: function(actions){
            this.menu('add');
            this.views.push(new NotFoundView());
            console.log('Not found:', actions);
        },

        menu: function(action){
            switch (action){
                case 'add':
                    if (!this.menuView) {
                        this.menuView = new MenuView();
                    }
                    break;
                case 'remove':
                    if (this.menuView) {
                        this.menuView.remove();
                        delete this.menuView;
                    }
                    break;
            }
        },
        
        _cleanup: function() {
            // Cleans up parts of the website (such as trajectory view) when necessary
            if (!_.isUndefined(weboillib.router.trajView)) {
                this.trajView.viewer.destroy();
                this.trajView.stopListening();
                this.trajView.remove();
                this.trajView = undefined;
            }
        }

    });

    return Router;
});
