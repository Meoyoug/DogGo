import os
from datetime import datetime, timedelta
from urllib.request import urlopen

import requests
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.core.files import File
from django.core.mail import EmailMessage
from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from common.utils import S3ImgUploader
from users import serializers
from users.models import User


class Signup(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=serializers.UserSignUpSerializer,
        responses=serializers.UserSignUpSerializer,
        description="회원 가입시 입력한 데이터를 검증하고 검증이 되면 유저에 대한 정보를 데이터 베이스에 저장함.",
    )
    def post(self, request: Request) -> Response:
        user_data = request.data
        profile_image = request.FILES.get("profile_image")
        if profile_image:
            user_data["profile_image"] = profile_image
        serializer = serializers.UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "회원가입 성공"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendVerificationCodeView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=serializers.EmailSerializer,
        description="유저가 회원가입시 이메일을 입력하면 인증을 진행해야하는데, 입력한 이메일을 검증 후에 인증에 쓰일 코드를 이메일로 보내줌.",
    )
    def post(self, request: Request) -> Response:
        serializer = serializers.EmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data.get("email")
        verification_code = get_random_string(length=6)
        message = f"""
            안녕하세요. DogGo 회원가입 시 이메일 인증 코드로 입력해야 할 인증 코드는 아래와 같습니다.
             {verification_code}
            인증 코드 란에 입력 후 인증하기 버튼을 눌러 주신 후 인증이 완료되면 남은 정보를 입력하고 회원가입을 마쳐 주세요.
            감사합니다.
            """
        email_message = EmailMessage(
            subject="Verification Code For DogGo Account Register",
            body=message,
            to=[email],
        )
        email_message.send()  # 이메일 전송
        cache.set(f"{email}-verify_code", verification_code, timeout=300)
        return Response({"msg": "verification code has been sent to email."}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=serializers.ForgotPasswordSerializer,
        description="비밀번호 찾기 시 입력한 아이디와 이메일을 검증하고 이메일로 인증코드를 보내도록 함.",
    )
    def post(self, request: Request) -> Response:
        serializer = serializers.ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            user_id = serializer.validated_data.get("user_id")
            verification_code = get_random_string(length=6)
            message = f"""
                        안녕하세요. DogGo의 계정 {user_id}의 비밀번호 찾기 시 인증 코드로 입력해야 할 인증 코드는 아래와 같습니다.
                         {verification_code}
                        인증 코드 란에 입력 후 인증하기 버튼을 눌러 주신 후 인증이 완료되면 새로운 비밀번호를 입력하고 완료해주세요.
                        감사합니다.
                        """
            email_message = EmailMessage(
                subject="Verification Code For DogGo Account ForgotPassword",
                body=message,
                to=[email],
            )
            email_message.send()  # 이메일 전송
            cache.set(f"{user_id}-{email}-verify_code", verification_code, timeout=180)
            return Response({"msg": "verification code has been sent to email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=serializers.VerificationCodeSerializer,
        description="회원가입 또는 비밀번호 찾기에서 이메일 인증 시 이메일과 인증 코드를 확인하여 인증여부를 응답으로 보내줌.",
    )
    def post(self, request: Request) -> Response:
        serializer = serializers.VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"msg": "Email Veryfied Successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JWTLoginView(TokenObtainPairView):
    def post(self, request: Request) -> Response:
        """
        유저가 입력한 아이디와 비밀번호를 검증하고 유저정보를 인식하는데 쓰일 토큰을 발급해줌.
        """
        try:
            user = authenticate(
                request=request, user_id=request.data.get("user_id"), password=request.data.get("password")
            )
            if user is not None:
                user.last_login = timezone.now()
                user.save()
                response = super().post(request)
                refresh_token = response.data["refresh"]
                # 응답의 바디에 토큰값이 안들어가도록 객체에서 삭제.
                del response.data["refresh"]
                # jwt 토큰을 쿠키에 저장하도록함
                # access token 은 30분 단위로 만료되도록함
                # refresh token 은 하루 단위로 만료되도록함
                response.set_cookie(
                    "AUT_REF",
                    refresh_token,
                    samesite=None,
                    secure=False,
                    httponly=False,
                    expires=datetime.now() + timedelta(days=1),
                )

                response.status_code = status.HTTP_200_OK
                return response
            else:
                return Response(
                    {"msg": "유저 아이디 또는 비밀번호가 올바르지 않습니다."}, status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            return Response({"msg": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JWTLogoutView(APIView):
    def post(self, request: Request) -> Response:
        """
        토큰을 보유한 유저의 로그아웃을 진행함.
        """
        # if request.data.get("login_type") == "kakao":
        #     CLIENT_ID = os.environ.get("CLIENT_ID")
        #     REDIRECT_URI = str(os.environ.get("REDIRECT_URI")) + "/logout"
        #     logout_response = requests.get(
        #         f"https://kauth.kakao.com/oauth/logout?client_id=${CLIENT_ID}&logout_redirect_uri=${REDIRECT_URI}"
        #     )
        #     if logout_response.status_code not in [status.HTTP_302_FOUND, status.HTTP_200_OK]:
        #         return Response({"msg": "카카오 로그아웃 요청 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            response = Response({"msg": "로그아웃 성공"}, status=status.HTTP_200_OK)
            # 응답으로 로그인한 사용자의 쿠키에서 토큰을 제거하는 설정
            response.delete_cookie("AUT_REF")
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JWTRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """
        엑세스 토큰이 만료되고 리프레쉬 토큰이 유효한 유저에게 액세스 토큰을 다시 발급해줌.
        """
        refresh_token = request.COOKIES.get("AUT_REF")

        if refresh_token is None:
            return Response({"msg": "required refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh_token_validate = RefreshToken(refresh_token)  # type: ignore
            access_token = str(refresh_token_validate.access_token)
            return Response({"access": access_token}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"msg": "Plz Login again"}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            # 예상치 못한 다른 예외 처리
            return Response({"msg": "an unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=serializers.UserInfoSerializer,
        responses=serializers.UserInfoSerializer,
        description="유저의 내정보 가져오기 기능",
    )
    def get(self, request: Request) -> Response:
        user = User.objects.get(id=request.user.id)  # type: ignore
        if user:
            serializer = serializers.UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=serializers.UserInfoModifySerializer,
        responses=serializers.UserInfoModifySerializer,
        description="유저가 입력한 정보를 바탕으로 유저의 정보를 업데이트 해줌",
    )
    def put(self, request: Request) -> Response:
        update_data = request.data
        update_image = request.FILES.get("profile_image")
        if update_image:
            update_data["profile_image"] = update_image
        serializer = serializers.UserInfoModifySerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if update_image:
            user = User.objects.get(id=request.user.id)  # type: ignore
            prev_image_url = user.profile_image
            if prev_image_url:
                image_uploader = S3ImgUploader()
                try:
                    image_uploader.delete_img_file(str(prev_image_url))
                except Exception as e:
                    return Response({"msg": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(description="회원탈퇴 요청을 처리하는 뷰, 데이터를 바로지우지않고 상태를 변경함.")
    def delete(self, request: Request) -> Response:
        # 회원탈퇴 요청이 들어오면 상태를 False로 바꿔 탈퇴예정임을 나타내고
        # del_req_time 을 요청이 들어온 현재시간으로 세팅한다.
        # 이후 장고의 Cron을 이용하여 매일 정각에 삭제요청 후 시점이 6개월이 지난 데이터들을 삭제할 예정
        # 필드가 수정되고나면 로그아웃을 시킴
        try:
            user = request.user
            user.is_active = False
            user.del_req_time = timezone.now()  # type: ignore
            user.save()

            # 로그아웃
            response = Response(status=status.HTTP_200_OK)
            response.delete_cookie("AUT_REF")
            return response
        except Exception as e:
            return Response({"msg": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class KakaoLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request: Request) -> Response:
        code = request.data.get("code")  # 프론트에서 보내준 코드
        # 카카오 oauth 토큰 발급 url로 code가 담긴 post 요청을 보내 응답을 받는다.
        CLIENT_ID = os.environ.get("CLIENT_ID")
        REDIRECT_URI = os.environ.get("REDIRECT_URI")
        token_response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": f"{REDIRECT_URI}/login",
                "client_id": CLIENT_ID,
            },
        )
        if token_response.status_code != status.HTTP_200_OK:
            return Response(
                {"msg": "카카오 서버로 부터 토큰을 받아오는데 실패하였습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        # 응답으로부터 액세스 토큰을 가져온다.
        access_token = token_response.json().get("access_token")
        response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
            },
        )

        if response.status_code != status.HTTP_200_OK:
            return Response(
                {"msg": "카카오 서버로 부터 프로필 데이터를 받아오는데 실패하였습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        """
        1. 문제: 에러가 발생시 json데이터가 안올 수 있는데, 무조건 json()을 호출하면 시리얼라이저 에러가 발생할 가능성이 높다.
        2. 해결방법: 응답 받고 status_code를 확인한 후에 json() 호출, 500 or 400코드가 발생시 raise exception으로 탈출?
        """
        user_data_json = response.json()
        kakao_account = user_data_json["kakao_account"]
        profile = kakao_account.get("profile")
        requests.post("https://kapi.kakao.com/v1/user/logout", headers={"Authorization": f"Bearer {access_token}"})
        try:
            user = User.objects.get(email=kakao_account.get("email"))
            refresh_token = RefreshToken.for_user(user)
            response = Response(
                {
                    "access": str(refresh_token.access_token),  # type: ignore
                    "user_data": serializers.UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
            response.set_cookie(  # type: ignore
                "AUT_REF",
                str(refresh_token),
                samesite=None,
                secure=False,
                httponly=False,
                expires=datetime.now() + timedelta(days=1),
            )
            return response  # type: ignore
        except User.DoesNotExist:
            # 이미지를 다운로드하여 파일 객체로 가져옴
            image_response = urlopen(profile.get("profile_image_url"))
            kakao_profile_image = File(image_response)
            user = User.objects.create(
                user_id="oauth" + get_random_string(8),
                email=kakao_account.get("email"),
                nickname=profile.get("nickname"),
                profile_image=kakao_profile_image,
            )
            user.set_unusable_password()
            refresh_token = RefreshToken.for_user(user)
            response = Response(
                {
                    "access": str(refresh_token.access_token),  # type: ignore
                    "user_data": serializers.UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
            response.set_cookie(  # type: ignore
                "AUT_REF",
                str(refresh_token),
                samesite=None,
                secure=False,
                httponly=False,
                expires=datetime.now() + timedelta(days=1),
            )
            return response  # type: ignore
        except Exception as e:
            return Response({"msg": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
