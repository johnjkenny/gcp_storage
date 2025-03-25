from setuptools import setup


try:
    setup(
        name='gstorage',
        version='1.0.0',
        entry_points={'console_scripts': [
            'gstorage = gcp_storage.cli:storage_parent',
            'gstorage-init = gcp_storage.cli:storage_init',
        ]},
    )
    exit(0)
except Exception as error:
    print(f'Failed to setup package: {error}')
    exit(1)
