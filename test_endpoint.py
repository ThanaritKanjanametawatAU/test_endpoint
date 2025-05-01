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
        output_message = response_data["output"]["message"]

        def get_extension_from_url(url):
            return os.path.splitext(url.split("?")[0])[1].lower()

        def get_media_type_from_ext(ext):
            if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                return "image"
            elif ext in [".mp3", ".wav", ".ogg", ".flac"]:
                return "audio"
            elif ext in [".mp4", ".mov", ".avi", ".webm"]:
                return "video"
            return None

        # Default values
        file_ext = ".jpg"
        media_type = "image"
        file_data = None

        # Handle Cloudinary dict
        if isinstance(output_message, dict):
            url = output_message.get("secure_url")
            public_id = output_message.get("public_id", "")
            print(f"Generated file URL: {url}")
            print(f"Public ID: {public_id}")
            file_ext = get_extension_from_url(url)
            media_type = get_media_type_from_ext(file_ext)
            response = requests.get(url)
            file_data = response.content

        # Handle direct URL
        elif isinstance(output_message, str) and output_message.startswith(('http://', 'https://')):
            print(f"Generated file URL: {output_message}")
            file_ext = get_extension_from_url(output_message)
            media_type = get_media_type_from_ext(file_ext)
            response = requests.get(output_message)
            file_data = response.content

        # Handle base64
        else:
            print(f"Decoding base64 output")
            try:
                file_data = base64.b64decode(output_message)
                # Try to detect file type from header
                if file_data[:4] == b'\x00\x00\x00\x18' or file_data[4:8] == b'ftyp':
                    file_ext = ".mp4"
                    media_type = "video"
                elif file_data[:4] == b'RIFF' and file_data[8:12] == b'WAVE':
                    file_ext = ".wav"
                    media_type = "audio"
                elif file_data[:3] == b'ID3' or file_data[:2] == b'\xff\xfb':
                    file_ext = ".mp3"
                    media_type = "audio"
                elif file_data[:8] == b'\x89PNG\r\n\x1a\n':
                    file_ext = ".png"
                    media_type = "image"
                elif file_data[:2] == b'\xff\xd8':
                    file_ext = ".jpg"
                    media_type = "image"
                else:
                    # Default to image
                    file_ext = ".jpg"
                    media_type = "image"
            except Exception as e:
                print(f"Failed to decode base64: {e}")
                raise

        # Save file and print location
        output_dir = "local_endpoint_result" if args.local else "runpod_endpoint_result"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/{test_name}{file_ext}"

        if media_type == "image":
            image = Image.open(io.BytesIO(file_data))
            image.save(output_path)
        else:
            with open(output_path, "wb") as f:
                f.write(file_data)

        print(f"{media_type.capitalize()} saved as {output_path}")
        
        
    except Exception as e:
        raise  
        

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
    "SkyreelsA2": {
        "workflow_path": "ProductionWorkflow/SkyreelsA2/SkyreelsA2V1-api.json",
        "modifications": [
            {
                # Subject #1 Image
                "path": ["181", "inputs", "url"],
                    "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745769079/human_uqtgyv.png"
            },
            {
                # Subject #2 Image
                "path": ["182", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745769078/thing_jvwp1d.jpg"
            },
            {
                # Background Image
                "path": ["183", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745769080/env_in4lyb.jpg"
            },
            {
                # Sampling Steps
                "path": ["27", "inputs", "steps"],
                "value": 1
            },
            {
                # Seed
                "path": ["27", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # CFG Scale
                "path": ["27", "inputs", "cfg"],
                "value": 4.0
            },
            {
                # Denoise Strength
                "path": ["27", "inputs", "denoise_strength"],
                "value": 0.92
            },
            {
                # Prompt
                "path": ["16", "inputs", "positive_prompt"],
                "value": "A man walking in the forest with his teddy bear."
            }
            
        ]
    },
    "FishSpeech": {
        "workflow_path": "ProductionWorkflow/FishSpeech/FishSpeechV1-api.json",
        "modifications": [
            {
                # User's Speech Audio
                "path": ["3", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/video/upload/v1745741249/Mimi_Cleaned_cmrhrm.wav"
            },
            {
                # Text That user WANT to speak
                "path": ["4", "inputs", "text"],
                "value": "はじめまして。ミミと申します。\n私は18歳です。東京の渋谷区に住んでいます。趣味は音楽を聴くことと料理をすることです。特に和食を作るのが大好きです。\n現在、東京大学の1年生で、経済学を専攻しています。将来は国際ビジネスの分野で働きたいと考えています。\n小さい頃から英語を勉強していて、今は中国語も勉強し始めました。新しい言語を学ぶことはとても楽しいです。"
            },
            {
                # Text That user spoke
                "path": ["4", "inputs", "prompt_text"],
                "value": "Hey everyone! Sometimes small acts of kindness can make a big difference. A simple smile or helping someone can have a lasting impact. Let's try to be kind today and make our world little better, one small action at a time. Thank you for being here and being part of this."
            },
            {
                "path": ["4", "inputs", "top_p"],
                "value": 0.7
            },
            {
                "path": ["4", "inputs", "repetition_penalty"],
                "value": 1.2
            },
            {
                "path": ["4", "inputs", "temperature"],
                "value": 0.7
            },           
            {
                "path": ["4", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            }
        ]
    },
    "HairStyle": {
        "workflow_path": "ProductionWorkflow/HairStyle/HairStyleV1-api.json",
        "modifications": [
            {
                "path": ["7", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                "path": ["15", "inputs", "url"],
                "value": "https://imgs.search.brave.com/YVrEvT_H1t4o9c-dUz2KzO-C0VNq37mfJ6db85DFfwY/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9pLnBp/bmltZy5jb20vb3Jp/Z2luYWxzL2I1LzEy/LzhmL2I1MTI4ZmY4/MTM5MjEwN2U2MTdk/NjMyN2QzZTMxYmFm/LmpwZw"
            },
            {
                # User's Image
                "path": ["82", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }
        ]
    },
    "AnimeTransform": {
        "workflow_path": "ProductionWorkflow/AnimeTransform/AnimeTransformV1-api.json",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                "path": ["55", "inputs", "url"],
                "value": "https://imgs.search.brave.com/nXZmSaMrB3oLjQ-EQED7gRUoGn2TO5sHCBjdfkdUR-A/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93MC5w/ZWFrcHguY29tL3dh/bGxwYXBlci83NDcv/MzI3L0hELXdhbGxw/YXBlci10YW5qaXJv/LXBpYy1mYW4tYXJ0/LWFuaW1lLWRlbW9u/LXNsYXllci1raW1l/dHN1LW5vLXlhaWJh/LmpwZw"
            },
            {
                # User's Image
                "path": ["56", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }
        ]
    },
    "Elf": {
        "workflow_path": "ProductionWorkflow/Chrismas/Elf/ElfV1-api.json",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # User's Image
                "path": ["55", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }
        ]
    },

    "Reindeer": {
        "workflow_path": "ProductionWorkflow/Chrismas/Reindeer/ReindeerV1-api.json",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # User's Image
                "path": ["55", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }
        ]
    },

    "Santa": {
        "workflow_path": "ProductionWorkflow/Chrismas/Santa/SantaV1-api.json",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # User's Image
                "path": ["55", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }
        ]
    },

    "Padoru": {
        "workflow_path": "ProductionWorkflow/Chrismas/Padoru/PadoruV1-api.json",
        "modifications": [
            {
                "path": ["3", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # User's Image
                "path": ["61", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }  
        ]
    },

    "Chrismas": {
        "workflow_path": "ProductionWorkflow/Chrismas/Chrismas/ChrismasV1-api.json",
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # User's Image
                "path": ["55", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }
        ]
    },

    "DevBase": {
        "workflow_path": "ProductionWorkflow/BasicPrompt/BasicPromptV1-api.json",
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
        "modifications": [
            {
                "path": ["25", "inputs", "noise_seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # User's Image
                "path": ["44", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            }
        ]
    },

}

tests = {
    "SkyreelsA2": {
        "workflow_path": "ProductionWorkflow/SkyreelsA2/SkyreelsA2V1-api.json",
        "modifications": [
            {
                # Subject #1 Image
                "path": ["181", "inputs", "url"],
                    "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745769079/human_uqtgyv.png"
            },
            {
                # Subject #2 Image
                "path": ["182", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745769078/thing_jvwp1d.jpg"
            },
            {
                # Background Image
                "path": ["183", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745769080/env_in4lyb.jpg"
            },
            {
                # Sampling Steps
                "path": ["27", "inputs", "steps"],
                "value": 1
            },
            {
                # Seed
                "path": ["27", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                # CFG Scale
                "path": ["27", "inputs", "cfg"],
                "value": 4.0
            },
            {
                # Denoise Strength
                "path": ["27", "inputs", "denoise_strength"],
                "value": 0.92
            },
            {
                # Prompt
                "path": ["16", "inputs", "positive_prompt"],
                "value": "A man walking in the forest with his teddy bear."
            }
            
        ]
    
    }
}

# Track test results
test_results = {
    "passed": 0,
    "failed": 0,
    "failed_tests": []
}

# Run tests
for test_name, params in tests.items():
    print(f"\nTesting {test_name}:")
    try:
        test_endpoint(**params)
        test_results["passed"] += 1
        print(f"\033[92m{test_name} completed\033[0m")
    except requests.exceptions.RequestException as e:
        test_results["failed"] += 1
        test_results["failed_tests"].append((test_name, f"Network error: {str(e)}"))
        print(f"\033[91m{test_name} failed\033[0m - Network error: {str(e)}")
    except json.JSONDecodeError:
        test_results["failed"] += 1
        test_results["failed_tests"].append((test_name, "Invalid JSON response"))
        print(f"\033[91m{test_name} failed\033[0m - Invalid JSON response")
    except KeyError:
        test_results["failed"] += 1
        test_results["failed_tests"].append((test_name, "Unexpected response format"))
        print(f"\033[91m{test_name} failed\033[0m - Unexpected response format")
    except Exception as e:
        test_results["failed"] += 1
        test_results["failed_tests"].append((test_name, f"Unexpected error: {str(e)}"))
        print(f"\033[91m{test_name} failed\033[0m - Unexpected error: {str(e)}")
        if 'response' in locals():
            print(f"Response content: {response.text}")

# Print summary
print("\nTest Summary:")
print(f"Total tests: {len(tests)}")
print(f"Passed: {test_results['passed']}")
print(f"Failed: {test_results['failed']}")
if test_results["failed"] > 0:
    print("\nFailed tests:")
    for test_name, error in test_results["failed_tests"]:
        print(f"- {test_name}: {error}")


