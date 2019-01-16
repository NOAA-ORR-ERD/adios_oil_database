define([
    'jquery',
    'underscore',
    'backbone',
    'moment',
    'text!templates/default/alert-danger.html',
    'views/modal/base',
    'views/form/base',
    'views/default/help',
    'views/attributes/attributes'
], function($, _, Backbone, moment,
            AlertDangerTemplate, BaseModal, BaseForm, HelpView, AttributesView) {
    'use strict';
    var PseudoMultipleInheritance = BaseForm.extend(BaseModal.prototype);

    var formModal = PseudoMultipleInheritance.extend({
        className: 'modal form-modal',
        buttons: '<button type="button" class="cancel" data-dismiss="modal">Cancel</button>' +
                 '<button type="button" class="save">Save</button>',
        form: [],

        events: {
            'click .next': 'save',
            'click .back': 'back',
            'show.bs.modal': 'triggerShown',
            'hide.bs.modal': 'triggerHidden',
            'shown.bs.modal': 'ready',
            'hidden.bs.modal': 'hidden',
            'click .modal-header>.close': 'wizardclose',
            'click .save': 'save',
            'click .finish': 'finish',
            'click .cancel': 'wizardclose',
            'click input': 'selectContents',
            'click .modal-header .oillib-help': 'showHelp',
            'change input': 'update',
            'change select': 'update'
        },

        initialize: function(options) {
            BaseModal.prototype.initialize.call(this, options);

            if (this.module) {
                this.help = new HelpView({path: this.module.id});
            }
        },

        render: function() {
            BaseModal.prototype.render.call(this);

            if(this.model) {
                this.sync();
                this.renderAttributes();
                this.model.on('change', this.renderAttributes, this);
            }
        },

        stickyFooter: function() {
            var modal_offset = this.$el.offset();
            var footer_offset = this.$('.modal-footer:first').offset();

            modal_offset.top += $(window).height();
            footer_offset.top -= modal_offset.top;
            footer_offset.top += this.$('.modal-footer:first').outerHeight();

            var modal_height = this.$('.modal-dialog').height();
            var top = this.$el.scrollTop();
            var bottom;

            if (footer_offset.top > 0 &&
                    this.$('.sticky-modal-footer').length === 0) {
                var modalClone = this.$('.modal-footer').clone();

                this.$('.modal-content').append(modalClone);
                this.$('.modal-footer:last').addClass('sticky-modal-footer');
                this.$('.modal-footer:last button').addClass('btn-sm btn');

                bottom = (modal_height - top - $(window).height());

                this.$('.sticky-modal-footer').css('bottom', bottom + 29 + 'px');
            }
            else if (footer_offset.top < 0 &&
                     this.$('.sticky-modal-footer').length > 0) {
                this.$('.sticky-modal-footer').remove();
            }
            else {
                bottom = (modal_height - top - $(window).height());
                this.$('.sticky-modal-footer').css('bottom', bottom + 29 + 'px');
            }
        },

        renderHelp: function() {
            if (this.$('.modal-header').length > 0) {
                if (this.$('.modal-header .oillib-help').length === 0) {
                    var button = '<div class="oillib-help" title="Click for help"></div>';
                    this.$('.modal-header h4').append(button);
                    this.$('.modal-header .oillib-help').tooltip();
                }
            }
            else {
                this.on('ready', this.renderHelp, this);
            }
        },

        showHelp: function() {
            if (this.$('.oillib-help.alert').length === 0) {
                this.$('.modal-body').prepend(this.help.$el);
                this.help.delegateEvents();
            }
        },

        ready: function() {
            this.trigger('ready');

            if (!_.isUndefined(this.help)) {
                if (this.help.ready) {
                    this.renderHelp();
                }
                else {
                    this.help.on('ready', this.renderHelp, this);
                }
            }

            if (_.isUndefined(this.scrollEvent)) {
                this.scrollEvent = this.$el.on('scroll', _.bind(this.stickyFooter, this));
            }

            this.stickyFooter();
            $(window).on('resize', _.bind(function() {
                this.stickyFooter();
            }, this));
        },

        windowResize: function() {
            BaseModal.prototype.windowResize.call(this);
            this.stickyFooter();
        },

        hidden: function() {
            $(window).off('resize');
            this.trigger('hidden');
        },

        save: function(callback) {
            if (this.superModel) {
                var opts = {
                    success: _.bind(function() {
                        this.trigger('save', this.superModel);

                        if (_.isFunction(callback)) { callback(); }

                        this.hide();
                    }, this),
                    error: _.bind(function(model, response) {
                        this.error('Saving Failed!', 'Server responded with HTTP code: ' + response.status);
                    }, this)
                };

                if (this.superModel.isNew()) {
                    opts.validate = false;
                }

                if (this.model.isValid()) {
                    this.superModel.save(null, opts);
                }

                if (this.superModel.validationError ||
                        this.model.validationError) {
                    this.error('Error!', this.superModel.validationError);
                    this.error('Error!', this.model.validationError);
                    this.$el.scrollTop(0);
                }
            }
            else if (this.model) {
                this.model.save(null, {
                    success: _.bind(function() {
                        this.trigger('save', this.model);
                        if(_.isFunction(callback)) { callback(); }
                        this.hide();
                    }, this),
                    error: _.bind(function(model, response) {
                        this.error('Saving Failed!',
                                   'Server responded with HTTP code: ' + response.status);
                    }, this)
                });

                if (this.model.validationError) {
                    this.error('Error!', this.model.validationError);
                    this.$el.scrollTop(0);
                }
            } else {
                this.trigger('save', this.$('form'));

                if (_.isFunction(callback)) { callback(); }

                this.hide();
            }
        },

        finish: function() {
            this.trigger('finish');
        },

        back: function() {
            this.hide();
            this.trigger('back');
        },

        renderAttributes: function() {
            if (this.attributes) {
                this.attributes.remove();
            }

            if (this.superModel) {
                this.attributes = new AttributesView({name: this.superModel.get('obj_type'),
                                                      model: this.superModel});
            }
            else {
                this.attributes = new AttributesView({name: this.model.get('obj_type'),
                                                      model: this.model});
            }
            
            this.$('.modal-body').append(this.attributes.$el);
        },

        error: function(strong, message) {
            this.$('.modal-body .alert.validation').remove();
            this.$('.modal-body').prepend(_.template(AlertDangerTemplate,
                                                     {strong: strong,
                                                      message: message}));
        },

        clearError: function() {
            this.$('.modal-body .alert.validation').remove();
        },

        wizardclose: function() {
            if (this.model) {
                this.model.fetch().then(_.bind(function() {
                    this.trigger('wizardclose');
                }, this));
            }
            else {
                this.trigger('wizardclose');
            }
        },

        triggerHidden: function() {
            this.trigger('hidden.bs.modal');
        },

        triggerShown: function() {
            this.trigger('shown.bs.modal');
        },

        close: function() {
            $(window).off('resize');
            this.$el.off('scroll');

            if (this.model) {
                this.model.off('change', this.renderAttributes, this);
            }

            BaseModal.prototype.close.call(this);
        }
    });

    return formModal;
});
