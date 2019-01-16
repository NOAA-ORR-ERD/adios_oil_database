define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/default/footer/footer.html',
    'text!templates/default/footer/disclaimer.html',
    'text!templates/default/footer/privacy.html',
    'text!templates/default/footer/troubleshooting.html',
    'views/modal/base'
], function($, _, Backbone,
            FooterTemplate, DisclaimerTemplate, PrivacyTemplate,
            TroubleShootingTemplate, BaseModal) {
    'use strict';
    var footerView = Backbone.View.extend({
        className: 'footer',
        rendered: false,
        modalButtons: '<a href="" class="btn btn-primary" data-dismiss="modal">Ok</a>',

        events: {
            'click .disclaimer': 'disclaimer',
            'click .privacy': 'privacy',
            'click .help': 'helpPopup'
        },

        initialize: function() {
            if($('body > .footer').length < 1) {
                this.render();
            }
        },

        render: function() {
            this.rendered = true;
            var compiled = _.template(FooterTemplate);
            this.$el.append(compiled);
            $('body').append(this.$el);
        },

        disclaimer: function(e) {
            e.preventDefault();
            var modal = new BaseModal({
                title: 'Disclaimer',
                body: DisclaimerTemplate,
                buttons: this.modalButtons
            });
            modal.render();
        },

        privacy: function(e) {
            e.preventDefault();
            var modal = new BaseModal({
                title: 'Privacy Policy',
                body: PrivacyTemplate,
                buttons: this.modalButtons
            });
            modal.render();
        },

        helpPopup: function(e) {
            e.preventDefault();
            var modal = new BaseModal({
                title: 'Trouble Shooting',
                body: TroubleShootingTemplate,
                buttons: this.modalButtons
            });
            modal.render();
        }
    });

    return footerView;
});
