import pickle
import gzip
import json

def get_json_data():
    try:
        # Load data from compressed pickle file
        with gzip.open('downloaded_file.pkl.gz', 'rb') as pkl_file:
            data_from_pickle = pickle.load(pkl_file)

        # Try converting to JSON
        temp_data = json.dumps(data_from_pickle, indent=4)

        # Write JSON to file
        with open('data.json', 'w', encoding='utf-8') as json_file:
            json_file.write(temp_data)

        print("Successfully converted 'downloaded_file.pkl.gz' to 'data.json'")
        return temp_data  # Return JSON string if successful

    except (TypeError, ValueError) as e:
        print(f"Error: Data is not JSON serializable: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None
