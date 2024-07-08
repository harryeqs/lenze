import json

def local_store(data, file_path='data/sources.json'):
      """
      Store data locally into a JSON file.
      """
      with open(file_path, 'w') as file:
            json.dump(data, file)

def local_read(file_path='data/sources.json'):
      """
      Read locally stored data from the JSON file.
      """
      with open(file_path, 'r') as file:
            data = json.load(file)
      return data