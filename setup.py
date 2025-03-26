from setuptools import setup


try:
    setup(
        name='gstorage',
        version='1.0.0',
        entry_points={'console_scripts': [
            'gstorage = gcp_storage.cli:storage_parent',
            'gstorage-init = gcp_storage.cli:storage_init',
            'gstorage-sa = gcp_storage.cli:storage_service_account',
            'gstorage-buckets = gcp_storage.cli:storage_buckets',
            'gstorage-create = gcp_storage.cli:storage_create',
            'gstorage-get = gcp_storage.cli:storage_get',
            'gstorage-delete = gcp_storage.cli:storage_delete',
        ]},
    )
    exit(0)
except Exception as error:
    print(f'Failed to setup package: {error}')
    exit(1)
