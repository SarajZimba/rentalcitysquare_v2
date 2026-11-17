from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from user.models import Customer
from ..serializers.user import CustomTokenPairSerializer, CustomerSerializer

from rest_framework.viewsets import ModelViewSet

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenPairSerializer


class CustomerAPI(ModelViewSet):
    serializer_class = CustomerSerializer
    model = Customer
    queryset = Customer.objects.active()
    pagination_class = None

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from api.serializers.user import AgentSerializer
from django.contrib.auth.models import Group


class AgentViewSet(viewsets.ViewSet):
    serializer_class = AgentSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            usercode = serializer.validated_data['username']
            full_name = serializer.validated_data['full_name']

            user = User.objects.create(username=usercode, full_name=full_name, is_superuser=False, is_staff=True)

            user.set_password(usercode)
            user.save()

            group = Group.objects.get(name="agent")
            user.groups.add(group)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
        
            return Response({"detail":"User with the username or email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
from rest_framework import generics
# from .models import Customer
# from .serializers import CustomerSerializer

class CustomerDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CustomerSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return Customer.objects.active()  # Ensure you have the correct queryset
    
from rest_framework import generics
# from .models import Customer
# from .serializers import CustomerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

class CustomerListAPIView(APIView):

    def get(self, request):

        customers = Customer.objects.filter(is_deleted=False)
        serializer = CustomerSerializer(customers, many=True)
        return Response (serializer.data, 200)  # Ensure you have the correct queryset