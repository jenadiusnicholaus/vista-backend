from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "_limit"
    offset_query_param = "_start"
