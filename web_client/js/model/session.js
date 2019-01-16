define(['underscore',
        'backbone',
        'sweetalert'],
function(_, Backbone, swal) {
    'use strict';
    var sessionModel = Backbone.Model.extend({
        url: function() {
            return weboillib.config.oil_api + '/session';
        },
        defaults: {
            'id': null,
        },

        initialize: function(callback) {
            this.save(null, {
                success: function(model){
                    localStorage.setItem('session', model.id);
                    callback();
                },
                error: this.error
            });

        },

        error: function() {
            swal({
                title: 'Connection Error',
                text: 'Error establishing a session with the API server.',
                type: 'error',
                confirmButtonText: 'Retry'
            }).then(function(){
                window.location.reload();
            });
        }
    });

    return sessionModel;
});