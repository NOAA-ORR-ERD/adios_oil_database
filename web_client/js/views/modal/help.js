define([
    'jquery',
    'underscore',
    'backbone',
    'views/modal/base',
], function($, _, Backbone, BaseModal) {
    'use strict';
    var helpModal = BaseModal.extend({
        name: 'oillib-help',
        size: 'md',
        title: 'Help',
        buttons: '<button type="button" class="cancel" data-dismiss="modal">Close</button>',

        initialize: function(options) {
            BaseModal.prototype.initialize.call(this, options);

            if (_.has(options, 'help')) {
                options.help.delegateEvents();
                this.body = options.help.$el;
                this.title = this.body.find('.title:first').text() + ' Help';
            }
            else {
                this.body = 'No help documentation found!';
            }
        },
    });

    return helpModal;
});
