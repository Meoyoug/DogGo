from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from coupons.models import Coupon, UserCoupon
from coupons.serializers import CouponSerializer, UserCouponSerializer


class CouponListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        coupons = Coupon.objects.all()
        if coupons:
            serializer = CouponSerializer(coupons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        coupon_data = request.data
        serializer = CouponSerializer(data=coupon_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CouponDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, coupon_id):
        coupon = get_object_or_404(Coupon, id=coupon_id)
        serializer = CouponSerializer(coupon)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, coupon_id):
        coupon = get_object_or_404(Coupon, id=coupon_id)
        modify_data = request.data
        serializer = CouponSerializer(coupon, data=modify_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, coupon_id):
        coupon = get_object_or_404(Coupon, id=coupon_id)
        coupon.delete()
        return Response(status=status.HTTP_200_OK)


class UserCouponListView(APIView):
    def get(self, request):
        # 전체 쿠폰 중에서 사용가능한 순으로, 그 중에서도 유효 기간이 짧은 순으로 내려줌
        coupons = UserCoupon.objects.filter(user_id=request.user.id).order_by("-status", "expired_at")
        if coupons:
            serializer = UserCouponSerializer(coupons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class AvailableUserCouponListView(APIView):
    """
    유저가 보유 중인 쿠폰 중 사용가능한 리스트를 내려주는 View
    """

    def get(self, request):
        # 사용가능한 쿠폰 중에서 유효기간이 짧은것부터 내려줌
        coupons = UserCoupon.objects.filter(user_id=request.user.id, status=True).order_by("expired_at")
        if coupons:
            serializer = UserCouponSerializer(coupons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class UsedUserCouponListView(APIView):
    """
    유저가 사용했던 쿠폰 리스트를 내려주는 View
    """

    def get(self, request):
        # 가장 최근에 사용했던 쿠폰순으로 내려줌
        coupons = UserCoupon.objects.filter(user_id=request.user.id, status=False).order_by("-modified_at")
        if coupons:
            serializer = UserCouponSerializer(coupons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserCouponDetailView(APIView):
    """
    유저가 보유한 쿠폰의 상세정보를 내려줄 메서드
    """

    def get(self, request, user_coupon_id):
        coupon = get_object_or_404(UserCoupon, id=user_coupon_id)
        if coupon.user_id != request.user.id:  # 요청을 보낸 유저가 쿠폰을 소지한 유저가 맞는지 확인
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserCouponSerializer(coupon)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def delete(self, request, user_coupon_id):
    """
    이미 사용한 유저의 쿠폰을 삭제해주는 메서드
    """
    #     coupon = get_object_or_404(UserCoupon, id=user_coupon_id)
    #     if coupon.user_id != request.user.id:  # 요청을 보낸 유저가 쿠폰을 소지한 유저가 맞는지 확인
    #         return Response(status=status.HTTP_401_UNAUTHORIZED)
    #     if not coupon.status:
    #         coupon.delete()
    #         return Response(status=status.HTTP_200_OK)
    #     return Response({"msg": "available coupon."}, status=status.HTTP_400_BAD_REQUEST)


class UserCouponIssueView(APIView):
    """
    쿠폰 발급요청을 처리하는 View
    이미 생성되어있는 쿠폰이 있으면 400 응답과 메시지를 반환,
    없다면 쿠폰의 유효성을 검증하고, 시리얼라이저로 데이터의 유효성 검증 후에 생성.
    시리얼라이저에서 유효성 검증 실패시 400 상태 코드, 시리얼라이저의 error 메시지를 반환.
    생성이 완료되면 응답으로 생성된 쿠폰의 정보와, 201 상태코드 반환.
    """

    serializer_class = UserCouponSerializer

    def post(self, request, coupon_id):
        user_coupon = UserCoupon.objects.filter(coupon_id=coupon_id, user_id=request.user.id, status=True).exists()
        if user_coupon:
            return Response({"msg": "already issued coupon."}, status=status.HTTP_400_BAD_REQUEST)
        coupon = get_object_or_404(Coupon, id=coupon_id)
        expired_date = coupon.get_expire_date()
        serializer = UserCouponSerializer(
            data={
                "user": request.user.id,
                "coupon": coupon_id,
                "expired_at": expired_date,
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
