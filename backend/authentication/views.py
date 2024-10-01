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
)
from .utils import send_password_in_email

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def register(self, request):
        user_data = {
            'email': request.data.get('email'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'password': make_password(secrets.token_urlsafe(8)),
            'role': Roles.convert_to_int_if_string(request.data.get('role'))
        }

        serializer = UserSerializer(data=user_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_data = serializer.validated_data

        # TODO: alterar função para retornar erro ao invés de lançar exceção
        duplicated_email_validation(user_data["email"])

        user = User.objects.create_user(**user_data)
        user.set_password(user_data["password"])
        user.save()

        user_serialized = UserSerializer(user)

        send_password_in_email(user_data["email"], user_data["password"])

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
        
        successful_count = 0
        failed_count = 0
        errors = []

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
                failed_count += 1
                errors.append({"line": index + 1, "error": serializer.errors})
                continue

            try:
                duplicated_email_validation(user_data["email"])
                user = User.objects.create_user(**user_data)
                user.set_password(user_data["password"])
                user.save()

                send_password_in_email(user_data["email"], user_data["password"])

                successful_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({"line": index + 1, "error": str(e)})

        return Response({
            "successful_count": successful_count,
            "failed_count": failed_count,
            "errors": errors,
            "total_lines": len(df)
        }, status=status.HTTP_200_OK)