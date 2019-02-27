// set up the app
require([
    'app'
], function(App){
    'use strict';
    window.weboildb = App;
    weboildb.initialize();
});