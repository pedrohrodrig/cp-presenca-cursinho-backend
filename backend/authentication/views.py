import secrets

import pandas as pd
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from attendance.models import Student

from .filters import UserFilter
from .models import Roles, User
from .serializers import UserBasicInfoSerializer, UserSerializer
from .validators import duplicated_email_validation, student_class_exists_validation


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserBasicInfoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def register(self, request):
        try:
            user_role = Roles.convert_to_int_if_string(request.data.get("role"))

            user_data = {
                "email": request.data.get("email"),
                "first_name": request.data.get("first_name"),
                "last_name": request.data.get("last_name"),
                "password": make_password(secrets.token_urlsafe(8)),
                "role": user_role,
            }

            serializer = UserSerializer(data=user_data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user_data = serializer.validated_data

            if user_role == Roles.STUDENT:
                student_class = student_class_exists_validation(request.data.get("student_class"))

            # TODO: alterar função para retornar erro ao invés de lançar exceção
            duplicated_email_validation(user_data["email"])

            with transaction.atomic():
                user = User.objects.create_user(**user_data)

                if user_role == Roles.STUDENT:
                    Student.objects.create(user=user, student_class=student_class)

                user.set_password(user_data["password"])
                user.save()

            user_serialized = UserSerializer(user)

            reset_password_token = ResetPasswordToken.objects.create(user=user)
            reset_password_token_created.send(
                sender=self.__class__, reset_password_token=reset_password_token, register=True
            )

            return Response(user_serialized.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def set_profile_photo(self, request, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        print(request.FILES)
        profile_image = request.FILES.get("profile_image")

        if profile_image:
            user.profile_photo = profile_image
            user.save()
            return Response({"message": "Image uploaded successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve_self(self, request):
        user = User.objects.filter(id=request.user.id).first()
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


class RegisterMultipleView(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)

    def register_multiple(self, request, *args, **kwargs):
        file = request.FILES["file"]
        if not file.name.endswith(".xlsx"):
            return Response(
                {"error": "Invalid file format. Please upload an Excel file."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        successful_count = 0
        failed_count = 0
        errors = []

        for index, row in df.iterrows():
            user_role = user_role = Roles.convert_to_int_if_string(row["role"])

            user_data = {
                "email": row["email"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "password": make_password(secrets.token_urlsafe(8)),
                "role": user_role,
            }
            serializer = UserSerializer(data=user_data)

            if not serializer.is_valid():
                failed_count += 1
                errors.append({"line": index + 1, "error": serializer.errors})
                continue

            try:
                if user_role == Roles.STUDENT:
                    student_class = student_class_exists_validation(row["student_class"])

                duplicated_email_validation(user_data["email"])

                with transaction.atomic():
                    user = User.objects.create_user(**user_data)

                    if user_role == Roles.STUDENT:
                        Student.objects.create(user=user, student_class=student_class)

                    user.set_password(user_data["password"])
                    user.save()

                reset_password_token = ResetPasswordToken.objects.create(user=user)
                reset_password_token_created.send(
                    sender=self.__class__, reset_password_token=reset_password_token, register=True
                )

                successful_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({"line": index + 1, "error": str(e)})

        return Response(
            {
                "successful_count": successful_count,
                "failed_count": failed_count,
                "errors": errors,
                "total_lines": len(df),
            },
            status=status.HTTP_200_OK,
        )
