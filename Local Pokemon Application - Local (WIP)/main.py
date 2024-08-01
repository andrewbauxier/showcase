import requests
import csv
from PIL import Image
from io import BytesIO

def get_pokemon_data(pokemon_id):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}/'
    response = requests.get(url)
    data = response.json()

    pokemon_data = {
        'id': data['id'],
        'name': data['name'],
        'type': ', '.join([t['type']['name'] for t in data['types']])
    }

    sprite_url = data['sprites']['front_default']
    sprite_response = requests.get(sprite_url)
    pokemon_data['sprite'] = sprite_response.content

    return pokemon_data

def save_to_csv(pokemon_list, filename='pokemon_data.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['ID', 'Name', 'Type', 'Sprite']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for pokemon in pokemon_list:
            writer.writerow(pokemon)

def save_sprites(pokemon_list):
    for pokemon in pokemon_list:
        image = Image.open(BytesIO(pokemon['sprite']))
        image.save(f"{pokemon['name']}.png")

def main():
    first_5_pokemon = [get_pokemon_data(i) for i in range(1, 6)]

    save_to_csv(first_5_pokemon)
    save_sprites(first_5_pokemon)

if __name__ == "__main__":
    main()
