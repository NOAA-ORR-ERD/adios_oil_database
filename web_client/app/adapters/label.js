import ApplicationAdapter from './application';

export default class LabelAdapter extends ApplicationAdapter {
    //host = 'https://adios-stage.orr.noaa.gov/api'
    //host = 'http://localhost:9898'
    headers = {
        'X-Requested-With': 'XMLHttpRequest'
    };

    ajax(url, method, options) {
        if (options === undefined) { options = {}; }

        options.crossDomain = true;
        options.xhrFields = { withCredentials: true };

        return super.ajax(url, method, options);
    }

    buildURL(type, id, record) {
        //call the default buildURL and then append a slash
        return super.buildURL(type, id, record) + '/';
    }
}
