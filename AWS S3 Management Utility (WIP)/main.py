import boto3
import random
import string
import datetime

# Initialize the S3 client
s3 = boto3.client('s3')


def list_buckets():
    """Lists existing S3 buckets."""
    response = s3.list_buckets()
    return [bucket['Name'] for bucket in response['Buckets']]


def create_bucket(first_name, last_name):
    """
    Creates a new S3 bucket with a unique name based on user's first and last name.

    Args:
    - first_name (string): User's first name.
    - last_name (string): User's last name.

    Returns:
    - string: The name of the newly created bucket.
    """
    suffix = ''.join(random.choices(string.digits, k=6))
    bucket_name = f"{first_name.lower()}{last_name.lower()}-{suffix}"
    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket '{bucket_name}' created. Press ENTER to continue.")
    input()
    return bucket_name


def put_object(bucket_name):
    """
    Adds a new object to the specified S3 bucket.

    Args:
    - bucket_name (string): Name of the target S3 bucket.
    """
    key = input("Enter object key: ")
    content = input("Enter object content: ")
    s3.put_object(Bucket=bucket_name, Key=key, Body=content)
    print(f"Type of 'bucket_name': {type(bucket_name)}")
    print(f"Value of 'bucket_name': {bucket_name}")
    print(f"Object '{key}' added to '{bucket_name}'. Press ENTER to continue.")
    input()


def list_objects_in_bucket(bucket_name):
    """
    Lists objects in the specified S3 bucket.

    Args:
    - bucket_name (string): Name of the target S3 bucket.

    Returns:
    - list: List of object keys in the bucket.
    """
    response = s3.list_objects(Bucket=bucket_name)
    objects = response.get('Contents', [])
    return [obj['Key'] for obj in objects]


def select_bucket(existing_buckets):
    """
    Asks the user to choose a bucket from the list.

    Args:
    - existing_buckets (list): List of existing S3 buckets.

    Returns:
    - string: Name of the selected S3 bucket.
    """
    print("Existing buckets:")
    for index, bucket in enumerate(existing_buckets, start=1):
        print(f"{index}. {bucket}")

    while True:
        try:
            choice = int(input("\nEnter the number of the bucket: "))
            if 1 <= choice <= len(existing_buckets):
                return existing_buckets[choice - 1]
            else:
                print("\nInvalid choice. Please enter a valid number.")
        except ValueError:
            print("\nInvalid input. Please enter a number.")


def delete_object():
    """
    Deletes an object from a user selected S3 bucket.
    """
    existing_buckets = list_buckets()
    if not existing_buckets:
        print("\nNo buckets available. Press ENTER to continue.")
        input()
        return

    # Picks bucket from bucket list
    bucket_name = select_bucket(existing_buckets)
    objects_in_bucket = list_objects_in_bucket(
        bucket_name)  # Shows objects in bucket

    if not objects_in_bucket:  # Catches empty bucket to avoid crash
        print(f"\nNo objects in '{bucket_name}'. Press ENTER to continue.")
        input()
        return

    print("\nObjects in selected bucket:")
    for index, obj in enumerate(objects_in_bucket, start=1):
        print(f"{index}. {obj}")

    while True:
        try:
            choice = int(input("\nEnter the number of the object to delete: "))
            if 1 <= choice <= len(objects_in_bucket):
                key_to_delete = objects_in_bucket[choice - 1]
                s3.delete_object(Bucket=bucket_name, Key=key_to_delete)
                print(
                    f"\nObject '{key_to_delete}' deleted from '{bucket_name}'. Press ENTER to continue.")
                input()
                return
            else:
                print("\nInvalid choice. Please enter a valid number.")
        except ValueError:
            print("\nInvalid input. Please enter a number.")


def is_bucket_empty(bucket_name):
    """
    Checks if a given S3 bucket is empty.

    Args:
    - bucket_name (string): Name of the target S3 bucket.

    Returns:
    - bool: True if the bucket is empty, False otherwise.
    """
    response = s3.list_objects(Bucket=bucket_name)
    return 'Contents' not in response


def get_bucket_name(existing_buckets):
    """
    Asks the user to choose an existing bucket from a list.

    Args:
    - existing_buckets (list): List of existing S3 buckets.

    Returns:
    - string: Name of the selected S3 bucket.
    """
    print("Existing buckets:")
    for index, bucket in enumerate(existing_buckets, start=1):
        print(f"{index}. {bucket}")

    while True:
        try:
            choice = int(
                input("\nEnter the number of the bucket you want to delete: "))
            if 1 <= choice <= len(existing_buckets):
                return existing_buckets[choice - 1]
            else:
                print("\nInvalid choice. Please enter a valid number.")
        except ValueError:
            print("\nInvalid input. Please enter a number.")


def delete_bucket(bucket_name, existing_buckets):
    """
    Deletes an existing S3 bucket after user confirmation.

    Args:
    - bucket_name (string): Name of the target S3 bucket.
    - existing_buckets (list): List of existing S3 buckets gathered before operations.
    """
    if not existing_buckets:
        print("\nNo buckets to delete. Press ENTER to continue.")
        input()
        return

    bucket_name = get_bucket_name(existing_buckets)

    if is_bucket_empty(bucket_name):
        s3.delete_bucket(Bucket=bucket_name)
        print(f"\nBucket '{bucket_name}' deleted. Press ENTER to continue.")
        existing_buckets.remove(bucket_name)
    else:
        print(
            f"\nBucket '{bucket_name}' is not empty. Empty the bucket first then try again. Press ENTER to continue.")
        input()


def copy_object():
    """
    Copies an object from one S3 bucket to another, specified by the user.
    """
    source_bucket = input("Enter source bucket name: ")
    source_key = input("Enter source object key: ")
    destination_bucket = input("Enter destination bucket name: ")
    destination_key = input("Enter destination object key: ")
    s3.copy_object(Bucket=destination_bucket, CopySource={
                   'Bucket': source_bucket, 'Key': source_key}, Key=destination_key)
    print(
        f"\nObject '{source_key}' copied from '{source_bucket}' to '{destination_bucket}'. Press ENTER to continue.")
    input()


def download_object(bucket_name):
    """
    Downloads an object from the specified S3 bucket to the local machine.
    Args:
    - bucket_name (string): Name of the target S3 bucket.
    """
    key = input("Enter object key to download: ")
    file_name = input(
        "Enter the file name for the local copy you are downloading: ")
    s3.download_file(Bucket=bucket_name, Key=key, Filename=file_name)
    print(
        f"\nObject '{key}' downloaded from '{bucket_name}' and saved to '{file_name}'. Press ENTER to continue.")
    input()


def main():
    """
    Main program and main menu for interacting with AWS S3 services.
    """
    existing_buckets = list_buckets()
    bucket_name = None  # Initialize the bucket_name variable
    print(list_buckets())

    # input("Enter your first name: ") <--TODO uncomment before submission
    first_name = "Andrew"  # <--TODO delete before submission
    # input("Enter your last name: ") <--TODO uncomment before submission
    last_name = "Auxier"  # <--TODO delete before submission

    while True:
        print("\nAWS S3 Menu:")
        print("1. Create Bucket")
        print("2. Put Object")
        print("3. Delete Object")
        print("4. Delete Bucket")
        print("5. Copy Object")
        print("6. Download Object")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ")

        if choice == '1':
            bucket_name = create_bucket(first_name, last_name)
        elif choice == '2':
            put_object(bucket_name)
        elif choice == '3':
            delete_object()
        elif choice == '4':
            delete_bucket(bucket_name, existing_buckets)
        elif choice == '5':
            copy_object()
        elif choice == '6':
            download_object(bucket_name)
        elif choice == '7':
            print(
                f"Exiting the program. Date and time: {datetime.datetime.now()}")
            break
        else:
            print(
                "\nInvalid choice. Please enter a number between 1 and 7. Press ENTER to continue")
            input()


if __name__ == "__main__":
    main()
