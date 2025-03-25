import json
import pickle
from pathlib import Path
from getpass import getpass

from google.cloud import storage
from google.oauth2 import service_account

from gcp_storage.encrypt import Cipher
from gcp_storage.color import Color
from gcp_storage.logger import get_logger


class GCPCloudStorage():
    def __init__(self, bucket: str = 'default', service_account: str = 'default'):
        self.log = get_logger('gcp-storage')
        self.service_account = service_account
        self.__bucket = bucket
        self.__client: storage.Client | None = None
        self.__cipher: Cipher | None = None

    @property
    def default_sa(self) -> str:
        """Get the default service account file path

        Returns:
            str: default service account file path
        """
        return f'{Path(__file__).parent}/gcp_env/default_sa'

    @property
    def default_bucket(self) -> str:
        return f'{Path(__file__).parent}/gcp_env/default_bucket'

    @property
    def used_buckets_file(self):
        return f'{Path(__file__).parent}/gcp_env/.used_buckets'

    @property
    def sa_file(self) -> str:
        """Get the service account file path. Looks up default service account if 'default' is set

        Returns:
            str: service account file path
        """
        if self.service_account == 'default':
            self.service_account = self.__get_default_service_account()
        return f'{Path(__file__).parent}/gcp_env/.{self.service_account}.sa'

    @property
    def bucket(self) -> str:
        """Get the default bucket name. Looks up default bucker if 'default' is set

        Returns:
            str: service account file path
        """
        if self.__bucket == 'default':
            self.__bucket = self.__get_default_bucket()
        return self.__bucket

    @property
    def cipher(self) -> Cipher:
        """Get the cipher object for encryption/decryption

        Returns:
            Cipher: cipher object
        """
        if self.__cipher is None:
            self.__cipher = Cipher(self.log)
        return self.__cipher

    @property
    def creds(self) -> service_account.Credentials | None:
        """Get the service account credentials object

        Returns:
            service_account.Credentials | None: service account credentials object or None on failure
        """
        try:
            with open(self.sa_file, 'rb') as file:
                __creds: dict = pickle.loads(self.cipher.decrypt(file.read(), self.cipher.load_key()))
            return service_account.Credentials.from_service_account_info(__creds)
        except Exception:
            self.log.exception('Failed to load credentials')
        return None

    @property
    def client(self) -> storage.Client | None:
        """Get the secret manager client object

        Returns:
            storage.Client | None: secret manager client object or None on failure
        """
        if self.__client is None:
            try:
                self.__client = storage.Client(credentials=self.creds)
            except Exception:
                self.log.exception('Failed to load cloud storage client')
        return self.__client

    @staticmethod
    def display_success(msg: str):
        Color().print_message(msg, 'green')

    @staticmethod
    def display_error(msg: str):
        Color().print_message(msg, 'red')

    def _load_json_service_account(self, sa_path: str) -> dict:
        """Load a service account json file to a dictionary

        Args:
            sa_path (str): path to the service account json file

        Returns:
            dict: service account data
        """
        try:
            with open(sa_path, 'r') as sa_file:
                return json.load(sa_file)
        except Exception:
            self.log.exception('Failed to create credentials file')
        return {}

    def _create_service_account_file(self, sa_file: str, sa_data: dict) -> bool:
        """Create a service account file and encrypt it with the cipher key.

        Args:
            sa_file (str): path to the service account file
            sa_data (dict): service account data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(sa_file, 'wb') as file:
                file.write(self.cipher.encrypt(pickle.dumps(sa_data), self.cipher.load_key()))
            return True
        except Exception:
            self.log.exception('Failed to create service account file')
        return False

    def _add_bucket_to_used_buckets(self):
        try:
            with open(self.used_buckets_file, 'r') as file:
                buckets = file.readlines()
            if self.bucket not in buckets:
                with open(self.used_buckets_file, 'a') as file:
                    file.write(f'{self.bucket}\n')
            return True
        except Exception:
            self.log.exception()
        return False

    def _prompt_for_passwd(self, verify: bool = False) -> str:
        """Prompt for a password on console without echoing

        Args:
            verify (bool, optional): True if password needs to be verified. Defaults to False.

        Returns:
            str: password provided
        """
        try:
            passwd = getpass('Enter password: ')
            if not passwd:
                self.log.error('Password cannot be empty')
                return self._prompt_for_passwd(verify)
            if verify:
                passwd_verify = getpass('Verify password: ')
                if passwd != passwd_verify:
                    self.log.error('Passwords do not match')
                    return self._prompt_for_passwd(verify)
            return passwd
        except KeyboardInterrupt:
            self.log.error('Password prompt cancelled')
            exit(1)

    def __get_default_service_account(self) -> str:
        """Get the default service account name

        Returns:
            str: default service account name or empty string if failed
        """
        try:
            with open(self.default_sa, 'r') as file:
                return file.read().strip()
        except Exception:
            self.log.exception('Failed to load default service account')
        return ''

    def __get_default_bucket(self) -> str:
        """Get the default bucket name

        Returns:
            str: default bucket name or empty string if failed
        """
        try:
            with open(self.default_bucket, 'r') as file:
                return file.read().strip()
        except Exception:
            self.log.exception('Failed to load default service account')
        return ''

    def get_blob(self, blob_path: str):
        """Get blob object from bucket

        Args:
            blob_path (str): bucket path to the blob

        Returns:
            storage.Blob: the blob object or None if failed
        """
        try:
            return self.client.get_bucket(self.bucket).blob(blob_path)
        except Exception:
            self.log.exception('Failed to get blob object')
        return None

    def __download_to_file(self, bucket_path: str, destination_path: str):
        """Download file from bucket and save to destination path

        Args:
            bucket_path (str): bucket path to file to download
            destination_path (str): save file to this path

        Returns:
            bool: True if successful, False otherwise
        """
        blob = self.get_blob(bucket_path)
        if blob:
            try:
                blob.download_to_filename(destination_path)
                self.log.debug('Successfully downloaded file')
                return True
            except Exception:
                self.log.exception(f'Failed to download file: {bucket_path}')
        else:
            self.log.error(f'Failed to download file: {bucket_path}')
        return False

    def download_data(self, bucket_path: str, passwd: bool = False) -> str:
        """Download data from bucket

        Args:
            bucket_path (str): bucket path to file to download
            passwd (bool, optional): True if the data is encrypted. Defaults to False.

        Returns:
            str: the downloaded data as string
        """
        if passwd:
        blob = self.get_blob(bucket_path)
        if blob:
            try:
                if passwd:
                data = blob.download_as_bytes()
                if passwd:
                    return self.cipher.passwd_xor(data, self._prompt_for_passwd(False)).decode()
                return data.decode()
            except Exception:
                self.log.exception(f'Failed to download data: {bucket_path}')
        else:
            self.log.error(f'Failed to download data: {bucket_path}')
        return ''

    def __upload_from_raw(self, data: str | bytes, bucket_path: str, content_type: str = 'text/plain'):
        """Upload data to bucket

        Args:
            data (str | bytes): data to upload
            bucket_path (str): the path to save the data in the bucket
            content_type (str, optional): the content type tag. Defaults to 'text/plain'.

        Returns:
            bool: True if successful, False otherwise
        """
        if isinstance(data, bytes) and content_type == 'text/plain':
            content_type = 'application/octet-stream'
        blob = self.get_blob(bucket_path)
        if blob:
            try:
                blob.upload_from_string(data, content_type=content_type)
                self.log.info(f'Successfully uploaded data to {bucket_path}')
                return True
            except Exception:
                self.log.exception(f'Failed to upload data to {bucket_path}')
        else:
            self.log.error(f'Failed to upload data to {bucket_path}')
        return False

    def __upload_from_file(self, file_path: str, bucket_path: str, content_type: str = 'text/plain'):
        """Upload file to bucket

        Args:
            file_path (str): file path to upload
            bucket_path (str): the path to save the file in the bucket
            content_type (str, optional): the content type tag. Defaults to 'text/plain'.

        Returns:
            bool: True if successful, False otherwise
        """
        blob = self.get_blob(bucket_path)
        if blob:
            try:
                blob.upload_from_filename(file_path, content_type=content_type)
                self.log.info(f'Successfully uploaded file {file_path} to {bucket_path}')
                return True
            except Exception:
                self.log.exception(f'Failed to upload file to {bucket_path}')
        else:
            self.log.error(f'Failed to upload file {file_path} to {bucket_path}')
        return False

    def upload_data_as_json(self, data_obj: object, bucket_path: str):
        """Upload data as json to bucket. This will convert the object to json string before uploading then
        set the content type to 'application/json' for the data upload

        Args:
            data_obj (object): python object to convert to json string
            bucket_path (str): path to save the data in the bucket

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data_str: str = json.dumps(data_obj)
        except Exception:
            self.log.exception('Failed to convert data to json')
            return False
        return self.__upload_from_raw(data_str, bucket_path, 'application/json')

    def upload_data(self, data: str, bucket_path: str, passwd: bool = False):
        """Upload data as text to bucket. This will set the content type to 'text/plain' for the data upload

        Args:
            data (str): the string data to save as text file in the bucket
            bucket_path (str): the path to save the data in the bucket
            passwd (bool, optional): True if the data should be encrypted. Defaults to False.

        Returns:
            bool: True if successful, False otherwise
        """
        content_type = 'text/plain'
        if passwd:
            data: bytes = self.cipher.passwd_xor(data.encode(), self._prompt_for_passwd(True))
            content_type = 'application/octet-stream'
        return self.__upload_from_raw(data, bucket_path, content_type)

    def upload_file(self, file_path: str, bucket_path: str, passwd: bool = False):
        """Upload text file to bucket. This will set the content type to 'text/plain' for the data upload

        Args:
            file_path (str): the file path to upload
            bucket_path (str): the path to save the file in the bucket
            passwd (bool, optional): True if the data should be encrypted. Defaults to False.

        Returns:
            bool: True if successful, False otherwise
        """
        if passwd:
            try:
                with open(file_path, 'rb') as file:
                    data = self.cipher.passwd_xor(file.read(), self._prompt_for_passwd(True))
            except Exception:
                self.log.exception('Failed to read file')
                return False
            return self.__upload_from_raw(data, bucket_path, 'application/octet-stream')
        if file_path.endswith('.json'):
            return self.__upload_from_file(file_path, bucket_path, 'application/json')
        return self.__upload_from_file(file_path, bucket_path, 'text/plain')

    def get_bucket_folder_blob_as_generator(self, folder_path: str):
        """Get all files in a folder in the bucket as a generator

        Args:
            folder_path (str): the path to the folder in the bucket

        Returns:
            generator: generator of files in the folder
        """
        try:
            for blob in self.client.get_bucket(self.bucket).list_blobs(prefix=folder_path):
                blob: storage.Blob
                yield blob
        except Exception:
            self.log.exception('Failed to get files')

    def get_bucket_folder_files(self, folder_path: str):
        """Get all files in a folder in the bucket

        Args:
            folder_path (str): the path to the folder in the bucket

        Returns:
            list: list of file names in the folder
        """
        contents = []
        try:
            for blob in self.get_bucket_folder_blob_as_generator(folder_path):
                contents.append(blob.name)
        except Exception:
            self.log.exception('Failed to list files')
        return contents

    def display_bucket_folder_files(self, folder_path: str = ''):
        payload = f'Contents of the {folder_path}:\n'
        try:
            for blob in self.client.get_bucket(self.bucket).list_blobs(prefix=folder_path):
                blob: storage.Blob
                payload += f'  {blob.name}\n'
        except Exception:
            self.log.exception('Failed to get files')
        self.display_success(payload)

    def delete_bucket_folder(self, folder_path: str):
        """Delete all files in a folder in the bucket

        Args:
            folder_path (str): the path to the folder in the bucket

        Returns:
            bool: True if successful, False otherwise
        """
        for blob in self.get_bucket_folder_blob_as_generator(folder_path):
            try:
                blob.delete()
                self.log.info(f'Deleted file: {blob.name}')
            except Exception:
                self.log.exception(f'Failed to delete file: {blob.name}')
                return False
        return True

    def delete_bucket_file(self, bucket_path: str):
        """Delete file from bucket

        Args:
            bucket_path (str): the path to the file in the bucket

        Returns:
            bool: True if successful, False otherwise
        """
        blob = self.get_blob(bucket_path)
        if blob:
            try:
                blob.delete()
                self.log.info('Successfully deleted file')
                return True
            except Exception:
                self.log.exception('Failed to delete file')
        return False

    def get_bucket_file_info(self, file_path: str):
        """Get the info of a file in the bucket. The info includes the file name, size, checksum and created date

        Args:
            file_path (str): the path to the file in the bucket

        Returns:
            dict: the file info
        """
        blob = self.get_blob(file_path)
        if blob:
            try:
                return {
                    'name': blob.name,
                    'size': blob.size,
                    'checksum': blob.crc32c,
                    'created': blob.time_created,
                }
            except Exception:
                self.log.exception(f'Failed to get file info for: {file_path}')
        else:
            self.log.error(f'File not found: {file_path}')
        return {}
