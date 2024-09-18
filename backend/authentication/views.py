from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import pandas as pd
import secrets
from django.contrib.auth.hashers import make_password

from .models import Roles, User
from .serializers import (
    UserSerializer,
    UserBasicInfoSerializer
)
from .validators import (
    duplicated_email_validation,
    password_confirmation_validation
)

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_data = serializer.validated_data
        user_data['password_confirmation'] = request.data['password_confirmation']

        # TODO: alterar função para retornar erro ao invés de lançar exceção
        duplicated_email_validation(user_data["email"])
        password_confirmation_validation(user_data["password"], user_data["password_confirmation"])

        user_data.pop("password_confirmation")

        user = User.objects.create_user(**user_data)
        user.set_password(user_data["password"])
        user.save()

        user_serialized = UserSerializer(user)

        return Response(user_serialized.data, status=status.HTTP_201_CREATED)

    def retrieve_self(self, request):
        user = User.objects.filter(id=request.user.id)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve_basic_info_by_id(self, request, pk):
        user = User.objects.get(id=pk)
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserBasicInfoSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def list(self, request):
        active_users = User.objects.filter(is_active=True)

        serializer = UserBasicInfoSerializer(active_users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RegisterMultipleView(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)

    def register_multiple(self, request, *args, **kwargs):
        file = request.FILES['file']
        if not file.name.endswith('.xlsx'):
            return Response({"error": "Invalid file format. Please upload an Excel file."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        for index, row in df.iterrows():
            user_data = {
                'email': row['email'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'password': make_password(secrets.token_urlsafe(8)),
                'role': Roles.convert_to_int_if_string(row['role'])
            }
            serializer = UserSerializer(data=user_data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # TODO: alterar função para retornar erro ao invés de lançar exceção
            duplicated_email_validation(user_data["email"])

            # TODO: verificar se o set_password já não é chamado pelo create_user
            user = User.objects.create_user(**user_data)
            user.set_password(user_data["password"])
            user.save()

            # TODO: enviar senha por e-mail para o usuário

        return Response({"message": "Users created successfully"}, status=status.HTTP_201_CREATED)