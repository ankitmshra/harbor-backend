import os
from datetime import datetime
from ftplib import FTP_TLS
import ssl

from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
import pandas as pd


# import models
from .models import AlphaBroderProducts
from .serializers import AlphaBroderProductsSerializer


class Process_alp_inventory(viewsets.ModelViewSet):

    _inventory = {}
    _prices = None
    _colors = {}
    _sizes = {}
    _images = {}
    _shopify_ids = {}
    _product_ids = {}
    _color_groups = ["", "Basic Colors", "Traditional Colors",
                     "Extended Colors", "Extended Colors 2",
                     "Extended Colors 3", "Extended Colors 4",
                     "Extended Colors 5", "Extended Colors 6",
                     "Extended Colors 7", "Extended Colors 8",
                     "Extended Colors 9", "Extended Colors 10"]
    _progress = []
    _save = False
    _skip_existing = True

    # AB connection info
    ftp_host = 'ftp.appareldownload.com'
    ftp_user = settings.AB_FTP_USER
    ftp_password = settings.AB_FTP_PASSWORD

    # AB Product files
    product_file = 'AllDBDiscoALP_4.txt'
    inventory_file = 'inventory-v5-alp.txt'

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
        self._styles_to_fix = []
        self._categories = ['Polos', 'Outerwear', 'Fleece',
                            'Sweatshirts', 'Woven Shirts',
                            'T-Shirts', 'Headwear', 'Bags']
        
    #####################################################
    #       Download Inventory and products file        #
    #####################################################
        
    def ensure_directory(self, directory):
        """Ensure that the given directory exists."""
        if not os.path.exists(directory):
            os.makedirs(directory)

    def download_file(self, ftp, filename, dir=''):
        """Download given file from global FTP server."""

        download_to = os.path.join('staticfiles/alpb', filename)
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

        ftp = FTP_TLS(host=host, context=ssl_context)
        ftp.set_debuglevel(2)
        ftp.set_pasv(True)

        ftp.login(user=user, passwd=passwd)
        ftp.prot_p()  # Explicit FTP over TLS

        self.ensure_directory('staticfiles/alpb')  # Ensure 'files' directory exists
        self.download_file(ftp, filename)

        ftp.quit()

    def clean(self):
        """Remove all downloaded files."""
        folder = 'images'
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

        if self._download:
            for f in [self.inventory_file, self.product_file]:
                if os.path.isfile(os.path.join('staticfiles/alpb', f)):
                    os.unlink(os.path.join('files', f))

    def prepare_products(self):
        """Prepare for updating products by downloading relevant files."""
        self.download_alpha(self.product_file)

    def prepare_inventory(self):
        """Prepare for updating product inventory by downloading relevant
          files."""
        self.download_alpha(self.inventory_file)

    #####################################################
    #                       Commons                     #
    #####################################################
    
    def debug(self, msg, force=False):
        """Method for printing debug messages."""
        if self._debug or force:
            print("<{}>: {}".
                  format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))

    #####################################################
    #                   Update Products                 #
    #####################################################
    def update_products(self, filename):
        """Read product details from the text file and
          save them to the model."""
        file_path = os.path.join('files', filename)

        if not os.path.isfile(file_path):
            self.debug(f"File {filename} not found.")
            return

        self.debug(f"Updating products from file: {filename}")

        # Read the file using pandas
        df = pd.read_csv(file_path, delimiter='^', encoding='ISO-8859-1',
                         error_bad_lines=False)
        
        columns_to_remove = [20, 45]
        df = df.drop(df.columns[columns_to_remove], axis=1)

        # Iterate over rows and save to the model
        for _, row in df.iterrows():
            product_details = {field.lower().replace(" ", "_").
                               replace('#', 'number'):
                               row[field] for field in df.columns}

            # Convert date strings to datetime objects
            date_fields = ['start_date', 'end_date']
            for field in date_fields:
                product_details[field] = datetime.strptime(
                    product_details[field], '%m/%d/%y')

            # Check if the product already exists
            existing_product = AlphaBroderProducts.objects.filter(
                sku=product_details['sku']).first()

            # Update or create the product
            if existing_product:
                if not self._skip_existing:
                    for key, value in product_details.items():
                        setattr(existing_product, key, value)
                    existing_product.save()
                    self.debug(f"Updated existing product with SKU: \
                               {product_details['sku']}")
                else:
                    self.debug(f"Skipped existing product with SKU: \
                               {product_details['sku']}")
            else:
                new_product = AlphaBroderProducts(**product_details)
                new_product.save()
                self.debug(f"Created new product with SKU: \
                           {product_details['sku']}")
                
    #####################################################
    #                  Update Inventory                 #
    #####################################################
    def update_inventory(self, filename):
        """Read product details from the text file and
          save them to the model."""
        file_path = os.path.join('files', filename)

        if not os.path.isfile(file_path):
            self.debug(f"File {filename} not found.")
            return

        self.debug(f"Updating inventory from file: {filename}")

        # Read the file using pandas
        df = pd.read_csv(file_path, delimiter='^', encoding='ISO-8859-1',
                         error_bad_lines=False)

        # Iterate over rows and save to the model
        for _, row in df.iterrows():
            product_details = {field.lower().replace(" ", "_").
                               replace('#', 'number'):
                               row[field] for field in df.columns}

            # Check if the product already exists
            existing_product = AlphaBroderProducts.objects.filter(
                sku=product_details['item_number']).first()

            # Update or create the product
            if existing_product:
                if not self._skip_existing:
                    for key, value in product_details.items():
                        setattr(existing_product, key, value)
                    existing_product.save()
                    self.debug(f"Updated existing product with SKU: \
                               {product_details['item_number']}")
                else:
                    self.debug(f"Skipped existing product with SKU: \
                               {product_details['item_number']}")
            else:
                new_product = AlphaBroderProducts(**product_details)
                new_product.save()
                self.debug(f"Created new product with SKU: \
                           {product_details['item_number']}")
                
    #####################################################
    #                   API Controllers                 #
    #####################################################

    def handle(self):
        """Handle GET requests to start downloading, processing,
          and updating the model."""
        # Download and process products
        # Download and process inventory
        self.prepare_inventory()
        self.update_inventory(self.inventory_file)

        # self.clean()
        self.prepare_products()
        self.update_products(self.product_file)


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


class GetALPProductsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            products = AlphaBroderProducts.objects.all()
            serializer = AlphaBroderProductsSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
