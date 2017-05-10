import jsonschema
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.db.models.query import QuerySet
from django.contrib.gis.db import models
from rest_framework import viewsets, renderers, parsers, serializers, mixins, permissions
from rest_framework.response import Response
from rest_framework_jsonp.renderers import JSONPRenderer
from jsonschema.exceptions import ValidationError as JsonValidationError
from isodate.isoerror import ISO8601Error
from .serializers import ContextSerializer, SubscriptionSerializer
from .schemas import SUBSCRIPTION_CREATION_SCHEMA, SUBSCRIPTION_UPDATE_SCHEMA, GET_CONTEXT_SCHEMA
from .pagination import ResultOffsetPagination
from .models import Subscription
from .consts import ELEMENT_KEY, RESPONSES_KEY
from .utils import get_fields


class NgsiViewSet(viewsets.GenericViewSet):
    serializer_class = ContextSerializer
    pagination_class = ResultOffsetPagination
    renderer_classes = (
        renderers.JSONRenderer, JSONPRenderer,
    )
    parser_classes = (parsers.JSONParser,)
    lookup_field = 'slug'
    
    def get_ngsi_404_response(self):
        status_key, status_value = self.serializer_class.get_not_found_items()
        return Response({status_key: status_value})
        
    def get_ngsi_response(self, content, attributes=[]):
        
        def valid_attributes(object):
            if attributes:
                fields = object._meta.get_all_field_names()
                return all(each in fields for each in attributes)
            return True
        
        if not content:
            return self.get_ngsi_404_response()
        if isinstance(content, models.Model):
            if not valid_attributes(content):
                return self.get_ngsi_404_response()
            serializer = self.get_serializer(content, many=False, attributes=attributes)
            return Response(serializer.data)
        else:
            if not valid_attributes(content.model):
                return self.get_ngsi_404_response()
            page = self.paginate_queryset(content)
            serializer = self.get_serializer(page, many=True, attributes=attributes)
            return self.get_paginated_response(serializer.data)
        
    def get_model_class(self, name):
        raise NotImplementedError()
    
    def get_model_queryset(self, entity_type, **kwargs):
        model = self.get_model_class(entity_type)
        if model:
            return model.objects.filter(**kwargs)
        
    def get_model_instance(self, entity_type, entity_id):
        queryset = self.get_model_queryset(entity_type, pk=entity_id)
        if queryset:
            if queryset.exists():
                return queryset.latest('id')

    
class ContextEntities(NgsiViewSet):    
    lookup_value_regex = r'[a-z]+_[0-9]+'
    #
    # def get_lookup_regex(self):
    #     return self.lookup_value_regex
    #
    def get_object(self, request, slug):
        name, pk = slug.split('_')
        return self.get_model_instance(name, pk)


class ContextTypes(NgsiViewSet):
    # lookup_value_regex = r'[a-z]+'
    
    def get_context_types(self):
        raise NotImplementedError()
        
    def retrieve(self, request, slug):
        queryset = self.get_model_queryset(slug)
        if queryset and self.filter_class:
            queryset = self.filter_class(request.GET, queryset=queryset)
        return self.get_ngsi_response(queryset)
        
    def list(self, request):  
        types = []
        for name, model in self.get_context_types().iteritems():
            types.append({
                'attributes': [each.name for each in get_fields(model)],
                'name': name
            })
        status_key, status_value = self.serializer_class.get_ok_items()
        return Response({
            "types": types,
            status_key: status_value
        })


class ModelContextTypes(mixins.ListModelMixin, NgsiViewSet):
    # queryset = User.objects.all()
    pass
    


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
    
class QueryContext(NgsiViewSet):

    def perform_authentication(self, request):
        pass

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(QueryContext, self).dispatch(*args, **kwargs)
    
    def create(self, request):
        try:
            jsonschema.validate(request.data, GET_CONTEXT_SCHEMA)
        except JsonValidationError as e:
            return Response(status=400)
        else:
            attributes = request.data.get('attributes', None)
            objects = []
            for each in request.data['entities']:
                instance = self.get_model_instance(each['type'], each['id'])
                if instance: 
                    objects.append(instance)
                else:
                    return self.get_ngsi_404_response()
            serializer = self.get_serializer(objects, many=True, attributes=attributes)
            return self.get_paginated_response(serializer.data)


class ContextSubscriptions(NgsiViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def iter_model_instances(self, entities):
        for each in entities:
            yield self.get_model_instance(each['type'], each['id'])

    def get_model_instances(self, entities):
        return [
            each for each in self.iter_model_instances(entities)
        ]

    def get_condition_values(self, notify_conditions):
        result = set()
        for each in notify_conditions:
            for value in each.get('condValues',[]):
                result.add( value )
        return list(result)

    def create_payload_valid(self, request):
        data = request.data
        return Subscription.create(
            user       = request.user,
            target     = data['reference'],
            duration   = data.get('duration', None),
            attributes = data.get('attributes', []),
            conditions = self.get_condition_values(data['notifyConditions']),
            instances  = self.get_model_instances(data['entities'])
        )
        
    def update_payload_valid(self, request):
        data = request.data
        subscription = get_object_or_404(Subscription, pk=data['subscriptionId'])
        if subscription.user != request.user:
            raise PermissionDenied()
        else:
            return subscription.update(
                duration = data.get('duration', None),
                conditions = self.get_condition_values(
                    data.get('notifyConditions', [])
                )
            )

    def create(self, request):
        try:
            jsonschema.validate(request.data, SUBSCRIPTION_CREATION_SCHEMA)
        except JsonValidationError as e:
            return Response(status=400)
        else:
            try:
                subscription = self.create_payload_valid(request)
            except (ValidationError, ObjectDoesNotExist, ISO8601Error):
                return Response(status=400)
            else:
                serializer = self.get_serializer(subscription, many=False)
                return Response(serializer.data, status=201)

    def destroy(self, request, slug):
        get_object_or_404(Subscription, pk=slug).destroy()
        return Response(status=200)

    def update(self, request, slug):
        data = request.data
        try:
            jsonschema.validate(data, SUBSCRIPTION_UPDATE_SCHEMA)
        except JsonValidationError:
            return Response(status=400)
        else:
            if slug == data['subscriptionId']:
                subscription = self.update_payload_valid(request)
                serializer = self.get_serializer(subscription, many=False)
                return Response(serializer.data, status=200)
            else:
                return Response(status=400)
        