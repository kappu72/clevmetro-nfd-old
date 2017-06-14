/**
 * Copyright 2016, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */
const React = require('react');
const ReactDOM = require('react-dom');
const {connect} = require('react-redux');
const appReducers = {
    naturalfeatures: require('./reducers/naturalfeatures'),
    selection: require('../MapStore2/web/client/reducers/selection')
};
const {initState, getAnimals, getMushrooms} = require('./actions/naturalfeatures');
const dEpics = require('./epics/naturalfeatures');
const ConfigUtils = require('../MapStore2/web/client/utils/ConfigUtils');
// ConfigUtils.setLocalConfigurationFile('/static/js/risksConfig.json');
// Set one hour cache
ConfigUtils.setConfigProp("cacheDataExpire", 3600);

const StandardApp = require('../MapStore2/web/client/components/app/StandardApp');
const url = require('url');
const urlQuery = url.parse(window.location.href, true).query;
const init = urlQuery && urlQuery.init && JSON.parse(decodeURIComponent(urlQuery.init));

const {pages, pluginsDef, initialState, storeOpts} = require('./appConfig');
const axios = require('../MapStore2/web/client/libs/ajax');
const Cookies = require('cookies-js');
// test cookies local setting
// Cookies.set('csrftoken', 'zR1gzO836hVjqoKIzSZuxtPCyTP3Jtho', { expires: Infinity });
if (Cookies.get('csrftoken')) {
    axios.defaults.headers.common['X-CSRFToken'] = Cookies.get('csrftoken');
}
const themeCfg = {
    path: '/static/js'
};
const StandardRouter = connect((state) => ({
    locale: state.locale || {},
    themeCfg,
    pages
}))(require('../MapStore2/web/client/components/app/StandardRouter'));

const appStore = require('../MapStore2/web/client/stores/StandardStore').bind(null, initialState, appReducers, {...dEpics});
// const geomPath = window.DISASTERRISK && window.DISASTERRISK.app && window.DISASTERRISK.app.geometry || '/risks/data_extraction/geom/AF/';
const restApiURL = 'http://192.168.1.38/gs-local/ws_jrodrigo/ows';
// const geomPath = 'http://disasterrisk.af.geonode.org/risks/data_extraction/geom/AF/';
const initialActions = init ? [
    () => initState(init)
] : [
    () => getAnimals(restApiURL, 'refinerias'),
    () => getMushrooms(restApiURL, 'pp_gas')
];
const appConfig = {
    storeOpts,
    appStore,
    pluginsDef,
    initialActions,
    appComponent: StandardRouter
};

ReactDOM.render(
    <StandardApp {...appConfig}/>,
    document.getElementById('container')
);