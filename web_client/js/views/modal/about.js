define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/modal/about.html',
    'views/modal/base',
], function($, _, Backbone,
            AboutTemplate, BaseModal) {
    'use strict';
    var aboutModal = BaseModal.extend({
        name: 'about',
        size: 'sm',
        title: 'About WebOilLibrary&reg;',
        buttons: '<button type="button" class="cancel" data-dismiss="modal">Ok</button>',

        initialize: function() {
            var compiled = _.template(AboutTemplate,
                                      {'email': 'oillibrary.help@noaa.gov'});
            this.body = compiled;
            BaseModal.prototype.initialize.call(this);
        }
    });

    return aboutModal;
});