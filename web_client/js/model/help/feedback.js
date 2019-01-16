define([
    'underscore',
    'backbone',
    'sweetalert'
], function(_, Backbone, swal){
    'use strict';
    var helpModel = Backbone.Model.extend({
        urlRoot: '/help',
        defaults: {
            helpful: false,
            response: ''
        }
    });

    return helpModel;
});
