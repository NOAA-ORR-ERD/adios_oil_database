define([
    'jquery',
    'underscore',
    'backbone',
    'views/default/help',
    'views/modal/help'
], function($, _, Backbone, HelpView, HelpModal) {
    'use strict';
    var baseView = Backbone.View.extend({
        events: {
            'click .oillib-help': 'renderHelp'
        },

        initialize: function() {
            if (this.module) {
                this.help = new HelpView({path: this.module.id,
                                          context: 'view'});
            }
        },

        render: function() {
            if (this.module) {
                if (this.help.ready) {
                    this.showHelp();
                }
                else {
                    this.help.on('ready', this.showHelp, this);
                }
            }
        },

        renderHelp: function(options) {
            options = _.defaults(options, {
                help: this.help
            });

            var modal = new HelpModal(options);

            modal.render();
        },
    });

    return baseView;
});
