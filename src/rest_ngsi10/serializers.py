from django.contrib.gis.geos import LineString, Point
from django.contrib.gis.geos.collections import MultiPolygon
from django.conf import settings
from django.db.models import AutoField, ManyToManyField
from django.http import Http404
from rest_framework import serializers
from .consts import *
from .utils import get_fields
import gpolyencode



class SubscriptionSerializer(serializers.BaseSerializer):
    def to_representation(self, obj):
        return {
            "subscribeResponse": {
                "subscriptionId": obj.id
            }
        }
    

class ContextSerializer(serializers.BaseSerializer):
    
    @classmethod
    def get_ok_items(cls):
        return STATUS_KEY, {
            "code": 200,
            REASON_KEY: "OK",
        }
    
    @classmethod
    def get_not_found_items(cls):
        return ERROR_KEY, {
            "code": "404",
            REASON_KEY: "No context elements found"
        }
    
    
    def __init__(self, *args, **kwargs):
        self.attributes = kwargs.pop('attributes', None)
        super(ContextSerializer, self).__init__(*args, **kwargs)
         
    def to_representation(self, obj):
        """
        Takes the object instance that requires serialization, and should 
        return a primitive representation
        """
        
        def get_typename_from_field(field):
            typename = field.__class__.__name__
            typename = typename.split('Field')[0].lower()
            if typename in ['auto']:
                return 'integer' 
            elif typename in ['text', 'foreignkey']:
                return 'string'
            elif typename in ['json']:
                return 'object'
            else:
                return typename
        
        def get_typename(field, value):
            if isinstance(value, Point):
                return 'coords'
            return get_typename_from_field(field)
        
        def get_value(value):
            if isinstance(value, Point):
                return "{lat}, {lon}".format(lat=value.coords[1], lon=value.coords[0])
            elif isinstance(value, bool):
                return str(value).lower()
            elif isinstance(value, list):
                return [get_value(each) for each in value]
            elif isinstance(value, dict):
                return {k: get_value(v) for k,v in value.iteritems()}
                # return value
            elif value == None:
                return value
            return unicode(value)

        def get_attributes(obj):
            result = []
            fields = get_fields(obj, self.attributes)
            for field in fields:
                if isinstance(field, ManyToManyField):
                    result.append({
                        'value': [str(i) for i in getattr(obj, field.name).all()],
                        'type': 'array',
                        'name': field.name, 
                    })
                else:
                    value = getattr(obj, field.name)
                    subjson = {
                        'value': get_value(value),
                        'type': get_typename(field, value),
                        'name': field.name,
                    }
                    if isinstance(value, Point):
                        subjson["metadatas"] = [{
                            "name": "location",
                            "type": "string",
                            "value": "WGS84"
                        }]
                    result.append(subjson)
            if hasattr(obj, 'translations'):
                if self.attributes and 'translations' not in self.attributes:
                    pass
                elif obj.translations.all().exists():
                    subjson = {
                        'name': 'translations',
                        'type': 'object',
                        'value': []
                    }
                    for each in obj.translations.values():
                        each.pop('id')
                        each.pop('i18n_source_id')
                        subjson['value'].append(each)
                    result.append(subjson)
            return result
        
        typename = obj.__class__.__name__.lower()
        status_key, status_value = self.get_ok_items()
        return {
            ELEMENT_KEY: {
                "attributes": get_attributes(obj),
                "id": str(obj.pk),
                "type": typename, 
            },
            status_key: status_value
        }
    