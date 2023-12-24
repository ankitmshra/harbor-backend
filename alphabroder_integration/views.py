import os
from datetime import datetime
from ftplib import FTP_TLS
import ssl
import shutil
from decimal import Decimal

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
import pandas as pd


# import models
from .models import Category, Products, Inventory, Style, Price

# import serializers
from .serializers import AlphaBroderStyleSerializer, AlphaBroderCategorySerializer, AlphaBroderStyleWithProductsSerializer


class Process_alp_inventory(viewsets.ModelViewSet):
    _skip_existing = True

    # AB connection info
    ftp_host = 'ftp.appareldownload.com'
    ftp_user = settings.AB_FTP_USER
    ftp_password = settings.AB_FTP_PASSWORD

    # AB Product files
    product_file = 'AllDBInfoALP_Prod.txt'
    inventory_file = 'inventory-v5-alp.txt'
    price_file = 'AllDBInfoALP_PRC_RZ99.txt'

    def __init__(self, download=True, debug=True, suffix=None,
                 basename=None, detail=None):
        """Initialize inventory by parsing provided inventory
          CSV file and building a dict of all inventory items."""
        self._db = None
        self._download = download
        self._debug = debug
        self._suffix = suffix
        self._basename = basename
        self._detail = detail
        self._current_products = {}
        self._product_images = {}

    #####################################################
    #                       Commons                     #
    #####################################################
        
    def ensure_directory(self, directory):
        """Ensure that the given directory exists."""
        if not os.path.exists(directory):
            os.makedirs(directory)

    def download_file(self, ftp, filename, dir=''):
        """Download given file from global FTP server."""
        download_to = os.path.join('files', 'alpb', filename)
        self.debug("Downloading '{}' to: {}".format(filename, download_to))

        local_file = open(download_to, 'wb')
        ftp.retrbinary(f'RETR {dir}{filename}', local_file.write)
        local_file.close()

    def download_alpha(self, filename):
        """Download the given file."""
        host = self.ftp_host
        user = self.ftp_user
        passwd = self.ftp_password

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.set_ciphers("DEFAULT")

        ftp = FTP_TLS(host=host, context=ssl_context, timeout=10)
        ftp.set_debuglevel(2)
        ftp.set_pasv(True)

        ftp.login(user=user, passwd=passwd)
        ftp.prot_p()  # Explicit FTP over TLS

        self.ensure_directory('files/alpb')  # Ensure 'files' directory exists
        self.download_file(ftp, filename)

        ftp.quit()
        
    def clean_directory(self, directory):
        """Clean the given directory by removing all files."""
        self.debug(f"Cleaning directory: {directory}")
        try:
            shutil.rmtree(directory)
            os.makedirs(directory)
            self.debug(f"Directory cleaned successfully.")
        except Exception as e:
            self.debug(f"Error cleaning directory: {e}")
    
    def debug(self, msg, force=False):
        """Method for printing debug messages."""
        if self._debug or force:
            print("<{}>: {}".
                  format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
            
    #####################################################
    #     Download Inventory, products, Price file      #
    #####################################################
        
    def prepare_products(self):
        """Prepare for updating products by downloading relevant files."""
        self.download_alpha(self.product_file)

    def prepare_inventory(self):
        """Prepare for updating product inventory by downloading relevant
          files."""
        self.download_alpha(self.inventory_file)

    def prepare_pricing(self):
        """Prepare for updating product pricing by downloading relevant
          files."""
        self.download_alpha(self.price_file)

    #####################################################
    #                   Update Products                 #
    #####################################################
    def update_products(self, filename):
        """Read product details from the text file and
          save them to the model."""
        file_path = os.path.join('files', 'alpb', filename)

        if not os.path.isfile(file_path):
            self.debug(f"File {filename} not found.")
            return

        self.debug(f"Updating products from file: {filename}")

        # Read the file using pandas
        df = pd.read_csv(file_path, sep='^', encoding='ISO-8859-1', error_bad_lines=False)

        # Iterate over rows and save to the model
        for _, row in df.iterrows():
            try:
                category, created = Category.objects.get_or_create(category=row['Category'])

                # Create or get Style
                style, created = Style.objects.get_or_create(
                    style_number=row['Style'],
                    defaults={
                        'short_description': row['Short Description'],
                        'mill_number': row['Mill #'],
                        'mill_name': row['Mill Name'],
                        'category': category,
                        'markup_code': row['Markup Code'],
                        'full_feature_description': row['Full Feature Description'],
                    }
                )

                # Create Product
                product_details = {
                    'is_new': row['NEW'] == 'NEW',
                    'item_number': row['Item Number'],
                    'style_number': style,
                    'color_name': row['Color Name'],
                    'color_group_code': row['Color Group Code'],
                    'color_code': row['Color Code'],
                    'hex_code': row['Hex Code'],
                    'size_group': row['Size Group'],
                    'size_code': row['Size Code'],
                    'size': row['Size'],
                    'case_qty': row['Case Qty'],
                    'weight': row['Weight'],
                    'front_image': row['Front of Image Name'],
                    'back_image': row['Back of Image Name'],
                    'side_image': row['Side of Image Name'],
                    'gtin': row['Gtin'],
                    'launch_date': row['Launch Date'],
                    'pms_color': row['PMS Color'],
                    'size_sort_order': row['Size Sort Order'],
                    'mktg_color_number': row['Mktg Color Number'],
                    'mktg_color_name': row['Mktg Color Name'],
                    'mktg_color_hex_code': row['Mktg Color Hex Code'],
                }
                # Use get_or_create for Products
                product, created = Products.objects.get_or_create(item_number=row['Item Number'], defaults=product_details)

                if not created and not self._skip_existing:
                    Products.objects.filter(item_number=row['Item Number']).update(**product_details)
                    self.debug(f"Updated existing product with Item Number: {row['Item Number']}")
                elif not created:
                    self.debug(f"Skipped existing product with Item Number: {row['Item Number']}")
                else:
                    self.debug(f"Created new product with Item Number: {row['Item Number']}")

            except Exception as e:
                self.debug(f"Error processing row: {row}")
                self.debug(f"Error details: {e}")

                
    #####################################################
    #                  Update Inventory                 #
    #####################################################
    def update_inventory(self, filename):
        file_path = os.path.join('files', 'alpb', filename)

        if not os.path.isfile(file_path):
            self.debug(f"File {filename} not found.")
            return

        self.debug(f"Updating inventory from file: {filename}")

        # Read the file using pandas
        df = pd.read_csv(file_path, delimiter=',', encoding='ISO-8859-1', error_bad_lines=False)

        for _, row in df.iterrows():
            # check if the item number and gtin number are not empty. and same
            item_number = row['Item Number']
            gtin_number = row['GTIN Number']

            # Check if the item number is in the product list
            try:
                product = Products.objects.get(item_number=item_number, gtin=gtin_number)
            except Products.DoesNotExist:
                self.debug(f"Product not found for Item Number: {item_number} and GTIN Number: {gtin_number}")
                continue  # Skip to the next iteration if the product doesn't exist

            product_details = {
                'gtin_number': gtin_number,
                'mill_style_number': row['Mill Style Number'],
                'cc': row['CC'],
                'cn': row['CN'],
                'fo': row['FO'],
                'gd': row['GD'],
                'kc': row['KC'],
                'ma': row['MA'],
                'ph': row['PH'],
                'td': row['TD'],
                'pz': row['PZ'],
                'bz': row['BZ'],
                'fz': row['FZ'],
                'px': row['PX'],
                'fx': row['FX'],
                'bx': row['BX'],
                'gx': row['GX'],
                'drop_ship': row['DROP SHIP'] if not pd.isna(row['DROP SHIP']) else 0,
            }

            # Update or create the inventory details using the related product instance
            Inventory.objects.update_or_create(item_number=product, defaults=product_details)

            self.debug(f"Updated inventory details for Item Number: {item_number} and GTIN Number: {gtin_number}")

    #####################################################
    #                   Update Pricing                  #
    #####################################################
    def update_pricing(self, filename):
        file_path = os.path.join('files', 'alpb', filename)

        if not os.path.isfile(file_path):
            self.debug(f"File {filename} not found.")
            return

        self.debug(f"Updating Pricing from file: {filename}")

        # Read the file using pandas
        df = pd.read_csv(file_path, sep='^', encoding='ISO-8859-1', error_bad_lines=False)

        # Iterate over rows and save to the model
        for _, row in df.iterrows():
            # check if the item number and gtin number are not empty. and same
            item_number = row['Item Number ']
            gtin_number = row['Gtin']

            # Check if the item number is in the product list
            try:
                product = Products.objects.get(item_number=item_number, gtin=gtin_number)
            except Products.DoesNotExist:
                self.debug(f"Product not found for Item Number: {item_number} and GTIN Number: {gtin_number}")
                continue  # Skip to the next iteration if the product doesn't exist

            def clean_numeric(value):
                if pd.isna(value) or value == '“nan”':
                    return None
                numeric_value = ''.join(char for char in str(value) if char.isdigit() or char == '.')
                # Convert the cleaned numeric value to a Decimal
                return Decimal(numeric_value) if numeric_value else None

            price_details = {
                'gtin_number': gtin_number,
                'price_per_piece': clean_numeric(row['Piece']),
                'price_per_dozen': clean_numeric(row['Dozen']),
                'price_per_case': clean_numeric(row['Case']),
                'retail_price': clean_numeric(row['Retail']),
            }

            # Update the product details
            Price.objects.update_or_create(item_number=product, defaults=price_details)
            self.debug(f"Updated Pricing details for Item Number: {item_number} and GTIN Number: {gtin_number}")
                             
                
    #####################################################
    #                   Update Handler                  #
    #####################################################
    def handle(self):
        """Handle GET requests to start downloading, processing,
          and updating the model."""
        self.clean_directory(os.path.join('files', 'alpb'))
        self.prepare_products()
        self.update_products(self.product_file)
        self.prepare_inventory()
        self.update_inventory(self.inventory_file)
        self.prepare_pricing()
        self.update_pricing(self.price_file)
        self.debug("Finished updating products and inventory and Pricing.")


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
class UpdateDataView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            process_alp_inventory = Process_alp_inventory()
            process_alp_inventory.handle()
            return Response({"message": "Data updated successfully."},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class StyleListView(ListAPIView):
    serializer_class = AlphaBroderStyleSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        category_param = self.request.query_params.get('category', None)

        if category_param:
            if not Category.objects.filter(category__iexact=category_param).exists():
                raise Http404("Category does not exist")

            # Filter styles by category
            styles = Style.objects.filter(category__category__iexact=category_param)
        else:
            styles = Style.objects.all()

        return styles

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
    serializer_class = AlphaBroderCategorySerializer
    pagination_class = StandardResultsSetPagination


class StyleWithProductsView(RetrieveAPIView):
    queryset = Style.objects.all()
    serializer_class = AlphaBroderStyleWithProductsSerializer
    lookup_field = 'style_number'  # Use 'style_number' as the lookup field

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['style_number'] = self.kwargs['style_number']
        return context

    def get_object(self):
        style_number = self.kwargs['style_number']
        return Style.objects.get(style_number=style_number)
