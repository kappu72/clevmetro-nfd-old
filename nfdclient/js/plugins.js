/**
 * Copyright 2016, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
 */

module.exports = {
    plugins: {
        MapPlugin: require('../MapStore2/web/client/plugins/Map'),
        DrawerMenuPlugin: require('../MapStore2/web/client/plugins/DrawerMenu'),
        TutorialPlugin: require('../MapStore2/web/client/plugins/Tutorial'),
        TOCPlugin: require('../MapStore2/web/client/plugins/TOC'),
        OmniBarPlugin: require('../MapStore2/web/client/plugins/OmniBar'),
        SearchPlugin: require('../MapStore2/web/client/plugins/Search'),
        BurgerMenuPlugin: require('../MapStore2/web/client/plugins/BurgerMenu'),
        NfdLoginPlugin: require('./plugins/NfdLogin'),
        ToolbarPlugin: require('../MapStore2/web/client/plugins/Toolbar'),
        ExpanderPlugin: require('../MapStore2/web/client/plugins/Expander'),
        LocatePlugin: require('../MapStore2/web/client/plugins/Locate'),
        ZoomAllPlugin: require('../MapStore2/web/client/plugins/ZoomAll'),
        ZoomInPlugin: require('../MapStore2/web/client/plugins/ZoomIn'),
        ZoomOutPlugin: require('../MapStore2/web/client/plugins/ZoomOut'),
        NotificationsPlugin: require('../MapStore2/web/client/plugins/Notifications'),
        ViewEditNaturalFeaturesPlugin: require('./plugins/ViewEditNaturalFeatures'),
        AddNaturalFeaturesPlugin: require('./plugins/AddNaturalFeatures'),
        ToggleAddEditPanelPlugin: require('./plugins/ToggleAddEditPanel'),
        FeaturesPlugin: require('./plugins/FeaturesPlugin')
    },
    requires: {}
};
