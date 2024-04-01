from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer


class ProductList(APIView):
    def get(self, request):
        product = Product.objects.all()

        serializer = ProductSerializer(product, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetail(APIView):
    def get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get(self, request, product_id):
        product = self.get_object(product_id)
        if product is not None:
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        else:
            return Response({"error": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, product_id):
        product = self.get_object(product_id)
        if product is not None:
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, product_id):
        product = self.get_object(product_id)
        if product is not None:
            product.delete()
            return Response({"message": "상품이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)