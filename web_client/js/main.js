
// Configure RequireJS
require.config({
    baseUrl: '/js',
    priority: ['underscore', 'jqueryui', 'backbone', 'bootstrap'],
    paths: {
        jquery: 'lib/jquery/dist/jquery',
        jqueryui: 'lib/jquery-ui/ui',
        chosen: 'lib/chosen/chosen.jquery',
        jqueryDatetimepicker: 'lib/datetimepicker/jquery.datetimepicker',
        'jquery-mousewheel': 'lib/jquery-mousewheel/jquery.mousewheel',
        underscore: 'lib/underscore/underscore',
        backbone: 'lib/backbone/backbone',
        bootstrap: 'lib/bootstrap/dist/js/bootstrap',
        moment: 'lib/moment/moment',
        'moment-round': 'lib/moment-round/dist/moment-round',
        mousetrap: 'lib/mousetrap/mousetrap',
        text: 'lib/requirejs-text/text',
        json: 'lib/requirejs-plugins/src/json',
        fuse: 'lib/fuse/src/fuse',
        html2canvas: 'lib/html2canvas/build/html2canvas',
        JUMFlotLib: 'lib/JUMFlot/jquery.flot.JUMlib',
        masonry: 'lib/masonry/masonry',
        eventEmitter: 'lib/eventEmitter/',
        outlayer: 'lib/outlayer/',
        sweetalert: 'lib/sweetalert2/dist/sweetalert2.min',
        toastr: 'lib/toastr/toastr',
        nucos: 'lib/nucos/nucos',
        relativeimportance: 'lib/relativeimportance/relativeImportance',
        dropzone: 'lib/dropzone/dist/dropzone-amd-module',
        socketio: 'lib/socket.io-client/dist/socket.io',
        localforage: 'lib/localforage/dist/localforage',
        eventie: 'lib/eventie/',
        'fizzy-ui-utils': 'lib/fizzy-ui-utils/',
        'doc-ready': 'lib/doc-ready/',
        'get-style-property': 'lib/get-style-property/',
        'get-size': 'lib/get-size/',
        'matches-selector': 'lib/matches-selector/',
        'php-date-formatter': 'lib/php-date-formatter/js/php-date-formatter',
        raphael: 'lib/raphael/raphael',
        whammy: 'lib/whammy/whammy',
        flot: 'lib/flot/jquery.flot',
        flotsymbol: 'lib/flot/jquery.flot.symbol',
        flottime: 'lib/flot/jquery.flot.time',
        flotresize: 'lib/flot/jquery.flot.resize',
        flotdirection: 'lib/flotdirection/jquery.flot.direction',
        flotspline: 'lib/flotspline/jquery.flot.spline',
        flotstack: 'lib/flot/jquery.flot.stack',
        flotpie: 'lib/flot/jquery.flot.pie',
        flotfillarea: 'lib/flotfillarea/jquery.flot.fillarea',
        flotselect: 'lib/flot/jquery.flot.selection',
        flotgantt: 'lib/JUMFlot/jquery.flot.gantt',
        flotneedle: 'lib/flotneedle/flotNeedle',
        flotextents: 'lib/flotextents/src/jquery.flot.extents',
        flotnavigate: 'lib/flot/jquery.flot.navigate',
    },
    shim: {
        jquery: {
            exports: '$'
        },
        chosen: {
            deps: ['jquery'],
            exports: '$'
        },
        jqueryui: {
            deps: ['jquery'],
            exports: '$.ui'
        },
        'jquery-mousewheel': ['jquery'],
        jqueryDatetimepicker: ['jquery', 'jquery-mousewheel', 'php-date-formatter'],
        'php-date-formatter': {
            exports: 'DateFormatter'
        },
        'moment-round': ['moment'],
        bootstrap: ['jquery'],
        toastr:{
            deps: ['jquery'],
            exports: 'toastr'
        },
        sweetalert: {
            exports: 'swal'
        },
        socketio: {
            exports: 'io'
        },
        localforage: {
            exports: 'localforage'
        },
        html2canvas: {
            exports: 'html2canvas'
        },
        flot: ['jquery'],
        flotsymbol: ['flot'],
        flottime: ['flot'],
        flotresize: ['flot'],
        flotdirection: ['flot'],
        flotspline: ['flot'],
        flotneedle: ['flot'],
        flotstack: ['flot'],
        flotpie: ['flot'],
        flotfillarea: ['flot'],
        flotselect: ['flot'],
        flotextents: ['flot'],
        flotnavigate: ['flot'],
        flotgantt: ['JUMFlotLib'],
        JUMFlotLib: ['flot']
    }
});

