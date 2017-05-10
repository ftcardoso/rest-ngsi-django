from django.conf import settings
from rest_framework import pagination, response
from .consts import RESPONSES_KEY


class ResultOffsetPagination(pagination.LimitOffsetPagination):
    default_limit = 25 # defaults to PAGE_SIZE
    max_limit = 50
    limit_query_param = 'results' # defaults to 'limit'
    
    def get_paginated_response(self, data):
        try:
            next_url, previous_url = self.get_next_link(), self.get_previous_link()
            link = ''
            if next_url:
                link += '<{next}>; rel="next"'.format(next=next_url)
                if previous_url:
                    link += ', <{previous}>; rel="previous"'.format(previous=previous_url)
            elif previous_url:
                link += '<{previous}>; rel="previous"'.format(previous=previous_url)
            return response.Response({RESPONSES_KEY: data}, headers={'Link': link})
        except: #?
            return response.Response({RESPONSES_KEY: data})
            