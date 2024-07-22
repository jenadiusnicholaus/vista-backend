from django.shortcuts import render

from property.serializers import  CreatePropertyReviewSerializers, GetCategorySerializers, GetPropertyDetailsSerializers, PropertySerializers
from user_data.models import MyFavoriteProperty
from .models import Category, Property, PropertyReview
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from property.paginators import CustomPageNumberPagination, CustomPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

class GetPropertysPaginationView(viewsets.ModelViewSet):
    queryset = Property.objects.filter(publication_status=True).order_by("-created_at")
    serializer_class = PropertySerializers
    pagination_class = CustomPageNumberPagination

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
                ).order_by("-created_at")
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
    

class GetCategoriesView(viewsets.ModelViewSet):
    queryset = Category.objects.filter(published=True)
    serializer_class = GetCategorySerializers
    permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class ReviewThePropertyView(viewsets.ModelViewSet):
    queryset = PropertyReview.objects.all()
    serializer_class = CreatePropertyReviewSerializers
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())    
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        property_id = request.query_params.get("property_id", None)
        user = request.user
        comment = request.data.get("comment", None)
        rating = request.data.get("rating", None)
        serializers = self.get_serializer(data={
            "property": property_id,
            "user": user.id,
            "comment": comment,
            "rating": rating,
        })
        if serializers.is_valid():
            serializers.save()
            return Response(
              
                {
                    "message": "Review added successfully.",
                },
              
                status=status.HTTP_201_CREATED
            )
            
        else:   
            return Response(serializers.errors, status=400)



       

