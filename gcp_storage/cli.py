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
        # return storage_delete(args['delete'])
        pass
    if args.get('serviceAccounts'):
        pass
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
        'create': {
            'short': 'c',
            'help': 'Create a secret object (gstorage-create)',
            'nargs': REMAINDER
        },
        'get': {
            'short': 'g',
            'help': 'Get secret data (gstorage-get)',
            'nargs': REMAINDER
        },
        'delete': {
            'short': 'd',
            'help': 'Delete a secret object (gstorage-delete)',
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
    args = ArgParser('GCP Secret Initialization', parent_args, {
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
        if args.get('name'):
            return GCPCloudStorage(args['bucket'], args['serviceAccount']).display_bucket_folder_files(args['name'])
        if args.get('list'):
            return GCPCloudStorage(args['bucket'], args['serviceAccount']).display_bucket_folder_files()
    elif args.get('name'):
        if args.get('toFile'):
            GCPCloudStorage(args['bucket'], args['serviceAccount']).get_secret_to_file(
                args['name'], args['toFile'], args['password'], args['version'])
        else:
            GCPCloudStorage(args['bucket'], args['serviceAccount']).get_secret(
                args['name'], args['password'], args['version'], True)
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
            'help': 'Secret name',
        },
        'list': {
            'short': 'l',
            'help': 'List all secrets',
            'action': 'store_true',
        },
        'version': {
            'short': 'v',
            'help': 'Secret version. Default: latest',
            'default': 'latest',
        },
        'password': {
            'short': 'p',
            'help': 'Password to decrypt secret data',
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
