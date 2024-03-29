from django.db.models.fields import BooleanField, TextField, CharField, DateTimeField,\
    DateField, NullBooleanField
from django.db.models.fields import IntegerField, DecimalField, FloatField
from django.contrib.gis.db.models.fields import GeometryField, PolygonField

from nfdcore.models import get_details_class, EarthwormEvidence, DisturbanceType,\
    SlimeMoldLifestages, TaxonLocation, NaturalAreaLocation, ElementNaturalAreas

from nfdcore.models import DictionaryTable
from nfdcore.models import Voucher, OccurrenceTaxon, PlantDetails,\
    StreamAnimalDetails, LandAnimalDetails, ElementSpecies, Species,\
    PondLakeAnimalDetails, WetlandAnimalDetails, SlimeMoldDetails,\
    OccurrenceNaturalArea, OccurrenceCategory, DictionaryTableExtended,\
    Photograph, get_occurrence_model, TaxonDetails, ConiferDetails, FernDetails,\
    FloweringPlantDetails, MossDetails, ConiferLifestages,\
    WetlandVetegationStructure, StreamSubstrate
from nfdcore.models import AnimalLifestages, OccurrenceObservation, PointOfContact
from rest_framework.serializers import Serializer, ModelSerializer
from django.db import models as db_models
from rest_framework import fields as rest_fields
from rest_framework import relations as rest_rels
from rest_framework import serializers
from collections import Mapping, OrderedDict
from rest_framework.serializers import Field
import reversion
from reversion.models import Version
from rest_framework.fields import empty, SerializerMethodField, ImageField
from rest_framework_gis import serializers as gisserializer
from django.db.models.fields import NOT_PROVIDED
from rest_framework.exceptions import ValidationError
from PIL import Image
from nfdapi import settings
import os
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models.query import QuerySet
from django.template.context_processors import request
from django.contrib.gis.geos import Point, Polygon

def _(message): return message

""" -------------------------------------------
UTILITY METHODS AND CLASSES
---------------------------------------------- """

def get_form_dict(forms):
    form_dict = {}
    for form in forms:
        form_dict[form[0]] = form
    return form_dict

MANAGEMENT_FORM_NAME = _('occurrencemanagement')
MANAGEMENT_FORM_ITEMS = [{
        "key": "id",
        "label": _("id"),
        "type": "integer",
        'readonly': True
    },{
        "key": "featuretype",
        "label": _("featuretype"),
        "type": "string",
        'readonly': True
    },{
        "key": "featuresubtype",
        "label": _("featuresubtype"),
        "type": "string",
        'readonly': True
    },{
        "key": "released",
        "label": _("released"),
        "type": "boolean",
        'readonly': True
    },{
        "key": "verified",
        "label": _("verified"),
        "type": "boolean",
        'readonly': False
    },{
        "key": "inclusion_date",
        "label": _("inclusion_date"),
        "type": "string",
        'readonly': True
    },{
        "key": "version_date",
        "label": _("version_date"),
        "type": "string",
        'readonly': True
    }]

MANAGEMENT_FORM_ITEMS_PUBLISHER = [{
        "key": "id",
        "label": _("id"),
        "type": "integer",
        'readonly': True
    },{
        "key": "featuretype",
        "label": _("featuretype"),
        "type": "string",
        'readonly': True
    },{
        "key": "featuresubtype",
        "label": _("featuresubtype"),
        "type": "string",
        'readonly': True
    },{
        "key": "released",
        "label": _("released"),
        "type": "boolean",
        'readonly': False
    },{
        "key": "verified",
        "label": _("verified"),
        "type": "boolean",
        'readonly': False
    },{
        "key": "inclusion_date",
        "label": _("inclusion_date"),
        "type": "string",
        'readonly': True
    },{
        "key": "version_date",
        "label": _("version_date"),
        "type": "string",
        'readonly': True
    }]
    

LAND_ANIMAL_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), LandAnimalDetails, ['details.lifestages']),
    (_('details.lifestages'), AnimalLifestages, []),
    (_('location'), TaxonLocation, []),
    ]
LAND_ANIMAL_TYPE_DICT = get_form_dict(LAND_ANIMAL_TYPE)

STREAM_ANIMAL_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), StreamAnimalDetails, ['details.lifestages', 'details.substrate']),
    (_('details.lifestages'), AnimalLifestages, []),
    (_('details.substrate'), StreamSubstrate, []),
    (_('location'), TaxonLocation, []),
    ]

STREAM_ANIMAL_TYPE_DICT = get_form_dict(STREAM_ANIMAL_TYPE)

PONDLAKE_ANIMAL_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), PondLakeAnimalDetails, ['details.lifestages']),
    (_('details.lifestages'), AnimalLifestages, []),
    (_('location'), TaxonLocation, []),
    ]
PONDLAKE_ANIMAL_TYPE_DICT = get_form_dict(PONDLAKE_ANIMAL_TYPE)


WETLAND_ANIMAL_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), WetlandAnimalDetails, ['details.lifestages', 'details.vegetation']),
    (_('details.lifestages'), AnimalLifestages, []),
    (_('details.vegetation'), WetlandVetegationStructure, []),
    (_('location'), TaxonLocation, []),
    ]
WETLAND_ANIMAL_TYPE_DICT = get_form_dict(WETLAND_ANIMAL_TYPE)

SLIMEMOLD_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), SlimeMoldDetails, ['details.lifestages']),
    (_('details.lifestages'), SlimeMoldLifestages, []),
    (_('location'), TaxonLocation, []),
    ]
SLIMEMOLD_TYPE_DICT = get_form_dict(SLIMEMOLD_TYPE)

CONIFER_PLANT_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), ConiferDetails, ['details.lifestages', 'details.earthworm_evidence', 'details.disturbance_type']),
    (_('details.lifestages'), ConiferLifestages, []),
    (_('details.earthworm_evidence'), EarthwormEvidence, []),
    (_('details.disturbance_type'), DisturbanceType, []),
    (_('location'), TaxonLocation, []),
    ]
CONIFER_PLANT_TYPE_DICT = get_form_dict(CONIFER_PLANT_TYPE)

FERN_PLANT_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), FernDetails, ['details.earthworm_evidence', 'details.disturbance_type']),
    (_('details.earthworm_evidence'), EarthwormEvidence, []),
    (_('details.disturbance_type'), DisturbanceType, []),
    (_('location'), TaxonLocation, []),
    ]
FERN_PLANT_TYPE_DICT = get_form_dict(FERN_PLANT_TYPE)

FLOWERING_PLANT_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), FloweringPlantDetails, ['details.earthworm_evidence', 'details.disturbance_type']),
    (_('details.earthworm_evidence'), EarthwormEvidence, []),
    (_('details.disturbance_type'), DisturbanceType, []),
    (_('location'), TaxonLocation, []),
    ]
FLOWERING_PLANT_TYPE_DICT = get_form_dict(FLOWERING_PLANT_TYPE)

MOSS_PLANT_TYPE = [
    (_('species'), Species, ['species.element_species']),
    (_('species.element_species'), ElementSpecies, []),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('voucher'), Voucher, []),
    (_('details'), MossDetails, ['details.earthworm_evidence', 'details.disturbance_type']),
    (_('details.earthworm_evidence'), EarthwormEvidence, []),
    (_('details.disturbance_type'), DisturbanceType, []),
    (_('location'), TaxonLocation, []),
    ]
MOSS_PLANT_TYPE_DICT = get_form_dict(MOSS_PLANT_TYPE)

NATURAL_AREA_TYPE = [
    (_('element'), ElementNaturalAreas, ['element.earthworm_evidence', 'element.disturbance_type']),
    (MANAGEMENT_FORM_NAME, OccurrenceTaxon, []),
    (_('observation'), OccurrenceObservation, ['observation.reporter', 'observation.verifier', 'observation.recorder']),
    (_('observation.reporter'), PointOfContact, []),
    (_('observation.verifier'), PointOfContact, []),
    (_('observation.recorder'), PointOfContact, []),
    (_('element.earthworm_evidence'), EarthwormEvidence, []),
    (_('element.disturbance_type'), DisturbanceType, []),
    (_('location'), NaturalAreaLocation, []),
    ]
NATURAL_AREA_TYPE_DICT = get_form_dict(NATURAL_AREA_TYPE)


del _
from django.utils.translation import ugettext_lazy as _


def get_details_serializer(category_code):
    if category_code=='co':
        return ConiferDetailsSerializer
    elif category_code=='fe':
        return FernDetailsSerializer
    elif category_code=='fl':
        return FloweringPlantDetailsSerializer
    elif category_code=='pl':
        return Serializer # FIXME
    elif category_code=='mo':
        return MossDetailsSerializer
    elif category_code=='fu':
        return Serializer # FIXME
    elif category_code=='sl':
        return SlimeMoldDetailsSerializer
    elif category_code=='ln':
        return LandAnimalDetailsSerializer
    elif category_code=='lk':
        return PondLakeAnimalDetailsSerializer
    elif category_code=='st':
        return StreamAnimalDetailsSerializer
    elif category_code=='we':
        return WetlandAnimalDetailsSerializer
    elif category_code=='na':
        return NaturalAreaElementSerializer

def is_deletable_field(f):
    if not getattr(f, 'related_model', False):
        return False
    if getattr(f, 'auto_created', False):
        return False
    if issubclass(f.related_model, DictionaryTable):
        return False
    if issubclass(f.related_model, DictionaryTableExtended):
        return False
    if issubclass(f.related_model, Species):
        return False
    return True
    

def delete_object_and_children(parent_instance):
    
    children = []

    if not getattr(parent_instance, '_meta', None):
        print parent_instance
        print type(parent_instance)
        print repr(parent_instance)
    if not isinstance(parent_instance, QuerySet):
        for f in parent_instance._meta.get_fields():
            if is_deletable_field(f):
                child_instance = getattr(parent_instance, f.name, None)
                if isinstance(f, GenericRelation):
                    # for generic related objects such as photographs, we get the related QuerySet
                    child_instance = child_instance.all()
                if child_instance:
                    children.append(child_instance)
    
    # some children are mandatory for the parent, so we first delete parents
    parent_instance.delete()
    for child_instance in children:
        delete_object_and_children(child_instance)

class DictionaryField(rest_fields.CharField):
    def get_attribute(self, instance):
        entry_instance = super(DictionaryField, self).get_attribute(instance)
        #entry_instance = get_attribute(instance, self.source_attrs)
        #field_name = self.source_attrs[-1]
        #entry_instance = getattr(instance, field_name, None)
        if entry_instance:
            return getattr(entry_instance, 'code', None)

    def to_internal_value(self, data):
        return rest_fields.CharField.to_internal_value(self, data)
    
    def to_representation(self, value):
        return rest_fields.CharField.to_representation(self, value)

class DictionaryExtendedField(rest_fields.CharField):
    def get_attribute(self, instance):
        entry_instance = super(DictionaryExtendedField, self).get_attribute(instance)
        #entry_instance = get_attribute(instance, self.source_attrs)
        #field_name = self.source_attrs[-1]
        #entry_instance = getattr(instance, field_name, None)
        if entry_instance:
            return getattr(entry_instance, 'code', None)

    def to_internal_value(self, data):
        return rest_fields.CharField.to_internal_value(self, data)
    
    def to_representation(self, value):
        return rest_fields.CharField.to_representation(self, value)

class TotalVersionsField(rest_fields.IntegerField):
    def get_attribute(self, instance):
        versions = Version.objects.get_for_object(instance).count()
        if versions<1:
            versions = 1
        return versions

def get_serializer_fields(form_name, model):
    fields = model._meta.get_fields()
    result = OrderedDict()
    for f in fields:
        fdef = None
        
        kwargs = {}
        if getattr(f, 'default', NOT_PROVIDED) != NOT_PROVIDED:
            kwargs['default'] = getattr(f, 'default')
        
        if getattr(f, 'primary_key', False):
            pass
        elif isinstance(f, CharField) or isinstance(f, TextField):
            kwargs['max_length'] = getattr(f, 'max_length', None)
            kwargs['allow_blank'] = getattr(f, 'blank', False)
            kwargs['allow_null'] = getattr(f, 'null', False)
            kwargs['required'] = not getattr(f, 'null', False)
            fdef = rest_fields.CharField(**kwargs)
        elif isinstance(f, BooleanField):
            fdef = rest_fields.BooleanField(**kwargs)
        elif isinstance(f, NullBooleanField):
            kwargs['required'] = not getattr(f, 'null', False)
            fdef = rest_fields.NullBooleanField(**kwargs)
        elif isinstance(f, DateTimeField):
            kwargs['allow_null'] = getattr(f, 'null', False)
            kwargs['required'] = not getattr(f, 'null', False)
            fdef = rest_fields.DateTimeField(**kwargs)
        elif isinstance(f, DateField):
            kwargs['allow_null'] = getattr(f, 'null', False)
            kwargs['required'] = not getattr(f, 'null', False)
            fdef = rest_fields.DateField(**kwargs)
        elif isinstance(f, DecimalField):
            kwargs['allow_null'] = getattr(f, 'null', False)
            kwargs['required'] = not getattr(f, 'null', False)
            kwargs['max_digits'] = getattr(f, 'max_digits', None)
            kwargs['decimal_places'] = getattr(f, 'decimal_places', None)
            fdef = rest_fields.DecimalField(**kwargs)
        elif isinstance(f, FloatField):
            kwargs['allow_null'] = getattr(f, 'null', False)
            kwargs['required'] = not getattr(f, 'null', False)
            fdef = rest_fields.FloatField(**kwargs)
        elif isinstance(f, IntegerField):
            kwargs['allow_null'] = getattr(f, 'null', False)
            kwargs['required'] = not getattr(f, 'null', False)
            fdef = rest_fields.IntegerField(**kwargs)
        elif getattr(f, 'related_model', False):
            kwargs['allow_blank'] = getattr(f, 'blank', False)
            kwargs['allow_null'] = getattr(f, 'null', False)
            kwargs['required'] = not getattr(f, 'null', False)
            if issubclass(f.related_model, DictionaryTable):
                fdef = DictionaryField(**kwargs)
            elif issubclass(f.related_model, DictionaryTableExtended):
                fdef = DictionaryExtendedField(**kwargs)
        elif isinstance(f, GeometryField):
            # skip geoms
            pass
            
        if fdef:
            if form_name:
                result[form_name + "." + f.name] = fdef
            else:
                result[f.name] = fdef
    return result


class OccurrenceRelatedObjectSerialzer(Serializer):
    def __init__(self, instance=None, data=empty, model=None, **kwargs):
        self._model = model
        Serializer.__init__(self, instance=instance, data=data, **kwargs)


def check_all_null(field_dict):
    if field_dict is None or field_dict is empty:
        return True
    for value in field_dict.values():
        if isinstance(value, dict):
            if not check_all_null(value):
                return False
        elif not (value is None or value == ''):
            return False
    return True

def to_flat_representation(values_dict, parent_path=None):
    result = OrderedDict()
    for fname, fvalue in values_dict.items():
        if parent_path:
            global_fname = parent_path + "." + fname
        else:
            global_fname = fname

        if fname != 'geom' and isinstance(fvalue, dict):
            child_dict = to_flat_representation(fvalue, global_fname)
            result.update(child_dict)
        else:
            result[global_fname] = fvalue
    return result

class CustomModelSerializerMixin(object):
    """
    Used by most of our model serializers to properly manage dictionaries and to ignore
    empty forms when they are not required
    """
    def build_field(self, field_name, info, model_class, nested_depth):
        """
        Return a two tuple of (cls, kwargs) to build a serializer field with.
        """
        if field_name in info.relations:
            relation_info = info.relations[field_name]
            if issubclass(relation_info.related_model, DictionaryTable):
                f = DictionaryField
                kwargs = {}
                if relation_info.model_field.blank:
                    kwargs["allow_blank"] = True
                    kwargs["required"] = False
                if relation_info.model_field.null:
                    kwargs["required"] = False
                    kwargs["allow_null"] = True
                
                return f, kwargs
            elif issubclass(relation_info.related_model, DictionaryTableExtended):
                f = DictionaryExtendedField
                kwargs = {}
                if relation_info.model_field.blank:
                    kwargs["allow_blank"] = True
                    kwargs["required"] = False
                if relation_info.model_field.null:
                    kwargs["required"] = False
                    kwargs["allow_null"] = True
                return f, kwargs
        return super(CustomModelSerializerMixin, self).build_field(field_name, info, model_class, nested_depth)

    def run_validation(self, data=empty):
        """
        We override the default `run_validation`, because the validation
        performed by validators and the `.validate()` method should
        be coerced into an error dictionary with a 'non_fields_error' key.
        """
        if not self.required and check_all_null(data):
            raise rest_fields.SkipField("Non required empty form")
        return super(CustomModelSerializerMixin, self).run_validation(data)

def init_forms(instance, category_code):
        if category_code=='co':
            instance.forms = CONIFER_PLANT_TYPE
            instance._form_dict = CONIFER_PLANT_TYPE_DICT
        elif category_code=='fe':
            instance.forms = FERN_PLANT_TYPE
            instance._form_dict = FERN_PLANT_TYPE_DICT
        elif category_code=='fl':
            instance.forms = FLOWERING_PLANT_TYPE
            instance._form_dict = FLOWERING_PLANT_TYPE_DICT
        elif category_code=='pl':
            return None #FIXME
        elif category_code=='mo':
            instance.forms = MOSS_PLANT_TYPE
            instance._form_dict = MOSS_PLANT_TYPE_DICT
        elif category_code=='fu':
            return None #FIXME
        elif category_code=='sl':
            instance.forms = SLIMEMOLD_TYPE
            instance._form_dict = SLIMEMOLD_TYPE_DICT
        elif category_code=='ln':
            instance.forms = LAND_ANIMAL_TYPE
            instance._form_dict = LAND_ANIMAL_TYPE_DICT
        elif category_code=='lk':
            instance.forms = PONDLAKE_ANIMAL_TYPE
            instance._form_dict = PONDLAKE_ANIMAL_TYPE_DICT
        elif category_code=='st':
            instance.forms = STREAM_ANIMAL_TYPE
            instance._form_dict = STREAM_ANIMAL_TYPE_DICT
        elif category_code=='we':
            instance.forms = WETLAND_ANIMAL_TYPE
            instance._form_dict = WETLAND_ANIMAL_TYPE_DICT
        elif category_code=='na':
            instance.forms = NATURAL_AREA_TYPE
            instance._form_dict = NATURAL_AREA_TYPE_DICT

class UpdateOccurrenceMixin(object):
    def __init__(self, instance=None, data=empty, is_writer=False, is_publisher=False, **kwargs):
        self.is_writer = is_writer
        self.is_publisher = is_publisher
        if instance and instance.occurrence_cat:
            init_forms(self, instance.occurrence_cat.code)
        super(UpdateOccurrenceMixin, self).__init__(instance, data, **kwargs)
        
    def _get_local_name(self, global_field_name):
        """
        Gets the local name of the provided attrib
        Example _get_local_name("species.element_species.native") returns "native"
        """
        parts = global_field_name.split(".")
        if len(parts)>0:
            return parts[-1]
        
    def _get_form_fields(self, form_name, instance):
        """
        Gets the field names of the given instance, using global name notation (e.g. "observation.reporter.name" )
        """
        result = []
        if (instance):
            return instance._meta.get_fields()                      
        return result
    
    def _get_validated_data_form(self, validated_data, form_name):
        """
        validated_data:
        form_name: dictionary key including subdicts (e.g. "species.element_species")
        Returns the data located on validated_data['species']['element_species'] or None if does not exist
        """
        if validated_data:
            if form_name == MANAGEMENT_FORM_NAME:
                return validated_data
            else:            
                parts = form_name.split(".")
                subdict = validated_data
                for part in parts:
                    subdict = subdict.get(part)
                    if subdict is None:
                        return None
            return subdict
        
    def set_form_values(self, form_name, instance, form_validated_data, force_save=False):
        """
        Updates the values of the provided instance using validated data 
        """
        if instance:
            if form_validated_data:
                fields = self._get_form_fields(form_name, instance)
                modified = False
                for f in fields:
                    if getattr(f, 'primary_key', False):
                        pass
                    elif getattr(f, 'related_model', False):
                        if issubclass(f.related_model, DictionaryTable) or issubclass(f.related_model, DictionaryTableExtended):
                            new_value = form_validated_data.get(f.name)
                            old_value =  getattr(instance, f.name, None)
                            if old_value != new_value and (old_value is None or new_value != old_value.code):
                                try:
                                    if new_value != None:
                                        dict_entry = f.related_model.objects.get(code=new_value)
                                    else:
                                        dict_entry = None
                                    modified = True
                                    setattr(instance, f.name, dict_entry)
                                except Exception as exc:
                                    setattr(instance, f.name, None)
                    else:
                        if isinstance(f, CharField) or isinstance(f, TextField):
                            new_value = form_validated_data.get(f.name, '')
                            if new_value is None:
                                new_value = ''
                            old_value =  getattr(instance, f.name, '')
                            if old_value is None:
                                old_value = ''
                        elif isinstance(f, DateTimeField) or isinstance(f, DateField):
                            new_value = form_validated_data.get(f.name, '')
                            old_value =  getattr(instance, f.name, None)
                        elif isinstance(f, BooleanField) or isinstance(f, NullBooleanField) or \
                                isinstance(f, FloatField) or isinstance(f, DecimalField) or isinstance(f, IntegerField):
                            new_value = form_validated_data.get(f.name)
                            old_value =  getattr(instance, f.name, None)
                        elif isinstance(f, PolygonField):
                            new_value = form_validated_data.get(f.name)
                            old_value =  getattr(instance, f.name, None)
                        #if new_value != None and new_value != old_value:
                        if new_value != old_value:
                            modified = True
                            setattr(instance, f.name, new_value)

                if force_save or modified:
                    instance.save()
                    return True
            else:
                # if the form is empty and instance exists, delete instance
                try: 
                    instance.delete()
                except:
                    pass
                return True
        return False
    
    def _get_form_model_instance(self, form_name, model_class, parent_instance):
        """
        Gets the related instance for the provided form name and parent instance.
        """
        if parent_instance is not None:
            if form_name == 'details':
                related_instance = parent_instance.get_details()
            else:
                related_instance = getattr(parent_instance, self._get_local_name(form_name), None)
            return related_instance
    
    def _update_form(self, form_name, model_class, validated_data, parent_instance, child_forms=[]):
        """
        Updates the appropriate instance according to the provided form_name and model instance. All
        related objects are also updated if modified.
        
        Returns True if the instance has been modified and saved, False if there were no changes. 
        """
        form_validated_data = self._get_validated_data_form(validated_data, form_name)
        
        related_instance = self._get_form_model_instance(form_name, model_class, parent_instance)
        if form_validated_data and not related_instance:
            related_instance = model_class()
            
        any_saved = False
        for (child_form_name, child_model_class, child_child_forms) in child_forms:
            saved = self._update_form(child_form_name, child_model_class, validated_data, related_instance, child_child_forms)
            any_saved = any_saved or saved
        
        saved = self.set_form_values(form_name, related_instance, form_validated_data, any_saved)
        any_saved = any_saved or saved
        
        if any_saved:
            if form_validated_data is None:
                setattr(parent_instance, self._get_local_name(form_name), None)
            else:
                setattr(parent_instance, self._get_local_name(form_name), related_instance)
        return any_saved
    
    def _get_form_dict(self):
        """
        Gets the definition of forms for the current instance type
        """
        if not self._form_dict:
            self._form_dict = get_form_dict(self.get_forms())
        return self._form_dict
        
    def _get_form_def_tree(self, form_name, model_class, children):
        """
        Gets the definition of a form and its related objects (children)
        """
        complete_children_def = []
        for child in children:
            (child_form_name, child_model_class, child_children) = self._get_form_dict()[child]
            child_def = self._get_form_def_tree(child_form_name, child_model_class, child_children)
            complete_children_def.append(child_def)
        return (form_name, model_class, complete_children_def)
    
    def get_toplevel_forms(self):
        """
        Gets the definition of the forms which are directly related to Occurrence objects. Each
        form contains also the definition of its related objects (as children)
        """
        forms = []
        for (form_name, model_class, children) in self.get_forms():
            if "." not in form_name:
                # only for top-level objects
                form_def = self._get_form_def_tree(form_name, model_class, children)
                forms.append(form_def)
        return forms
    
    def get_forms(self):
        """
        Gets the definition of all forms
        """
        return self.forms
    
    def update(self, instance, validated_data):
        with reversion.create_revision():
            for (form_name, model_class, children) in self.get_toplevel_forms():
                if form_name == 'species':
                    try:
                        species_id = validated_data['species']['id']
                        selected_species = Species.objects.get(pk=species_id)
                        instance.species = selected_species
                        self._update_form('species', Species, validated_data, instance)
                        self._update_form('species.element_species', ElementSpecies, validated_data, selected_species)
                    except:
                        raise ValidationError({"species": [_("No species was selected")]})
                elif form_name != MANAGEMENT_FORM_NAME:
                    self._update_form(form_name, model_class, validated_data, instance, children)
            
            if isinstance(instance, OccurrenceTaxon):
                # taxon
                pass
            else:
                # natural area
                pass

            instance.geom = validated_data.get("geom") or instance.geom
            instance.version = instance.version + 1
            instance.verified = validated_data.get("verified", False) or False
            if self.is_publisher:
                instance.released = validated_data.get("released", False) or False
                if instance.released:
                    instance.released_versions = instance.released_versions + 1
            else:
                instance.released = False
            instance.save()
        return instance
    
    def create(self, validated_data):
        code = validated_data.get('featuresubtype')
        if code == 'na':
            instance = OccurrenceNaturalArea()
        else:
            instance = OccurrenceTaxon()
        instance.occurrence_cat = OccurrenceCategory.objects.get(code=code)
        instance.geom = validated_data.get('geom')
        init_forms(self, instance.occurrence_cat.code)
        return self.update(instance, validated_data)


""" -------------------------------------------
MODEL SERIALIZERs
---------------------------------------------- """
class VoucherSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = Voucher
        exclude = ('id',)

class ElementSpeciesSerializer(CustomModelSerializerMixin,ModelSerializer):
    class Meta:
        model = ElementSpecies
        exclude = ('id',)
        
class SpeciesSerializer(CustomModelSerializerMixin,ModelSerializer):
    element_species = ElementSpeciesSerializer(required=False)
    
    def to_internal_value(self, data):
        result = super(SpeciesSerializer, self).to_internal_value(data)
        if data.get("id"):
            # We need the id of the new species to set it in the occurrence 
            result['id'] = data.get('id')
        return result
    
    class Meta:
        model = Species
        fields = "__all__"

class PointOfContactSerializer(CustomModelSerializerMixin, ModelSerializer):
        
    class Meta:
        model = PointOfContact
        exclude = ('id',)

class OccurrenceObservationSerializer(CustomModelSerializerMixin, ModelSerializer):
    reporter = PointOfContactSerializer(required=True)
    recorder = PointOfContactSerializer(required=False)
    verifier = PointOfContactSerializer(required=False)
        
    class Meta:
        model = OccurrenceObservation
        exclude = ('id',)


class AnimalLifestagesSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = AnimalLifestages
        exclude = ('id',)

class BaseDetailsSerializer(ModelSerializer):
    def to_representation(self, instance):
        if instance:
            #self.set_model_class(instance.occurrencetaxon.get_details_class())
            instance = instance.occurrencetaxon.get_details()
        return super(BaseDetailsSerializer, self).to_representation(instance)
    
class LandAnimalDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    lifestages = AnimalLifestagesSerializer(required=False)
    class Meta:
        model = LandAnimalDetails
        exclude = ('id',)

class WetlandVetegationStructureSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = WetlandVetegationStructure
        exclude = ('id',)

class WetlandAnimalDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    lifestages = AnimalLifestagesSerializer(required=False)
    vegetation = WetlandVetegationStructureSerializer(required=False)
    class Meta:
        model = WetlandAnimalDetails
        exclude = ('id',)


class StreamSubstrateSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = StreamSubstrate
        exclude = ('id',)

class StreamAnimalDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    lifestages = AnimalLifestagesSerializer(required=False)
    substrate = StreamSubstrateSerializer(required=False)
    class Meta:
        model = StreamAnimalDetails
        exclude = ('id',)

class PondLakeAnimalDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    lifestages = AnimalLifestagesSerializer(required=False)
    class Meta:
        model = PondLakeAnimalDetails
        exclude = ('id',)

class ConiferLifestagesSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = ConiferLifestages
        exclude = ('id',)


class DisturbanceTypeSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = DisturbanceType
        exclude = ('id',)

class EarthwormEvidenceSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = EarthwormEvidence
        exclude = ('id',)

class ConiferDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    lifestages = ConiferLifestagesSerializer(required=False)
    disturbance_type = DisturbanceTypeSerializer(required=False)
    earthworm_evidence = EarthwormEvidenceSerializer(required=False)
    
    class Meta:
        model = ConiferDetails
        exclude = ('id',)

class FernDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    disturbance_type = DisturbanceTypeSerializer(required=False)
    earthworm_evidence = EarthwormEvidenceSerializer(required=False)
    #lifestages = FernLifestages(required=False) # FIXME
    class Meta:
        model = FernDetails
        exclude = ('id',)

class FloweringPlantDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    disturbance_type = DisturbanceTypeSerializer(required=False)
    earthworm_evidence = EarthwormEvidenceSerializer(required=False)
    #lifestages = FloweringPlantLifestages(required=False) # FIXME
    class Meta:
        model = FloweringPlantDetails
        exclude = ('id',)
    
class MossDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    disturbance_type = DisturbanceTypeSerializer(required=False)
    earthworm_evidence = EarthwormEvidenceSerializer(required=False)
    #lifestages = MossLifestages(required=False) # FIXME
    class Meta:
        model = MossDetails
        exclude = ('id',)


class SlimeMoldLifestagesSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = SlimeMoldLifestages
        exclude = ('id',)

class SlimeMoldDetailsSerializer(CustomModelSerializerMixin, BaseDetailsSerializer):
    lifestages = SlimeMoldLifestagesSerializer(required=False)
    class Meta:
        model = SlimeMoldDetails
        exclude = ('id',)


""" --------------------------------------------
PHOTOGRAPHS
------------------------------------------------ """

class PhotographPublishSerializer(Serializer):
    """
    Used to publish new photographs
    """ 
    image = serializers.ListField(
        child=ImageField(max_length=1000,
            allow_empty_file=False,
            use_url=True))
    featuretype = rest_fields.CharField()
    occurrence_fk = rest_fields.IntegerField()
    image_id = rest_fields.IntegerField(required=False, read_only=True)
    thumbnail = rest_fields.CharField(required=False, read_only=True)
    description = rest_fields.CharField(required=False, allow_blank=True)
    notes = rest_fields.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        try:
            ft = data.get("featuretype")
            fk = data.get("occurrence_fk")
            ft_model = get_occurrence_model(ft)
            ft_model.objects.get(pk=fk)
        except:
            raise serializers.ValidationError(_("occurrence_fk: Not a valid occurrence"))
        return data
                      
    class Meta:
        model = Photograph
        fields = ('image', 'featuretype', 'occurrence_fk')

    def create(self, validated_data):
        image=validated_data.pop('image')
        ft = validated_data.pop("featuretype")
        ft_model = get_occurrence_model(ft)
        content_type = ContentType.objects.get_for_model(ft_model)
        response = {
            "image": [],
            "featuretype": ft,
            "occurrence_fk": validated_data.get("occurrence_fk")
            }
        for img in image:
            photo = Photograph.objects.create(image=img, content_type_id=content_type.id, **validated_data)
            #photo.thumbnail = create_thumbnail(img, photo.image.path)
            response['image'].append(photo.image)
        if len(response['image'])==1:
            response['image_id'] = photo.id
            response['thumbnail'] = photo.thumbnail.url
        return response

class PhotographSerializer(ModelSerializer):
    """
    Used to list photographs
    """
    class Meta:
        model = Photograph
        fields = '__all__'
        #exclude = ('occurrence_fk', 'occurrence', 'content_type') 

""" -------------------------------------------
OCCURRENCE SERIALIZER
---------------------------------------------- """
class OccurrenceSerializer(UpdateOccurrenceMixin, Serializer):
    """
    Manages serialization/deserialization of Occurrences
    """
    id = rest_fields.IntegerField(required=False, read_only=True)
    featuretype = rest_fields.CharField(required=False, read_only=True)
    featuresubtype = rest_fields.CharField(read_only=True)
    released = rest_fields.NullBooleanField(required=False, read_only=False)
    verified = rest_fields.NullBooleanField(required=False, read_only=False)
    version = rest_fields.IntegerField(required=False, read_only=True)
    total_versions = TotalVersionsField(required=False, read_only=True)
    inclusion_date = rest_fields.DateTimeField(required=False, read_only=True)
    version_date = rest_fields.DateTimeField(required=False, read_only=True)
    #geom = gisserializer.GeometryField()
    polygon = gisserializer.GeometryField(required=False)
    observation = OccurrenceObservationSerializer(required=True)
    
    def get_fields(self):
        fields = Serializer.get_fields(self)
        
        if self.instance and self.instance.occurrence_cat:
            self.featuresubtype = self.instance.occurrence_cat.code
        
        fields['details'] = get_details_serializer(self.featuresubtype)(required=False)
        return fields
    
    def to_representation(self, instance):
        if isinstance(instance, OccurrenceTaxon):
            details_name = instance.get_details_class().__name__.lower()
            setattr(instance, details_name, instance.get_details())
        r = Serializer.to_representation(self, instance)

        result = to_flat_representation(r)
        result["id"] = r["id"]
        
        if self.is_writer or self.is_publisher:
            result["version"] = instance.version
            result["total_versions"] = instance.version
        else:
            result["version"] = instance.released_versions
            result["total_versions"] = instance.released_versions
        result['featuretype'] = instance.occurrence_cat.main_cat
        result['featuresubtype'] = instance.occurrence_cat.code
        result['version_date'] = instance.inclusion_date
        photo_serializer = PhotographSerializer(instance.photographs, many=True)
        result['images'] = photo_serializer.data
        result['is_writer'] = self.is_writer
        result['is_publisher'] = self.is_publisher
        if instance.location and isinstance(instance.location.polygon, Polygon):
            result['polygon'] = instance.location.polygon.geojson
        return result
    
    def to_nested_representation(self, data):
        formvalues = OrderedDict()
        for global_field_name in data: # transform the flat object to a set of dictionaries of forms
            field_parts = global_field_name.split(".")
            if len(field_parts)>1:
                base = formvalues
                for local_field_name in field_parts[:-1]:
                    base[local_field_name] = base.get(local_field_name, {})
                    if base[local_field_name] is None:
                        base[local_field_name] = {}
                    base = base[local_field_name]
                if not (isinstance(base.get(field_parts[-1]), dict) and data[global_field_name] is None):  # avoid overwritting new values with old empty forms
                    base[field_parts[-1]] = data[global_field_name]
            else:
                if not (isinstance(formvalues.get(global_field_name), dict) and data[global_field_name] is None): # avoid overwritting new values with old empty forms 
                    formvalues[global_field_name] = data[global_field_name]
        return formvalues
    
    def to_internal_value(self, data):
        
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise rest_fields.ValidationError({
                rest_fields.api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        validated_formvalues = OrderedDict()
        errors = OrderedDict()
        self.featuresubtype = data.get("featuresubtype")
        self.to_internal_value_extra(data, validated_formvalues, errors)
        
        fields = self._writable_fields
        
        # transform the flat object to a set of dictionaries of forms
        formvalues = self.to_nested_representation(data)

        for field in fields: # validate values
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            if isinstance(field, ModelSerializer):
                primitive_value = field.get_value(formvalues)
                if check_all_null(primitive_value) and not field.required:
                    continue
            else:
                primitive_value = field.get_value(formvalues)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except rest_fields.ValidationError as exc:
                errors[field.field_name] = exc.detail
            except rest_fields.DjangoValidationError as exc:
                errors[field.field_name] = rest_fields.get_error_detail(exc)
            except rest_fields.SkipField:
                pass
            else:
                rest_fields.set_value(validated_formvalues, field.source_attrs, validated_value)

        validated_formvalues = validated_formvalues
        validated_formvalues["released"] = data.get("released", False)
        validated_formvalues["verified"] = data.get("verified", False)
        validated_formvalues['featuretype'] = data.get("featuretype")
        validated_formvalues['featuresubtype'] = data.get("featuresubtype")
            
        if isinstance(validated_formvalues.get('polygon'), Polygon):
            location = validated_formvalues.get('location', {})
            location['polygon'] = validated_formvalues.pop('polygon')
            validated_formvalues['location'] = location
        
        try:
            geom_serializer = gisserializer.GeometryField()
            validated_formvalues['geom'] = geom_serializer.to_internal_value(data.get("geom"))
        except:
            if not data.get('id'):
                errors["geom"] = [_("Geometry is missing")]

        if errors:
            raise rest_fields.ValidationError(to_flat_representation(errors))

        return validated_formvalues

class TaxonLocationSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = TaxonLocation
        exclude = ('id', 'polygon')

class NaturalAreaElementSerializer(CustomModelSerializerMixin, ModelSerializer):
    disturbance_type = DisturbanceTypeSerializer(required=False)
    earthworm_evidence = EarthwormEvidenceSerializer(required=False)
    #lifestages = MossLifestages(required=False) # FIXME
    class Meta:
        model = ElementNaturalAreas
        exclude = ('id',)

class NaturalAreaLocationSerializer(CustomModelSerializerMixin, ModelSerializer):
    class Meta:
        model = NaturalAreaLocation
        exclude = ('id', 'polygon')

class TaxonOccurrenceSerializer(OccurrenceSerializer, Serializer):
    species = SpeciesSerializer(required=False)
    voucher = VoucherSerializer(required=False)
    location = TaxonLocationSerializer(required=False)
    
    def to_internal_value_extra(self, data, result, errors):
        species_id = data.get('species.id')
        if not species_id:
            errors["species"] = [_("No species was selected")]

class NaturalAreaOccurrenceSerializer(OccurrenceSerializer, Serializer):
    element = NaturalAreaElementSerializer(required=False)
    location = NaturalAreaLocationSerializer(required=False)
    
    def to_internal_value_extra(self, data, result, errors):
        pass

""" -------------------------------------------
LAYERS
---------------------------------------------- """

class LayerSerializer(gisserializer.GeoFeatureModelSerializer):
    id = rest_fields.IntegerField(required=False, read_only=True)
    featuretype = rest_fields.CharField(required=False, read_only=True)
    featuresubtype = rest_fields.CharField()
    released = rest_fields.BooleanField(required=False, read_only=True)
    inclusion_date = rest_fields.DateTimeField(required=False, read_only=True)
    verified = rest_fields.BooleanField(required=False, read_only=True)
    version = rest_fields.IntegerField(required=False, read_only=True)
    total_versions = rest_fields.IntegerField(required=False, read_only=True)
    
    def __init__(self, *args, **kwargs):
        self.is_writer_or_publisher = kwargs.pop('is_writer_or_publisher', False)
        super(LayerSerializer, self).__init__(*args, **kwargs)
    
    def get_properties(self, instance, fields):
        result = {}
        if self.is_writer_or_publisher:
            result['total_versions'] = instance.version
        else:
            result['total_versions'] = instance.released_versions
        result['version'] = instance.version
        result['featuretype'] = instance.occurrence_cat.main_cat
        result['featuresubtype'] = instance.occurrence_cat.code
        result['released'] = instance.released
        result['verified'] = instance.verified
        result['inclusion_date'] = instance.inclusion_date
        result['id'] = instance.id
        return result
    
    class Meta:
        model = OccurrenceTaxon
        geo_field = "geom"
        fields = ('id', 'featuretype', 'featuresubtype', 'inclusion_date', 'released', 'verified', 'version', 'total_versions')

class ListSerializer(gisserializer.GeoFeatureModelSerializer):
    id = rest_fields.IntegerField(required=False, read_only=True)
    featuretype = rest_fields.CharField(required=False, read_only=True)
    featuresubtype = rest_fields.CharField()
    released = rest_fields.BooleanField(required=False, read_only=True)
    inclusion_date = rest_fields.DateTimeField(required=False, read_only=True)
    verified = rest_fields.BooleanField(required=False, read_only=True)
    version = rest_fields.IntegerField(required=False, read_only=True)
    total_versions = rest_fields.IntegerField(required=False, read_only=True)
    
    def __init__(self, *args, **kwargs):
        self.is_writer_or_publisher = kwargs.pop('is_writer_or_publisher', False)
        super(ListSerializer, self).__init__(*args, **kwargs)
    
    
    class Meta:
        model = OccurrenceTaxon
        geo_field = "geom"
        fields = ('id', 'featuretype', 'featuresubtype', 'inclusion_date', 'released', 'verified', 'version', 'total_versions')


class TaxonListSerializer(ListSerializer):    
    def get_properties(self, instance, fields):
        result = {}
        if self.is_writer_or_publisher:
            result['total_versions'] = instance.version
        else:
            result['total_versions'] = instance.released_versions
        result['version'] = instance.version
        result['featuretype'] = instance.occurrence_cat.main_cat
        result['featuresubtype'] = instance.occurrence_cat.code
        result['released'] = instance.released
        result['verified'] = instance.verified
        result['inclusion_date'] = instance.inclusion_date
        result['id'] = instance.id
        result['species.id'] = instance.species.id
        result['species.first_common'] = instance.species.first_common
        result['species.name_sci'] = instance.species.name_sci
        result['observation.observation_date'] = instance.observation.observation_date
        return result


class NaturalAreaListSerializer(ListSerializer):    
    def get_properties(self, instance, fields):
        result = {}
        if self.is_writer_or_publisher:
            result['total_versions'] = instance.version
        else:
            result['total_versions'] = instance.released_versions
        result['version'] = instance.version
        result['featuretype'] = instance.occurrence_cat.main_cat
        result['featuresubtype'] = instance.occurrence_cat.code
        result['released'] = instance.released
        result['verified'] = instance.verified
        result['inclusion_date'] = instance.inclusion_date
        result['id'] = instance.id
        result['natural_area_element.id'] = instance.natural_area_element.id
        result['natural_area_element.general_description'] = instance.natural_area_element.general_description
        result['natural_area_element.type'] = instance.natural_area_element.type
        result['natural_area_element.natural_area_code_nac'] = instance.natural_area_element.natural_area_code_nac
        result['observation.observation_date'] = instance.observation.observation_date
        return result

""" -------------------------------------------
FEATURE TYPES
---------------------------------------------- """
class FeatureTypeSerializer():
    def __init__(self, occurrence_cat, is_writer=False, is_publisher=False):
        self.is_writer = is_writer
        self.is_publisher = is_publisher
        self.occurrence_cat = occurrence_cat
        if occurrence_cat:
            init_forms(self, occurrence_cat.code)
    
    def get_feature_type(self):
        result = {}
        result['featuretype'] = self.occurrence_cat.main_cat
        result['featuresubtype'] = self.occurrence_cat.code
        forms = []
        for formdef in self.forms:
            form = {}
            form_name = formdef[0]
            form['formlabel'] = _(form_name)
            form['formname'] = form_name
            if form_name != MANAGEMENT_FORM_NAME:
                form['formitems'] = self.get_form_featuretype(form_name, formdef[1])
            else:
                if self.is_publisher:
                    form['formitems'] = MANAGEMENT_FORM_ITEMS_PUBLISHER
                else:
                    form['formitems'] = MANAGEMENT_FORM_ITEMS
            forms.append(form)
        result['forms'] = forms
        return result

    def get_form_featuretype(self, form_name, model):
        fields = model._meta.get_fields()
        result = []
        for f in fields:
            fdef = {}

            if getattr(f, 'primary_key', False):
                pass
                #fdef['type'] = 'pk'
            elif isinstance(f, CharField) or isinstance(f, TextField):
                fdef['type'] = 'string'
            elif isinstance(f, BooleanField):
                fdef['type'] = 'boolean'
            elif isinstance(f, NullBooleanField):
                fdef['type'] = 'boolean'
            elif isinstance(f, DateTimeField):
                fdef['type'] = 'datetime'
            elif isinstance(f, DateField):
                fdef['type'] = 'date'
            elif isinstance(f, GeometryField):
                # skip geoms
                pass
            elif isinstance(f, FloatField) or isinstance(f, DecimalField):
                fdef['type'] = 'double'
            elif isinstance(f, IntegerField):
                fdef['type'] = 'integer'
            elif getattr(f, 'related_model', False):
                if issubclass(f.related_model, DictionaryTable) or issubclass(f.related_model, DictionaryTableExtended):
                    fdef['type'] = 'stringcombo'
                    items = []
                    for item in f.related_model.objects.all():
                        idef = {}
                        idef['key'] = item.code
                        idef['value'] = item.name
                        items.append(idef)
                    fdef['values'] = {'items': items}
                else:
                    #fdef['type'] = 'fk'
                    pass
                
            if 'type' in fdef:
                fdef['mandatory'] = (not getattr(f, "null", True) and not getattr(f, "blank", True))
                if not (self.is_writer or self.is_publisher):
                    fdef['readonly'] = True
                fdef['key'] = form_name + "." + f.name
                fdef['label'] = _(f.name)
                result.append(fdef)
        return result


class OccurrenceVersionSerializer():
    def is_related_field(self, f):
        if not getattr(f, 'related_model', False):
            return False
        if getattr(f, 'auto_created', False):
            return False
        return True
    
    def is_dict_model(self, related_model):
        if issubclass(related_model, DictionaryTable):
            return True
        if issubclass(related_model, DictionaryTableExtended):
            return True
        return False
    
    def get_related_fields(self, model_meta):
        rel_fields = []
        for f in model_meta.get_fields():
            if self.is_related_field(f):
                rel_fields.append((f.name, f.attname, f.related_model))
        return rel_fields
    
    def add_related_values(self, obj_dict, model_meta, revision_date):
        for (rel_field_name, rel_attname, rel_field_model) in self.get_related_fields(model_meta):
            rel_id = obj_dict.get(rel_attname)
            rel_field_model = self.get_instance_model(obj_dict, rel_field_model)
            if rel_id is None:
                obj_dict[rel_field_name] = None
            elif self.is_dict_model(rel_field_model):
                obj_dict[rel_field_name] = rel_field_model.objects.get(pk=rel_id).code
            else:
                obj_dict[rel_field_name] = self.get_version_from_model(rel_field_model, rel_id, revision_date)
            del obj_dict[rel_attname]
        return obj_dict
        
    def get_version_from_model(self, model, id, revision_date):
        obj_versions = Version.objects.get_for_object_reference(model, id).filter(revision__date_created__lte=revision_date)
        if len(obj_versions)>0: 
        #try:
            requested_version = obj_versions[0]
            requested_obj = requested_version.field_dict
            return self.add_related_values(requested_obj, model._meta, revision_date)
        #except:
        #    pass
    
    def get_instance_model(self, parent_instance, model):
        if issubclass(model, TaxonDetails):
            category_code = parent_instance.get('occurrence_cat')
            category = OccurrenceCategory.objects.get(code=category_code)
            return get_details_class(category.code)
        return model 
    
    def get_version(self, instance, version, exclude_unreleased=False):
        """
        Gets a dict representing a particular version of the occurrence
        
        instance: an instance of the last version of the occurrence
        version: the requested version 
        """
        versions = Version.objects.get_for_object(instance)
        if exclude_unreleased:
            total_versions = instance.released_versions
            num_released_version = total_versions
            for v in versions:
                if v.field_dict.get('released', False):
                    if num_released_version != version:
                        num_released_version = num_released_version - 1
                    else:
                        requested_version = v
                        break
        else:
            total_versions = instance.version
            version_internal = total_versions - version
            requested_version = versions[version_internal]

        revision_date = requested_version.revision.date_created
        
        result = self.add_related_values(requested_version.field_dict, instance._meta, revision_date)
        if result.get('location') and isinstance(result.get('location').get('polygon'), Polygon):
            result['polygon'] = result.get('location').pop('polygon').geojson
        result['geom'] = {'type': 'Point', 'coordinates': result['geom'].coords}
        result['total_versions'] = total_versions
        result['version'] = version
        result['version_date'] = revision_date
        return to_flat_representation(result)

""" -------------------------------------------
SPECIES SEARCH
---------------------------------------------- """
class SpeciesSearchSerializer(ModelSerializer):
    name = SerializerMethodField()

    def get_name(self, obj):
        return '{} - {}'.format(obj.first_common, obj.name_sci) 
    
    class Meta:
        model = Species
        fields = ('id', 'name')

class SpeciesSearchResultSerializer(ModelSerializer):
    element_species = ElementSpeciesSerializer(required=False)
    
    class Meta:
        model = Species
        fields = "__all__"
        
    def to_representation(self, instance):
        r = super(SpeciesSearchResultSerializer, self).to_representation(instance)
        return to_flat_representation(r, 'species')

