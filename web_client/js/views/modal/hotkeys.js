define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/modal/hotkeys.html',
    'views/modal/base'
], function($, _, Backbone,
            HotkeysTemplate, BaseModal) {
    'use strict';
    var hotkeysModal = BaseModal.extend({
        name: 'hotkeys',
        size: 'sm',
        title: 'Trajectory Hotkeys',
        body: _.template(HotkeysTemplate),
        buttons: '<button type="button" class="cancel" data-dismiss="modal">Ok</button>'
    });

    return hotkeysModal;
});