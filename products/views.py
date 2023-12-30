from django.http import Http404
from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from products.models import Products, Category
from products.serializers import (
    ProductCategoryReadSerializer,
    ProductReadSerializer,
    VerboseProductReadSerializer
)

#####################################################
#                   Helper Classes                  #
#####################################################
# pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


#####################################################
#                   API Controllers                 #
#####################################################
class ProductsListView(ListAPIView):
    serializer_class = ProductReadSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        category_param = self.request.query_params.get('category', None)

        if category_param:
            if not Category.objects.filter(category__iexact=category_param).exists():
                raise Http404("Category does not exist")

            # Filter styles by category
            products = Products.objects.filter(category__category__iexact=category_param)
        else:
            products = Products.objects.all()

        return products

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_404_NOT_FOUND if not queryset.exists() else status.HTTP_200_OK)


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = ProductCategoryReadSerializer
    pagination_class = StandardResultsSetPagination


class VerboseProductsView(RetrieveAPIView):
    queryset = Products.objects.all()
    serializer_class = VerboseProductReadSerializer
    lookup_field = 'product_number'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product_number'] = self.kwargs['product_number']
        return context

    def get_object(self):
        product_number = self.kwargs['product_number']
        return Products.objects.get(product_number=product_number)
