import json
import os

def local_store(data, file_path='data/sources.json'):
      """
      Store data locally into a JSON file.
      """
      # Create the directory if it does not exist
      os.makedirs(os.path.dirname(file_path), exist_ok=True)
      
      # Load existing data
      if os.path.exists(file_path):
            with open(file_path, 'r') as file:
             try:
                  existing_data = json.load(file)
             except json.JSONDecodeError:
                  existing_data = []
      else:
            existing_data = []

      # Ensure existing_data is a list
      if not isinstance(existing_data, list):
            existing_data = []

      # Append new data
      existing_data.append(data)

      # Save updated data back to the file
      with open(file_path, 'w') as file:
            json.dump(existing_data, file)


def local_read(file_path='data/sources.json'):
      """
      Read locally stored data from the JSON file.
      """
      with open(file_path, 'r') as file:
            data = json.load(file)
      return data


def local_empty(file_path='data/sources.json'):
    """
    Empties the JSON file.
    """
    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write an empty list to the file
    with open(file_path, 'w') as file:
        json.dump([], file)