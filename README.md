# GCP-Storage

This is a simple command line tool to interact with Google Cloud Storage. The tool allows you to create, get, and
delete storage objects in GCP buckets. The tool also allows you to manage service accounts and set default buckets for
use. You can upload storage object with string data or from file. It has the option to use a password to encrypt and
decrypt the storage object data so incase the GCP service account key is compromised the object data is still secure.
The service account keys are stored in the `gcp_storage/gcp_env` directory and encrypted with a generated cipher key.

The tool has the following features:
- Initialize GCP environment with service account and default bucket
- Create storage object with string data or from file
- Get storage object and display contents to console or store to file
- Delete storage object or all objects with prefix (folder path if `/` is used in names)
- List all objects in bucket and filter by prefix (folder path if `/` is used in names)
- List service accounts
- Set default service account
- Remove and add service account
- List used buckets for fast lookup incase many buckets are used in your environment
- Set default bucket
- Remove bucket name from used buckets


## Prerequisites

- GCP project access
- Create service account that has `Storage Admin` role permissions
- Download service account key in JSON format
- Python 3.12 environment


## Usage:

### Parent Commands:

```bash
# Command Options:
gstorage -h
usage: gstorage [-h] [-I ...] [-s ...] [-b ...] [-c ...] [-g ...] [-d ...]

GCP Storage Commands

options:
  -h, --help            show this help message and exit

  -I ..., --init ...    Initialize commands (gstorage-init)

  -s ..., --serviceAccounts ...
                        Service account commands (gstorage-sa)

  -b ..., --buckets ...
                        Bucket commands (gstorage-buckets)

  -c ..., --create ...  Create a storage object (gstorage-create)

  -g ..., --get ...     Get storage object (gstorage-get)

  -d ..., --delete ...  Delete a storage object (gstorage-delete)
```

### Initialize Environment:

```bash
gstorage -I -h
usage: gstorage [-h] -sa SERVICEACCOUNT -b BUCKET [-F]

GCP Cloud Storage Initialization

options:
  -h, --help            show this help message and exit

  -sa SERVICEACCOUNT, --serviceAccount SERVICEACCOUNT
                        Service account path (full path to json file)

  -b BUCKET, --bucket BUCKET
                        GCP bucket name to set as the default bucket

  -F, --force           Force action
```

1. Run the init command:
```bash
gstorage -I -sa /home/myUser/sa.json -b test_bucket1
```


### Create Cloud Storage Objects:

```bash
# Command Options:
gstorage -c -h
usage: gstorage [-h] [-sa SERVICEACCOUNT] -n NAME [-ff FROMFILE] [-s STR] [-p] [-b BUCKET]

GCP Cloud Storage Create

options:
  -h, --help            show this help message and exit

  -sa SERVICEACCOUNT, --serviceAccount SERVICEACCOUNT
                        Service account name. Default: default

  -n NAME, --name NAME  Storage object name (Include full object path in name)

  -ff FROMFILE, --fromFile FROMFILE
                        Create storage object from file (full path to file)

  -s STR, --str STR     String data to store in object text file

  -p, --password        Password to encrypt object

  -b BUCKET, --bucket BUCKET
                        Bucket name. Default: default
```

1. Create object with string data:
```bash
gstorage -c -n test1.txt -s "this is a test"
[2025-03-26 15:45:47,858][INFO][cloud_storage,152]: Successfully uploaded data to test1.txt

# Create object with folder like sorting:
gstorage -c -n f1/f2/test123.txt -s "this was also a test"
[2025-03-26 15:45:47,858][INFO][cloud_storage,152]: Successfully uploaded data to f1/f2/test123.txt

# Create object with password:
gstorage -c -n test2.txt -s "this is a test 2" -p
Enter password: 
Verify password: 
[2025-03-26 15:48:16,341][INFO][cloud_storage,152]: Successfully uploaded data to test2.txt
```

2. Create object with file data:
```bash
echo "this was a test3" > test3.txt
gstorage -c -n test3.txt -ff ./test3.txt
[2025-03-26 15:49:50,652][INFO][cloud_storage,175]: Successfully uploaded file ./test3.txt to test3.txt

# Create object with password:
gstorage -c -n test4.txt -ff ./test3.txt -p
Enter password:
Verify password:
[2025-03-26 15:50:49,943][INFO][cloud_storage,152]: Successfully uploaded data to test4.txt
```

### Get Cloud Storage Objects:

```bash
# Command Options:
gstorage -g -h              
usage: gstorage [-h] [-sa SERVICEACCOUNT] [-tf TOFILE] [-n NAME] [-i] [-l] [-p] [-b BUCKET]

GCP Cloud Storage Get

options:
  -h, --help            show this help message and exit

  -sa SERVICEACCOUNT, --serviceAccount SERVICEACCOUNT
                        Service account name. Default: default

  -tf TOFILE, --toFile TOFILE
                        Store bucket download to file (full path to file)

  -n NAME, --name NAME  Object name

  -i, --info            Get object info

  -l, --list            List all objects in bucket. Use with --name (-n) to filter by prefix or
                        folder name

  -p, --password        Password to decrypt object data

  -b BUCKET, --bucket BUCKET
                        Bucket name. Default: default
```

1. List all objects in bucket:

```bash
gstorage -g -l
# output:
Contents:
  f1/f2/test123.txt
  test1.txt
  test2.txt
  test3.txt
  test4.txt
  test5.txt

# Use --name (-n) to filter by prefix or folder name
gstorage -g -l -n f1
# output:
Contents:
  f1/f2/test321.txt
```

2. Get object and display contents to console:
```bash
gstorage -g -n test4.txt
# output:
Downloaded data:
this was a test2
```

3. Get object with password and display contents to console:
```bash
# Failed to provide password/incorrect password will result in error
gstorage -g -n test5.txt
# output:
[2025-03-26 15:11:18,423][ERROR][cloud_storage,426]: Failed to decrypt data
Failed to download data: test5.txt

gstorage -g -n test5.txt -p 
Enter password:
# output:
Downloaded data:
this was a test2
```

4. Get object and store to file:
```bash
gstorage -g -n test4.txt -tf ./test4.txt
# output:
[2025-03-26 15:26:09,113][INFO][cloud_storage,382]: Successfully downloaded object to file ./test4.txt
```

5. Get encrypted object and store to file:
```bash
# example without password
gstorage -g -n test5.txt -tf ./test5.txt
[2025-03-26 15:27:02,568][INFO][cloud_storage,382]: Successfully downloaded object to file ./test5.txt
# Data is still encrypted
cat test5.txt
�K���UԊ��)U��

# example with password
 gstorage -g -n test5.txt -tf ./test5.txt -p
Enter password: 
# output:
[2025-03-26 15:32:22,072][INFO][cloud_storage,396]: Successfully downloaded object to file ./test5.txt
cat test5.txt                              
this was a test2
```
6. Get Object Info:
```bash
gstorage -g -i -n f1/f2/test321.txt
Object Info:
{
  "name": "f1/f2/test321.txt",
  "size": null,
  "checksum": null,
  "created": null
}
```

### Delete Cloud Storage Objects:

```bash
gstorage -d -h
usage: gstorage [-h] [-sa SERVICEACCOUNT] [-n NAME] [-F] [-b BUCKET]

GCP Cloud Storage Delete

options:
  -h, --help            show this help message and exit

  -sa SERVICEACCOUNT, --serviceAccount SERVICEACCOUNT
                        Service account name. Default: default

  -n NAME, --name NAME  Object name. Use suffix "/" to delete all objects in folder

  -F, --force           Force action without confirmation

  -b BUCKET, --bucket BUCKET
                        Bucket name. Default: default
```

```bash
# Delete single object
gstorage -d -n test5.txt -F
[2025-03-26 16:02:57,302][INFO][cloud_storage,463]: Successfully deleted object test5.txt

gstorage -g -l          
Contents:
  f1/f2/test123.txt
  test1.txt
  test2.txt
  test3.txt
  test4.txt

gstorage -d -n test5.txt -F
[2025-03-26 16:05:57,763][ERROR][cloud_storage,468]: File not found: test5.txt

# Delete all objects in folder (prefix delete)
gstorage -d -n f1/f2/ -F
[2025-03-26 16:09:46,122][INFO][cloud_storage,438]: Deleting files in folder: f1/f2/
[2025-03-26 16:09:46,806][INFO][cloud_storage,443]: Deleted file: f1/f2/test123.txt

gstorage -g -l            
Contents:
  test1.txt
  test2.txt
  test3.txt
  test4.txt

# create dir structure for test and deleting multiple files:
gstorage -c -n f1/f2/test1.txt -s 'test1'
[2025-03-26 16:11:57,265][INFO][cloud_storage,153]: Successfully uploaded data to f1/f2/test1.txt

gstorage -c -n f1/f2/test2.txt -s 'test2'
[2025-03-26 16:12:04,536][INFO][cloud_storage,153]: Successfully uploaded data to f1/f2/test2.txt

gstorage -c -n f1/f3/test3.txt -s 'test3'
[2025-03-26 16:12:14,980][INFO][cloud_storage,153]: Successfully uploaded data to f1/f3/test3.txt

gstorage -g -l                           
Contents:
  f1/f2/test1.txt
  f1/f2/test2.txt
  f1/f3/test3.txt
  test1.txt
  test2.txt
  test3.txt
  test4.txt

gstorage -d -n f1/f2/ -F
[2025-03-26 16:12:40,597][INFO][cloud_storage,438]: Deleting files in folder: f1/f2/
[2025-03-26 16:12:41,266][INFO][cloud_storage,443]: Deleted file: f1/f2/test1.txt
[2025-03-26 16:12:41,503][INFO][cloud_storage,443]: Deleted file: f1/f2/test2.txt

gstorage -g -l       
Contents:
  f1/f3/test3.txt
  test1.txt
  test2.txt
  test3.txt
  test4.txt


# Delete multiple folders test
gstorage -c -n f1/f2/test1.txt -s 'test1'
[2025-03-26 16:14:13,974][INFO][cloud_storage,153]: Successfully uploaded data to f1/f2/test1.txt

gstorage -c -n f1/f2/test2.txt -s 'test2'
[2025-03-26 16:14:18,798][INFO][cloud_storage,153]: Successfully uploaded data to f1/f2/test2.txt

gstorage -d -n f1/ -F
[2025-03-26 16:14:32,099][INFO][cloud_storage,438]: Deleting files in folder: f1/
[2025-03-26 16:14:32,711][INFO][cloud_storage,443]: Deleted file: f1/f2/test1.txt
[2025-03-26 16:14:32,916][INFO][cloud_storage,443]: Deleted file: f1/f2/test2.txt
[2025-03-26 16:14:33,121][INFO][cloud_storage,443]: Deleted file: f1/f3/test3.txt

gstorage -g -l                           
Contents:
  test1.txt
  test2.txt
  test3.txt
  test4.txt

# Using prefix '/' for folder name prefix example:

gstorage -c -n /test2.txt -s 'test2'
[2025-03-26 16:16:46,653][INFO][cloud_storage,153]: Successfully uploaded data to /test2.txt

gstorage -g -l                      
Contents:
  /test2.txt
  test1.txt
  test2.txt
  test3.txt
  test4.txt

gstorage -d -n / -F
[2025-03-26 16:18:00,698][INFO][cloud_storage,438]: Deleting files in folder: /
[2025-03-26 16:18:01,238][INFO][cloud_storage,443]: Deleted file: /test2.txt

# Prompt for delete example (without --force or -F):
gstorage -d -n test1.txt 
Delete object test1.txt? (y/n): y
[2025-03-26 18:18:40,486][INFO][cloud_storage,541]: Successfully deleted object test1.txt
```


### Service Account Commands:

```bash
# Command Options:
gstorage -s -h
usage: gstorage [-h] [-a ADD] [-l] [-d DEFAULT] [-R REMOVE]

GCP Cloud Storage Service Account

options:
  -h, --help            show this help message and exit

  -a ADD, --add ADD     Service account path (full path to json file)

  -l, --list            List all service accounts

  -d DEFAULT, --default DEFAULT
                        Set default service account by name

  -R REMOVE, --remove REMOVE
                        Remove service account by name
```

1. Add Service Account:
```bash
gstorage -s -a /home/myUser/sa2.json 
Added service account test-sa02
Service accounts:
  test-sa02
  test-sa01 (default)
```

2. Set default service account:
```bash
gstorage -s -d test-sa02             
Set default service account to test-sa02
Service accounts:
  test-sa02 (default)
  test-sa01
```

3. Remove Service Account:
```bash
gstorage -s -R test-sa02
Removed service account test-sa02
Service accounts:
  test-sa01 (default)
```

4. List Service Accounts:
```bash
gstorage -s -l
Service accounts:
  test-sa02
  test-sa01 (default)
```

### Bucket Commands:

```bash
# Command Options:
usage: gstorage [-h] [-l] [-d DEFAULT] [-R REMOVE]

GCP Cloud Storage Buckets

options:
  -h, --help            show this help message and exit

  -l, --list            List all bucket names used

  -d DEFAULT, --default DEFAULT
                        Set default bucket

  -R REMOVE, --remove REMOVE
                        Remove used bucket name
```

1. list used buckets:
```bash
gstorage -b -l                                                
Used Buckets:
    test_bucket1 (default)
```

2. Set default bucket:
```bash
gstorage -b -d test_bucket2
Set default bucket to test_bucket2
Used Buckets:
  test_bucket1
  test_bucket2 (default)
```

3. Remove used bucket:
```bash
gstorage -b -R test_bucket2       
Removed bucket test_bucket2
Used Buckets:
  test_bucket1 (default)
```
