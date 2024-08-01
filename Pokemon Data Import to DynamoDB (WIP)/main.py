import requests
import boto3

# Set up DynamoDB client
dynamodb = boto3.resource('dynamodb')
pokemon_table = dynamodb.create_table(
    TableName='PokemonTable',
    KeySchema=[
        {
            'AttributeName': 'ID',
            'KeyType': 'HASH'
        },
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'ID',
            'AttributeType': 'S'
        },
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

# Wait until the table is created
pokemon_table.meta.client.get_waiter(
    'table_exists').wait(TableName='PokemonTable')

# Function to fetch Pokémon data from PokeAPI


def fetch_pokemon_data(pokemon_id):
    try:
        response = requests.get(
            f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
        data = response.json()
        return {
            'id': f"{pokemon_id:03}",  # Pad with zeros to match your ID format
            'Name': data['name'],
            'Types': [t['type']['name'] for t in data['types']],
            # Add other attributes as needed
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for Pokemon {pokemon_id}: {e}")
        return None

# Function to batch write Pokémon data to DynamoDB


def batch_write_pokemon_data(pokemon_data):
    with pokemon_table.batch_writer() as batch:
        for item in pokemon_data:
            batch.put_item(Item=item)


# Fetch and add Pokémon data
pokemon_ids = range(1, 4)  # IDs for the first 151 Pokémon
pokemon_data = []

for pokemon_id in pokemon_ids:
    data = fetch_pokemon_data(pokemon_id)
    if data:
        pokemon_data.append(data)

# Add data to DynamoDB
batch_write_pokemon_data(pokemon_data)

print("Successfully added Pokémon data to DynamoDB.")
