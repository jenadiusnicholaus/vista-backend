
from authentication.permissions import IsHost
from host_data.models import PropertyHost
from host_data.serializers import  HostPropertySerializers, PropertyAmenitiesSerializers, PropertyFacilitiesSerializers, PropertyImagesSerializers, PropertyRentingRequirementsSerializers, PropertyRulesSerializers
from property.models import Property, PropertyAmenity, PropertyFacility, PropertyImages, PropertyRentingRequirements, PropertyRules
from property.paginators import CustomPageNumberPagination
from property.serializers import PropertySerializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated  

# Create your views here.




class HostPropertysPaginationView(viewsets.ModelViewSet):
    queryset = Property.objects.filter(publication_status=True).order_by("-created_at")
    serializer_class = HostPropertySerializers
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsHost,IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset =  self.queryset.filter(host__user=user, publication_status=True).order_by("-created_at")    
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        try:
            host = PropertyHost.objects.get(user=request.user, is_verified=True)
        except PropertyHost.DoesNotExist:
            return Response({'message': 'Host not found'}, status=status.HTTP_404_NOT_FOUND)      
        data = {
            'name': request.data.get('name'),   
            'category': request.data.get('category_id'),   
            'price': request.data.get('price'),
            'currency': request.data.get('currency'),
            'period': request.data.get('period'),
            'description': request.data.get('description'),
            'address': request.data.get('address'),
            'city': request.data.get('city'),
            "business_type": request.data.get('business_type'),
            'country': request.data.get('country'),
            'latitude': request.data.get('latitude'),
            'longitude': request.data.get('longitude'),
            'image': request.data.get('image'),
            "supported_geo_region": request.data.get('supported_geo_region'),
            'host': host.id,
            'availability_status':  True if request.data.get('availability_status') == 'true' else False,
            'publication_status': True if request.data.get('publication_status') == 'true' else False,

        }

        serializers = self.get_serializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response({
                'message': 'Property added successfully',
               
            }, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        try:
            host = PropertyHost.objects.get(user=request.user, is_verified=True)
        except PropertyHost.DoesNotExist:
            return Response({'message': 'Host not found'}, status=status.HTTP_404_NOT_FOUND)      
        try:
            property_id = request.query_params.get('property_id')
            property = Property.objects.get(id=property_id, host=host)
        except Property.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        data = {
            'name': request.data.get('name'),   
            'category': request.data.get('category_id'),   
            'price': request.data.get('price'),
            'currency': request.data.get('currency'),
            'period': request.data.get('period'),
            'description': request.data.get('description'),
            'address': request.data.get('address'),
            'city': request.data.get('city'),
            "business_type": request.data.get('business_type'),
            'country': request.data.get('country'),
            'latitude': request.data.get('latitude'),
            'longitude': request.data.get('longitude'),
            'image': request.data.get('image'),
            "supported_geo_region": request.data.get('supported_geo_region'),
            'host': host.id,
            'availability_status':  True if request.data.get('availability_status') == 'true' else False,
            'publication_status': True if request.data.get('publication_status') == 'true' else False,

        }

        serializers = self.get_serializer(property, data=data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        property_id = request.query_params.get('property_id')
        try:
            host = PropertyHost.objects.get(user=request.user, is_verified=True)
        except PropertyHost.DoesNotExist:
            return Response({'message': 'Host not found'}, status=status.HTTP_404_NOT_FOUND)      
        try:
            property = Property.objects.get(id=property_id, host=host)
        except Property.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        property.delete()
        return Response({'message': 'Property deleted successfully'}, status=status.HTTP_200_OK)
    

class PropertyRulesViewSet(viewsets.ModelViewSet):
    queryset = PropertyRules.objects.all()
    serializer_class = PropertyRulesSerializers
    permission_classes = [IsHost, IsAuthenticated]

    def get_object(self):
        return self.queryset.get(id=self.request.query_params.get('rule_id'))
       
    def list(self, request):
        property_id = request.query_params.get("property_id", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        queryset = self.queryset.filter(property=property)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 


    def create(self, request):
        property_id = request.query_params.get("property_id", None)
        rule = request.data.get("rule", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        data = {
            'property': property.id,
            'rule': rule
        }
        serializers = self.get_serializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, ):
        try:
            instance = self.get_object()
        except PropertyRules.DoesNotExist:
            return Response({'message': 'Rule not found'}, status=status.HTTP_404_NOT_FOUND)
        
        rule = request.data.get('rule')
        data = {
            'rule': rule
        }
        serializers = self.get_serializer(instance, data=data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        try:
            instance = self.get_object()
        except PropertyRules.DoesNotExist:
            return Response({'message': 'Rule not found'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({'message': 'Rule deleted successfully'}, status=status.HTTP_200_OK)
    
class PropertyImagesViewSet(viewsets.ModelViewSet):
    queryset = PropertyImages.objects.all()
    serializer_class = PropertyImagesSerializers
    permission_classes = [IsHost, IsAuthenticated]

    def get_object(self):
        return self.queryset.get(id=self.request.query_params.get('image_id'))
       
    def list(self, request):
        property_id = request.query_params.get("property_id", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        queryset = self.queryset.filter(property=property)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 


    def create(self, request):
        property_id = request.query_params.get("property_id", None)
        image = request.data.get("image", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        data = {
            'property': property.id,
            'image': image
        }
        serializers = self.get_serializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, ):
        try:
            instance = self.get_object()
        except PropertyImages.DoesNotExist:
            return Response({'message': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        
        image = request.data.get('image')
        data = {
            'image': image
        }
        serializers = self.get_serializer(instance, data=data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        try:
            instance = self.get_object()
        except PropertyImages.DoesNotExist:
            return Response({'message': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({'message': 'Image deleted successfully'}, status=status.HTTP_200_OK)
    
class PropertyFacilitiesViewSet(viewsets.ModelViewSet):
    queryset = PropertyFacility.objects.all()
    serializer_class = PropertyFacilitiesSerializers
    permission_classes = [IsHost, IsAuthenticated]

    def get_object(self):
        return self.queryset.get(id=self.request.query_params.get('facility_id'))
       
    def list(self, request):
        property_id = request.query_params.get("property_id", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        queryset = self.queryset.filter(property=property)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 


    def create(self, request):
        property_id = request.query_params.get("property_id", None)
        facility = request.data.get("facility", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        data = {
            'property': property.id,
            'facility': facility,
            "description": request.data.get('description')
        }
        serializers = self.get_serializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, ):
        try:
            instance = self.get_object()
        except PropertyFacility.DoesNotExist:
            return Response({'message': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
        
        facility = request.data.get('facility')
        data = {
            'facility': facility,
            'description': request.data.get('description')
        }
        serializers = self.get_serializer(instance, data=data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        try:
            instance = self.get_object()
        except PropertyFacility.DoesNotExist:
            return Response({'message': 'Facility not found'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({'message': 'Facility deleted successfully'}, status=status.HTTP_200_OK)  


class PropertyAmenitiesViewSet(viewsets.ModelViewSet):
    queryset = PropertyAmenity.objects.all()
    serializer_class = PropertyAmenitiesSerializers
    permission_classes = [IsHost, IsAuthenticated]

    def get_object(self):
        return self.queryset.get(id=self.request.query_params.get('amenity_id'))
       
    def list(self, request):
        property_id = request.query_params.get("property_id", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        queryset = self.queryset.filter(property=property)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 


    def create(self, request):
        property_id = request.query_params.get("property_id", None)
        amenity = request.data.get("name", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        data = {
            'property': property.id,
            'name': amenity,
            'description': request.data.get('description')  
        }
        serializers = self.get_serializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, ):
        try:
            instance = self.get_object()
        except PropertyAmenity.DoesNotExist:
            return Response({'message': 'Amenity not found'}, status=status.HTTP_404_NOT_FOUND)
        
        amenity = request.data.get('name')
        data = {
            'name': amenity,
            'description': request.data.get('description')
        }
        serializers = self.get_serializer(instance, data=data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        try:
            instance = self.get_object()
        except PropertyAmenity.DoesNotExist:
            return Response({'message': 'Amenity not found'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({'message': 'Amenity deleted successfully'}, status=status.HTTP_200_OK) 
    
class PropertyRentingRequirementsViewSet(viewsets.ModelViewSet):
    queryset = PropertyRentingRequirements.objects.all()
    serializer_class = PropertyRentingRequirementsSerializers
    permission_classes = [IsHost, IsAuthenticated]

    def get_object(self):
        return self.queryset.get(id=self.request.query_params.get('requirement_id'))
       
    def list(self, request):
        property_id = request.query_params.get("property_id", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'error': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        queryset = self.queryset.filter(property=property)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 


    def create(self, request):
        property_id = request.query_params.get("property_id", None)
        requirement = request.data.get("requirement", None)
        try:
            property = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return Response({'message': 'Property not found'}, status=status.HTTP_404_NOT_FOUND)      
        data = {
            'property': property.id,
            'requirement': requirement,
            'description': request.data.get('description')  
        }
        serializers = self.get_serializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, ):
        try:
            instance = self.get_object()
        except PropertyRentingRequirements.DoesNotExist:
            return Response({'message': 'Requirement not found'}, status=status.HTTP_404_NOT_FOUND)
        
        requirement = request.data.get('requirement')
        data = {
            'requirement': requirement,
            'description': request.data.get('description')
        }
        serializers = self.get_serializer(instance, data=data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request):
        try:
            instance = self.get_object()
        except PropertyRentingRequirements.DoesNotExist:
            return Response({'message': 'Requirement not found'}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response({'message': 'Requirement deleted successfully'}, status=status.HTTP_200_OK)
       
    
  
    







