/**
* Copyright 2017, GeoSolutions Sas.
* All rights reserved.
*
* This source code is licensed under the BSD-style license found in the
* LICENSE file in the root directory of this source tree.
*/

const React = require('react');
const {connect} = require('react-redux');

const {loadList, selectFeature, zooToFeature, searchSpecies, setFilterProp, resetFtFilters} = require('../../actions/featuresearch');

const FilterUtils = require('../../utils/FilterUtils');

const dataSelector = (state) => state.featuresearch && state.featuresearch.plant || {};
const dataFilterSelector = (state) => state.featuresearch && state.featuresearch.plant_filters || {};

const FeatureTypePanel = require('../../components/naturalfeatures/FeatureTypePanel');
const FeaturesPanel = connect((state) => {
    const data = dataSelector(state);
    return {
        features: data.features || [],
        page: data.page || 0,
        total: data.total || 0,
        pageSize: state.featuresearch && state.featuresearch.pageSize || 30,
        height: state.map && state.map.present && state.map.present.size && state.map.present.size.height || 600};
}, {
    loadFtType: loadList
})(require('../../components/naturalfeatures/FeaturesPanel'));

const FeatureCard = connect((state) => ({
    enableEdit: state.naturalfeatures && (state.naturalfeatures.mode !== 'ADD' && state.naturalfeatures.mode !== 'EDIT')
}), {
    onEdit: selectFeature,
    onZoom: zooToFeature
})(require('../../components/naturalfeatures/FeatureCard'));

const FilterElement = require('../../components/naturalfeatures/FilterElement');

const resetFilters = resetFtFilters.bind(null, 'plant');
const upDateFeatureType = loadList.bind(null, 'plant', 1);
const FilterPanel = connect((state) => {
    const data = dataFilterSelector(state);
    const operator = state.featuresearch && state.featuresearch.defaultOperator;
    return {
        height: state.map && state.map.present && state.map.present.size && state.map.present.size.height || 600,
        disableBtns: !FilterUtils.isFilterValid({operator, ...data})
    };
}, {
    onReset: resetFilters,
    onUpdate: upDateFeatureType
})(require('../../components/naturalfeatures/FilterPanel'));

const onSearch = searchSpecies.bind(null, 'plant');
const onSpeciesChange = setFilterProp.bind(null, 'plant', 'selectedSpecies');

const SpeciesSelector = connect((state) => {
    const data = dataFilterSelector(state);
    return {
        options: data.species,
        selectedSpecies: data.selectedSpecies
}; }, {
    onSearch,
    onChange: onSpeciesChange
})(require('../../components/naturalfeatures/SpeciesSelector'));

const onReleasedChange = setFilterProp.bind(null, 'plant', 'released');

const ReleasedFilter = connect((state) => {
    const data = dataFilterSelector(state);
    return {
        value: !!data.released
    };
}, {
    onChange: onReleasedChange
})(require('../../components/naturalfeatures/CheckFilter'));

const updateFieldValue = setFilterProp.bind(null, 'plant');

const DateFiled = connect((state) => {
    const data = dataFilterSelector(state);
    return {
        operator: data.operator || state.featuresearch && state.featuresearch.defaultOperator,
        fieldValue: data.includevalue
    };
}, {
    updateFieldValue
})(require('../../components/naturalfeatures/DateFilter'));

class Plant extends React.Component {
    render() {
        return (
            <FeatureTypePanel featureType="plant">
                <FeaturesPanel>
                    <FeatureCard/>
                </FeaturesPanel>
                <FilterPanel>
                    <FilterElement label="by Species">
                        <SpeciesSelector/>
                    </FilterElement>
                    <FilterElement label="by Inclusion date">
                        <DateFiled/>
                    </FilterElement>
                    <FilterElement label="by Properties">
                        <ReleasedFilter label="released"/>
                    </FilterElement>
                </FilterPanel>
            </FeatureTypePanel>
            );
    }
}

module.exports = Plant;
