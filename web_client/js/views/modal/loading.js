define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/modal/loading.html',
    'views/modal/base'
], function($, _, Backbone, LoadingTemplate, BaseModal) {
    'use strict';
    var loadingModal = BaseModal.extend({
        name: 'loading',
        size: 'sm',
        title: 'Loading...',
        body: _.template(LoadingTemplate),
        buttons: '',

        render: function() {
            BaseModal.prototype.render.call(this);
            this.$('.close').hide();
            this.$('.modal-footer').hide();
        }
    });

    return loadingModal;
});
