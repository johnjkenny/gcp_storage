from argparse import REMAINDER

from gcp_storage.arg_parser import ArgParser
from gcp_storage.cloud_storage import GCPCloudStorage


def parse_parent_args(args: dict):
    if args.get('init'):
        return storage_init(args['init'])
    if args.get('create'):
        return storage_create(args['create'])
    if args.get('get'):
        return storage_get(args['get'])
    if args.get('delete'):
        return storage_delete(args['delete'])
    if args.get('serviceAccounts'):
        return storage_service_account(args['serviceAccounts'])
    if args.get('buckets'):
        return storage_buckets(args['buckets'])
    return True


def storage_parent():
    args = ArgParser('GCP Storage Commands', None, {
        'init': {
            'short': 'I',
            'help': 'Initialize commands (gstorage-init)',
            'nargs': REMAINDER
        },
        'serviceAccounts': {
            'short': 's',
            'help': 'Service account commands (gstorage-sa)',
            'nargs': REMAINDER
        },
        'buckets': {
            'short': 'b',
            'help': 'Bucket commands (gstorage-buckets)',
            'nargs': REMAINDER
        },
        'create': {
            'short': 'c',
            'help': 'Create a storage object (gstorage-create)',
            'nargs': REMAINDER
        },
        'get': {
            'short': 'g',
            'help': 'Get storage object (gstorage-get)',
            'nargs': REMAINDER
        },
        'delete': {
            'short': 'd',
            'help': 'Delete a storage object (gstorage-delete)',
            'nargs': REMAINDER
        }
    }).set_arguments()
    if not parse_parent_args(args):
        exit(1)
    exit(0)


def parse_init_args(args: dict):
    from gcp_storage.init import Init
    if args.get('serviceAccount'):
        return Init(args['serviceAccount'], args['bucket'], args['force'])._run()
    return True


def storage_init(parent_args: list = None):
    args = ArgParser('GCP Cloud Storage Initialization', parent_args, {
        'serviceAccount': {
            'short': 'sa',
            'help': 'Service account path (full path to json file)',
            'required': True,
        },
        'bucket': {
            'short': 'b',
            'help': 'GCP bucket name to set as the default bucket',
            'required': True,
        },
        'force': {
            'short': 'F',
            'help': 'Force action',
            'action': 'store_true',
        }
    }).set_arguments()
    if not parse_init_args(args):
        exit(1)
    exit(0)


def parse_create_args(args: dict):
    if args.get('fromFile'):
        return GCPCloudStorage(args['bucket'], args['serviceAccount']).upload_file(
            args['fromFile'], args['name'], args['password'])
    if args.get('str'):
        return GCPCloudStorage(args['bucket'], args['serviceAccount']).upload_data(
            args['str'], args['name'], args['password'])
    return True


def storage_create(parent_args: list = None):
    args = ArgParser('GCP Cloud Storage Create', parent_args, {
        'serviceAccount': {
            'short': 'sa',
            'help': 'Service account name. Default: default',
            'default': 'default',
        },
        'name': {
            'short': 'n',
            'help': 'Storage object name (Include full object path in name)',
            'required': True,
        },
        'fromFile': {
            'short': 'ff',
            'help': 'Create storage object from file (full path to file)',
        },
        'str': {
            'short': 's',
            'help': 'String data to store in object text file',
            'type': str,
        },
        'password': {
            'short': 'p',
            'help': 'Password to encrypt object',
            'action': 'store_true',
        },
        'bucket': {
            'short': 'b',
            'help': 'Bucket name. Default: default',
            'default': 'default',
        }
    }).set_arguments()
    if not parse_create_args(args):
        exit(1)
    exit(0)


def parse_get_args(args: dict):
    if args.get('list'):
        return GCPCloudStorage(args['bucket'], args['serviceAccount']).display_bucket_folder_files(args.get('name'))
    if args.get('name'):
        if args.get('info'):
            return GCPCloudStorage(args['bucket'], args['serviceAccount']).display_object_info(args['name'])
        if args.get('toFile'):
            return GCPCloudStorage(args['bucket'], args['serviceAccount']).download_object_to_file(
                args['name'], args['toFile'], args['password'])
        return GCPCloudStorage(args['bucket'], args['serviceAccount']).display_downloaded_object(
            args['name'], args['password'])
    return True


def storage_get(parent_args: list = None):
    args = ArgParser('GCP Cloud Storage Get', parent_args, {
        'serviceAccount': {
            'short': 'sa',
            'help': 'Service account name. Default: default',
            'default': 'default',
        },
        'toFile': {
            'short': 'tf',
            'help': 'Store bucket download to file (full path to file)',
        },
        'name': {
            'short': 'n',
            'help': 'Object name',
        },
        'info': {
            'short': 'i',
            'help': 'Get object info',
            'action': 'store_true',
        },
        'list': {
            'short': 'l',
            'help': 'List all objects in bucket. Use with --name (-n) to filter by prefix or folder name',
            'action': 'store_true',
        },
        'password': {
            'short': 'p',
            'help': 'Password to decrypt object data',
            'action': 'store_true',
        },
        'bucket': {
            'short': 'b',
            'help': 'Bucket name. Default: default',
            'default': 'default',
        }
    }).set_arguments()
    if not parse_get_args(args):
        exit(1)
    exit(0)


def parse_delete_args(args: dict):
    if args.get('name'):
        return GCPCloudStorage(args['bucket'], args['serviceAccount']).delete_object(args['name'], args['force'])
    return True


def storage_delete(parent_args: list = None):
    args = ArgParser('GCP Cloud Storage Delete', parent_args, {
        'serviceAccount': {
            'short': 'sa',
            'help': 'Service account name. Default: default',
            'default': 'default',
        },
        'name': {
            'short': 'n',
            'help': 'Object name. Use suffix "/" to delete all objects in folder',
        },
        'force': {
            'short': 'F',
            'help': 'Force action without confirmation',
            'action': 'store_true',
        },
        'bucket': {
            'short': 'b',
            'help': 'Bucket name. Default: default',
            'default': 'default',
        }
    }).set_arguments()
    if not parse_delete_args(args):
        exit(1)
    exit(0)


def parse_service_account_args(args: dict):
    if args.get('list'):
        return GCPCloudStorage().list_service_accounts()
    if args.get('default'):
        return GCPCloudStorage().set_default_service_account(args['default'])
    if args.get('remove'):
        return GCPCloudStorage().remove_service_account(args['remove'])
    if args.get('add'):
        return GCPCloudStorage().add_service_account(args['add'])
    return True


def storage_service_account(parent_args: list = None):
    args = ArgParser('GCP Cloud Storage Service Account', parent_args, {
        'add': {
            'short': 'a',
            'help': 'Service account path (full path to json file)',
        },
        'list': {
            'short': 'l',
            'help': 'List all service accounts',
            'action': 'store_true',
        },
        'default': {
            'short': 'd',
            'help': 'Set default service account by name',
        },
        'remove': {
            'short': 'R',
            'help': 'Remove service account by name',
        },
    }).set_arguments()
    if not parse_service_account_args(args):
        exit(1)
    exit(0)


def parse_bucket_args(args: dict):
    if args.get('list'):
        return GCPCloudStorage().list_used_buckets()
    if args.get('default'):
        return GCPCloudStorage().set_default_bucket(args['default'])
    if args.get('remove'):
        return GCPCloudStorage().remove_used_bucket(args['remove'])
    return True


def storage_buckets(parent_args: list = None):
    args = ArgParser('GCP Cloud Storage Buckets', parent_args, {
        'list': {
            'short': 'l',
            'help': 'List all bucket names used',
            'action': 'store_true',
        },
        'default': {
            'short': 'd',
            'help': 'Set default bucket',
        },
        'remove': {
            'short': 'R',
            'help': 'Remove used bucket name',
        },
    }).set_arguments()
    if not parse_bucket_args(args):
        exit(1)
    exit(0)
