from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import Inventory, Order, Product, OrderProduct
from .serializers import (
    InventorySerializer,
    UpdateInventorySerializer,
    ProductSerializer,
    OrderProductSerializer,
    OrderProductPurchaseSerializer
)

class ProductApiView(APIView):

    @swagger_auto_schema(
            operation_id='Get all Products',
    )
    def get(self, request, *args, **kwargs):

        products = Inventory.objects.all()
        
        serializer = InventorySerializer(products, many=True)

        return Response(serializer.data , status=status.HTTP_200_OK)
    

    @swagger_auto_schema(
            request_body=InventorySerializer(many=True), 
            operation_id='Create a Product',
            responses={201: InventorySerializer(many=True)}
    )
    def post(self, request, *args, **kwargs):

        serializer = InventorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryApiView(APIView):
    
    @swagger_auto_schema(
            request_body=UpdateInventorySerializer(many=True), 
            operation_id='Update stock of product',
            responses={200: 'Stock of product update successfully'}
    )
    def patch(self, request, product_id):

        serializer = UpdateInventorySerializer(data=request.data)

        if serializer.is_valid():

            try:
                inventory = Inventory.objects.get(product_id = product_id)
            except Inventory.DoesNotExist:
                return Response({'error': 'Inventory of product not found'}, status=status.HTTP_404_NOT_FOUND)
        
            inventory.stock += serializer.data['stock']
            inventory.save()
            return Response({'message': 'Stock of product update successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrdersApiView(APIView):
    
    @swagger_auto_schema(
            request_body=OrderProductPurchaseSerializer(many=True), 
            operation_id='Create a Order products',
            responses={201: OrderProductSerializer(many=True)}
    )
    def post(self, request, *args, **kwargs):

        # This endpoint create a new purchase order and
        # Discount all products stock inventory

        serializer = OrderProductPurchaseSerializer(data=request.data)

        if serializer.is_valid():

            products = serializer.validated_data['products']

            # create order number
            order =  Order.objects.create()

            for product in products:
                
                # is discounted for each product purchased

                inventory = Inventory.objects.get(product_id=product['product_id'])
                inventory.stock -= product['total_products']
                inventory.save()

                # Add products to OrderProducts

                order_product  = OrderProduct.objects.create(
                    product = inventory.product,
                    order = order
                )

                order_product.save()

            order_products =  OrderProduct.objects.filter(order_id = order.id)

            serializer = OrderProductSerializer(order_products, many=True)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
