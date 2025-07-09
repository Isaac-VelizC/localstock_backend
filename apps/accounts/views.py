from .serializers import RegisterUserSerializer, AccountSerializer, AccountUpdateSerializer, UserOnboardingSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework.permissions import IsAuthenticated, AllowAny
from dj_rest_auth.registration.views import SocialLoginView
from apps.stores.models import Plan, Store, GeneralSetting
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Role, EmailVerificationCode, User
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from django.core.mail import send_mail
import random

# Create your views here.
class GetAccountShowView(generics.RetrieveAPIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class SendVerificationCode(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email requerido"}, status=400)
        code = str(random.randint(100000, 999999))
        EmailVerificationCode.objects.create(email=email, code=code)
        subject = "Tu código de verificación"
        message = f"Tu código es: {code}"

        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "Código enviado correctamente"}, status=200)

class VerifyCodeAndRegister(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Email y código son requeridos"}, status=400)

        try:
            entry = EmailVerificationCode.objects.filter(email=email).latest('created_at')
        except EmailVerificationCode.DoesNotExist:
            return Response({"error": "Código no encontrado"}, status=404)

        if entry.is_expired():
            return Response({"error": "Código expirado"}, status=400)

        if entry.code != code:
            return Response({"error": "Código incorrecto"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Este correo ya está registrado."}, status=400)

        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Eliminar todos los códigos del email
            EmailVerificationCode.objects.filter(email=email).delete()

            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Usuario creado y autenticado",
                "user_id": user.id,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=201)
        else:
            print(serializer.errors)
            return Response({
                "message": "Error en los datos",
                "errors": serializer.errors
            }, status=400)
        
class CompleteOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserOnboardingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response({'detail': 'Onboarding completado.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateDataAccount(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        serializer = AccountUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Información actualizado exitosamente."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GoogleLoginCustom(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        # Realiza el login original de dj-rest-auth
        response = super().post(request, *args, **kwargs)
        user = self.user  # Usuario autenticado
        # Si no tiene tienda asignada, crearla
        if not hasattr(user, 'store'):
            plan = Plan.objects.get(name="Básico")  # o un plan por defecto
            store = Store.objects.create(
                name=user.username or user.email.split('@')[0],
                plan=plan,
                rubro=None,
                logo=None,
                phone='',
                address=None,
            )

            GeneralSetting.objects.create(store=store)

            role, _ = Role.objects.get_or_create(name="Administrador")
            user.role = role
            user.store = store
            user.save()

        return response
