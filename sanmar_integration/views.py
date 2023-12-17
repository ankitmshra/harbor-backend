import ftplib
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MyModelSerializer


class GetFileFromFTP(APIView):
    def get(self, request, *args, **kwargs):
        ftp_host = settings.SANMAR_FTP_HOST
        ftp_user = settings.SANMAR_FTP_USER
        ftp_password = settings.SANMAR_FTP_PASSWORD
        ftp_file_path = settings.FTP_FILE_PATH

        try:
            # Connect to FTP server
            with ftplib.FTP(ftp_host, ftp_user, ftp_password) as ftp:
                # Download file
                with open('local_file.txt', 'wb') as local_file:
                    ftp.retrbinary(f'RETR {ftp_file_path}', local_file.write)

            # Create a response using the serialized data and status
            serializer = MyModelSerializer(data={'name': 'Example Name', 'description': 'Example Description'})
            serializer.is_valid(raise_exception=True)
            serialized_data = serializer.data

            response_data = {
                'status': 'success',
                'message': 'File downloaded successfully.',
                'data': serialized_data,
            }

            return JsonResponse(response_data)

        except Exception as e:
            response_data = {
                'status': 'error',
                'error': str(e),
            }
            return JsonResponse(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)