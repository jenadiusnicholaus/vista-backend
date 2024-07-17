from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination




class CustomPagination(LimitOffsetPagination):
    # default_limit = 10
    limit_query_param = "_limit"
    offset_query_param = "_start"


class CustomPageNumberPagination(PageNumberPagination):
    # django_paginator_class = 'django.core.paginator.Paginator'  # Default, change if needed
    page_size = 10  # Override PAGE_SIZE setting
    page_query_param = 'page_number'
    page_size_query_param = 'page_size'  # Allow client to set page size
    max_page_size = 10  # Maximum page size the client can request
    last_page_strings = ('last',)  # Recognize "last" as a request for the last page
    template = None  # Disable HTML pagination controls (set to a template path to enable)
