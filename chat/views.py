from chat.serializers import UserRegSerializer, LoginSerializer
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status,generics
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


# Create your views here.




class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        print()
        serializer = UserRegSerializer(data=request.POST.dict())
        print("Request data:", request.data)
        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Возвращаем токены в ответе
            return Response({
                'access': access_token,
                'refresh': refresh_token
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class userLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

class CheckTokenView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        return Response({"message":"Token is valid"})



def redirect_auth(request):
    return redirect('login')


def login_page(request):
    return render(request,'chat/login_page.html')
def signup_page(request):
    return render(request,'chat/signup_page.html')
def main_page(request):
    return render(request,'chat/main_page.html')

