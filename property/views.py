from django.shortcuts import render

from property.serializers import  GetPropertyDetailsSerializers, PropertySerializers
from .models import Property
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from property.paginators import CustomPagination


# Create your views here.


class GetPropertysPaginationView(viewsets.ModelViewSet):
    queryset = Property.objects.filter(publication_status=True).order_by("-created_at")
    serializer_class = PropertySerializers
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        if request.query_params.get("category", None) == "all":
            queryset = self.filter_queryset(self.get_queryset()).order_by(
                "-created_at"
            )
        else:
            queryset = self.filter_queryset(
                self.get_queryset().filter(
                    category=request.query_params.get("category", None)
                )
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)
    
class GetPropertyDetailsViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(publication_status=True)
    serializer_class = GetPropertyDetailsSerializers
    permission_classes = [AllowAny]

    def get_object(self):
        id = self.request.query_params.get("id", None)
        if id is None:
            raise ValueError("id parameter is required.")
        return Property.objects.get(id=id)

    
    def list(self, request, *args, **kwargs):
        print(request.query_params.get("id", None)  )
        try:
            instance = self.get_object()
        except Property.DoesNotExist:
            return Response({"error": "Property not found."}, status=404)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
