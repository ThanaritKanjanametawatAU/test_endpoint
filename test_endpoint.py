import requests
import os
import io
from PIL import Image
import base64
import random
import json
import time
import dotenv
import argparse

# Add argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--local', type=bool, default=False, help='Whether to test local endpoint')
args = parser.parse_args()

dotenv.load_dotenv()

# Set endpoint based on local argument
if args.local:
    endpoint = "http://localhost:8000/runsync"
    headers = {}
else:
    endpoint = os.environ.get("RUNPOD_ENDPOINT")
    bearer_token = os.environ.get("RUNPOD_BEARER_TOKEN")
    headers = {"Authorization": f"Bearer {bearer_token}"}

def save_request_body(test_name, endpoint_body):
    os.makedirs("ready-to-use", exist_ok=True)
    with open(f"ready-to-use/{test_name}.json", "w") as f:
        json.dump(endpoint_body, f, indent=2)


def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def modify_workflow(workflow, modifications):
    """
    Apply modifications to the workflow based on configuration.
    
    Args:
        workflow (dict): The original workflow dictionary
        modifications (list): List of modifications, each containing a path and value
            path: List of keys/indices to traverse
            value: New value to set at the target location
    
    Returns:
        dict: Modified workflow
    """
    modified = workflow.copy()
    
    for mod in modifications:
        path = mod["path"]
        value = mod["value"]
        
        # Navigate to the target location
        current = modified
        for key in path[:-1]:  # Navigate until the second-to-last key
            if isinstance(current, dict):
                if key not in current:
                    current[key] = {}
                current = current[key]
            elif isinstance(current, list):
                key = int(key)  # Convert string indices to integers for lists
                while len(current) <= key:
                    current.append({})  # Extend list if needed
                current = current[key]
            else:
                raise ValueError(f"Cannot navigate through type {type(current)}")
        
        # Set the value at the final location
        final_key = path[-1]
        if isinstance(current, dict):
            current[final_key] = value
        elif isinstance(current, list):
            current[int(final_key)] = value
        else:
            raise ValueError(f"Cannot set value in type {type(current)}")
    
    return modified

def test_endpoint(workflow_path, modifications=None, image_path=None):
    # Read the workflow JSON file
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    # Apply modifications if any
    if modifications:
        workflow = modify_workflow(workflow, modifications)

    # Prepare the base endpoint body
    endpoint_body = {
        "input": {
            "workflow": workflow
        }
    }
    
    # Add image if provided
    if image_path:     
        print(f"Using image: {image_path}")
        try:
            image_string = convert_image_to_base64(image_path)
            endpoint_body["input"]["images"] = [
                {
                    "name": "current.jpg",
                    "image": image_string
                }
            ]
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return

    try:
        # Make the API request
        start_time = time.time()
        response = requests.post(endpoint, json=endpoint_body, headers=headers)
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")
        save_request_body(test_name, endpoint_body)
        print(f"Saved request body to ready-to-use/{test_name}.json")
        response.raise_for_status()
        
        # Parse the response
        response_data = response.json()
        image_string = response_data["output"]["message"]
        
        # Decode and save/show the image
        image_data = base64.b64decode(image_string)
        image = Image.open(io.BytesIO(image_data))
        

        # Save image and print location
        output_dir = "local_endpoint_result" if args.local else "runpod_endpoint_result"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{test_name}.jpg"
        image.save(output_path)
        print(f"Image saved as {output_path}")
        
        # Print that the test name is completed with green checkmark
        print(f"\033[92m{test_name} completed\033[0m")
        
    except requests.exceptions.RequestException as e:
        print(f"\033[91m{test_name} failed\033[0m - Network error: {str(e)}")
    except json.JSONDecodeError:
        print(f"\033[91m{test_name} failed\033[0m - Invalid JSON response")
    except KeyError:
        print(f"\033[91m{test_name} failed\033[0m - Unexpected response format")
    except Exception as e:
        print(f"\033[91m{test_name} failed\033[0m - Unexpected error: {str(e)}")
        print(f"Response content: {response.text}")

# Define test cases with their modifications
tests = {
    # "ChangeClothesReal": {
    #     "workflow_path": "ProductionWorkflow/ChangeClothesReal/ChangeClothesRealV1-api.json",
    #     "image_path": "current.jpg",
    #     "modifications": [
    #         {
    #             "path": ["54", "inputs", "image"],
    #             "value": "7.png"
    #         }
    #     ]
    # },
    "HairStyle": {
        "workflow_path": "ProductionWorkflow/HairStyle/HairStyleV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["7", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                "path": ["15", "inputs", "url"],
                "value": "https://imgs.search.brave.com/YVrEvT_H1t4o9c-dUz2KzO-C0VNq37mfJ6db85DFfwY/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pLnBp/bmltZy5jb20vb3Jp/Z2luYWxzL2I1LzEy/LzhmL2I1MTI4ZmY4/MTM5MjEwN2U2MTdk/NjMyN2QzZTMxYmFm/LmpwZw"
            }
        ]
    },
    "AnimeTransform": {
        "workflow_path": "ProductionWorkflow/AnimeTransform/AnimeTransformV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                "path": ["55", "inputs", "url"],
                "value": "https://imgs.search.brave.com/nXZmSaMrB3oLjQ-EQED7gRUoGn2TO5sHCBjdfkdUR-A/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93MC5w/ZWFrcHguY29tL3dh/bGxwYXBlci83NDcv/MzI3L0hELXdhbGxw/YXBlci10YW5qaXJv/LXBpYy1mYW4tYXJ0/LWFuaW1lLWRlbW9u/LXNsYXllci1raW1l/dHN1LW5vLXlhaWJh/LmpwZw"
            }
        ]
    },
    "Elf": {
        "workflow_path": "ProductionWorkflow/Chrismas/ElfV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },

    "Reindeer": {
        "workflow_path": "ProductionWorkflow/Chrismas/ReindeerV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },

    "Santa": {
        "workflow_path": "ProductionWorkflow/Chrismas/SantaV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },

    "Padoru": {
        "workflow_path": "ProductionWorkflow/Chrismas/PadoruV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["3", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },

    "Chrismas": {
        "workflow_path": "ProductionWorkflow/Chrismas/ChrismasV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },

    "DevBase": {
        "workflow_path": "ProductionWorkflow/Base/devbaseV1-api.json",
        "modifications": [
            {
                "path": ["6", "inputs", "text"],
                "value": "An Anime Girl in a desert landscape"  # Can be modified by user
            },
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },
    "MooDeng": {
        "workflow_path": "ProductionWorkflow/MooDeng/MooDengV1-api.json",
        "image_path": "current.jpg",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },

}

# Run tests
for test_name, params in tests.items():
    print(f"\nTesting {test_name}:")
    test_endpoint(**params)