
# Project Name:    Homework 4
# Module Name:     main.py
# Author:          Andrew Auxier
# Contributors:    Jim
# Class:           SDEV 400 6381 Secure Programming in the Cloud (2242)
# Organization:    University of Maryland Global Campus
# Description:     
    
#     This Program works on AWS using the Cloud9 IDE CLI. It pulls pokemon data from PokeAPI and then formats it into a menu driven application where the user can search through and examine aspects about the pokemon. The functionality is light but can be expanded upon.


import boto3
import requests
import re
from boto3.dynamodb.conditions import Attr


def main():
    try:
        welcome_message()
    except Exception as e:
        print(f"An error occurred: {e}")

def welcome_message():
    print("\nWelcome to the AWS Pokemon App!")
    print("The app begins by collecting necessary data from PokeAPI and importing it to AWS.")
    print("The process will ask for a table and bucket name then becomes automated from there.")
    print("Next, a menu will pop up asking for options. The options are:")
    print("Find Pokemon by ID: Enter the pokemon ID to select and view that pokemon's data.")
    print("Find Pokemon by Name: Find a pokemon by entering their name (not case sensitive).")
    print("Find Pokemon by Type: Enter a pokemon type to list all pokemon with that type")
    print("List All Pokemon: Lists all pokemon located in the table. Warning: The List could be long")
    print("Download Pokemon Sprite by ID: Downloads the pokemons sprite to your local storage")
    print("Exit Program: Performs clean up to remove tables and buckets then gracefully exits (hopefully).")

    initialize_program()

def initialize_program():
    try:
        print("\nInitializing Program, Please Standby.")
        bucket_name, table_name = get_user_input()
        sprite_bucket, pokemon_table = setup_resources(bucket_name, table_name)
        print("Table and buckets created, now uploading data.")
        upload_pokemon_data(sprite_bucket, pokemon_table)
        menu(sprite_bucket, pokemon_table)

    except Exception as e:
        print(f"An error occurred: {e}")
        clean_up_on_error(sprite_bucket, pokemon_table)

def setup_resources(bucket_name, table_name):
    sprite_bucket = create_s3_bucket(bucket_name)
    pokemon_table = create_dynamodb_table(table_name)
    return sprite_bucket, pokemon_table

def upload_pokemon_data(sprite_bucket, pokemon_table):
    try:
        print("\nThis next section determines the range of the pokemon to upload.")
        print("\nWarning: Pokeapi limits calls to 300 per 24 hour period. ")
        range_min = int(input("\nWhat pokemon would you like to start at? (Try 1): "))
        range_max = int(input("\nWhat pokemon would you like to end at? (Try 9): "))

        for pokemon_id in range(range_min, range_max + 1):
            pokemon_data = fetch_pokemon_data(pokemon_id)
            store_sprites_to_s3(sprite_bucket, [pokemon_data])
            batch_write_pokemon_data([pokemon_data], pokemon_table)

    except Exception as e:
        print(f"An error occurred during data upload: {e}")
        raise  # Re-raise the exception to trigger the cleanup

def clean_up_on_error(sprite_bucket, pokemon_table):
    delete_dynamodb_table(pokemon_table)

    if 'sprite_bucket' in locals():
        delete_s3_bucket(sprite_bucket)


def get_user_input():
    # Validates user input and returns validated versions
    bucket_name = get_valid_bucket_name()
    table_name = get_valid_table_name()
    return bucket_name, table_name


def get_valid_bucket_name():
    while True:
        bucket_name = input("\nEnter a name for your S3 Pokemon Sprite bucket: ")
        if is_valid_bucket_name(bucket_name):
            return bucket_name
        else:
            print("Invalid input. Bucket name must be alphanumeric and between 3-63 characters.")


def get_valid_table_name():
    while True:
        table_name = input("Enter a name for your DynamoDB Pokemon Data Table: ")
        if is_valid_table_name(table_name):
            return table_name
        else:
            print("Invalid input. Table name must be alphanumeric and between 3-63 characters.")


def is_valid_bucket_name(bucket_name):
    # Allow only letters and numbers, length between 3 and 63 characters
    return re.match("^[a-zA-Z0-9]{3,63}$", bucket_name) is not None


def is_valid_table_name(table_name):
    # Allow only letters and numbers, length between 3 and 63 characters
    return re.match("^[a-zA-Z0-9]{3,63}$", table_name) is not None


def create_s3_bucket(bucket_name):
    print("\nCreating Bucket Now, Please Standby.")
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket=bucket_name)
    print(f"Successfully created '{bucket_name}'")
    return bucket_name


def delete_s3_bucket(sprite_bucket):
    print("Deleting Bucket Now, Please Standby.")
    s3 = boto3.client('s3')
    # List all objects in the bucket
    objects = s3.list_objects(Bucket=sprite_bucket).get('Contents', [])
    # Delete each object in the bucket
    for obj in objects:
        s3.delete_object(Bucket=sprite_bucket, Key=obj['Key'])
    # Delete the bucket itself
    s3.delete_bucket(Bucket=sprite_bucket)
    print(f"Successfully deleted '{sprite_bucket}'")


def create_dynamodb_table(table_name):
    print("\nCreating Table Now, Please Standby.")
    dynamodb = boto3.resource('dynamodb')
    pokemon_table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    # Wait until the table is created
    pokemon_table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"Successfully created '{table_name}'")
    return pokemon_table


def delete_dynamodb_table(pokemon_table):
    try:
        print("Deleting Table Now, Please Standby.")
        table_name = pokemon_table.table_name
        dynamodb = boto3.client('dynamodb')
        dynamodb.delete_table(TableName=table_name)
        dynamodb.get_waiter('table_not_exists').wait(TableName=table_name)
        print(f"Successfully deleted '{table_name}'")
    except Exception as e:
        print(f"An error occurred during cleanup: {e}")


def fetch_pokemon_data(id):
    try:
        # Calls PokeAPI for the requested data
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{id}')
        response.raise_for_status()
        data = response.json()
        name = data.get('name', '')
        types = [t['type']['name'] for t in data.get('types', [])]

        return {
            'id': id,
            'Name': name,
            'Types': types,
            # Front default is the standard game sprite image, more images are available
            # such as shinies, or what not.
            'Sprites': data.get('sprites', {}).get('front_default', None), 
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for Pokemon {id}: {e}")
        return None

def store_sprites_to_s3(bucket_name, pokemon_data):
    s3 = boto3.client('s3')
    # Iterates through sprite data in table to retrieve sprites
    for data in pokemon_data:
        sprite_url = data.get('Sprites', None)

        if sprite_url:
            sprite_name = sprite_url.split('/')[-1]
            sprite_image_response = requests.get(sprite_url)
            sprite_image_response.raise_for_status()
            sprite_image_data = sprite_image_response.content

            # Upload sprite image to bucket
            s3.put_object(Bucket=bucket_name, Key=sprite_name, Body=sprite_image_data)
            print(f"Uploaded sprite '{sprite_name}' to '{bucket_name}'")
        else:
            print("No sprite data to upload.")


def batch_write_pokemon_data(pokemon_data, pokemon_table):
    with pokemon_table.batch_writer() as batch:
        for item in pokemon_data:
            try:
                batch.put_item(Item=item)
                print(f"Successfully uploaded Pokemon data for ID {item['id']}")
            except Exception as e:
                print(f"Error uploading Pokemon data for ID {item['id']}: {e}")



def menu(sprite_bucket, pokemon_table):
    while True:
        print("\nMenu:")
        print("1. Find Pokemon by ID")
        print("2. Find Pokemon by Name")
        print("3. Find Pokemon by Type")
        print("4. List all Pokémon in DynamoDB")
        print("5. Download Pokemon Sprite by ID")
        print("6. Exit Program")
    
        choice = input("\nEnter your choice (1-6): ")
    
        if choice == '1':
            find_pokemon_by_id(pokemon_table)
        elif choice == '2':
            find_pokemon_by_name(pokemon_table)
        elif choice == '3':
            find_pokemon_by_type(pokemon_table)
        elif choice == '4':
            list_all_pokemon(pokemon_table)
        elif choice == '5':
            download_pokemon_sprite_by_id(sprite_bucket)
        elif choice == '6':
            clean_up_and_exit(pokemon_table, sprite_bucket)
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
    return choice

# Menu Functions listed below
def find_pokemon_by_id(pokemon_table):
    try:
        print("\nEnter an ID number from within the range you provided. ")
        pokemon_id = int(input("Enter the Pokemon ID now: "))
        response = pokemon_table.get_item(Key={'id': int(pokemon_id)})

        if 'Item' in response:
            print("Pokemon found:")
            print(response['Item'])
        else:
            print(f"No Pokemon found with ID {pokemon_id}")
    except Exception as e:
        print(f"An error occurred: {e}")
    

def find_pokemon_by_name(pokemon_table):
    try:
        print("\Enter the pokemon's name. Try 'Ivysaur'.")
        pokemon_name = input("Enter the Pokemon Name: ").lower()
        scan_response = pokemon_table.scan(FilterExpression=Attr('Name').eq(pokemon_name))

        if 'Items' in scan_response and scan_response['Items']:
            print("Pokemon found:")
            for item in scan_response['Items']:
                print(item)
        else:
            print(f"No Pokemon found with the name {pokemon_name}")
    except Exception as e:
        print(f"An error occurred: {e}")


def find_pokemon_by_type(pokemon_table):
    try:
        print("\nEnter the Pokemon type you wish to filter by. Try 'grass'")
        pokemon_type = input("Enter the Pokemon Type: ").lower()
        scan_response = pokemon_table.scan(FilterExpression=Attr('Types').contains(pokemon_type))

        if 'Items' in scan_response and scan_response['Items']:
            # Sort the list of Pokemon data based on their IDs
            sorted_pokemon_data = sorted(scan_response['Items'], key=lambda x: x['id'])
            
            # Iterate through the list and print the entries
            print("Pokemon found:")
            for item in sorted_pokemon_data:
                print(item)
        else:
            print(f"No Pokemon found with the type {pokemon_type}")
    except Exception as e:
        print(f"An error occurred: {e}")



def list_all_pokemon(pokemon_table):
    try:
        scan_response = pokemon_table.scan()
        
        if 'Items' in scan_response and scan_response['Items']:
            # Sort the list of Pokemon data based on their IDs
            sorted_pokemon_data = sorted(scan_response['Items'], key=lambda x: x['id'])
            
            print("All Pokemon in DynamoDB:")
            for item in sorted_pokemon_data:
                # Convert 'id' to int before printing
                pokemon_data = {
                    'id': int(item['id']),
                    'Name': item['Name'],
                    'Types': item['Types']
                }
                print(pokemon_data)
        else:
            print("No Pokemon found in DynamoDB")
    except Exception as e:
        print(f"An error occurred: {e}")



def download_pokemon_sprite_by_id(sprite_bucket):
    try:
        
        pokemon_id = int(input("Enter the Pokemon ID to download sprite: "))
        sprite_name = f"{pokemon_id}.png"

        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=sprite_bucket, Key=sprite_name)

        with open(sprite_name, 'wb') as file:
            file.write(response['Body'].read())

        print(f"Sprite downloaded as '{sprite_name}'")
    except Exception as e:
        print(f"An error occurred: {e}")
        

def clean_up_and_exit(pokemon_table, sprite_bucket):
    clean_up_finished = False
    while not clean_up_finished:
        try:
            
            # Delete DynamoDB table
            delete_table_input = int(input("\nWould you like to delete your Table? (1 for yes, 2 for no): "))
            if delete_table_input == 1:
                delete_dynamodb_table(pokemon_table)
            elif delete_table_input == 2:
                pass
            else:
                print ("\nPlease choose 1 for 'yes' or 2 for 'no'")
            
            # Delete S3 Bucket
            delete_bucket_input = int(input("\nWould you like to delete your Bucket? (1 for yes, 2 for no): "))
            if delete_bucket_input == 1:
                delete_s3_bucket(sprite_bucket)
            elif delete_bucket_input == 2:
                pass
            else:
                print ("\nPlease choose 1 for 'yes' or 2 for 'no'")
    
            print("Cleanup complete. Exiting program.")
            clean_up_finished = True
            exit()
            
        except Exception as e:
            print(f"An error occurred during cleanup: {e}")
        
if __name__ == "__main__":
    main()
