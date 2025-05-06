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

def test_endpoint(test_name, workflow_path, modifications=None, image_path=None):
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
        # Make the API request to /run
        if args.local:
            run_url = "http://localhost:8000/run"
        else:
            run_url = endpoint.rstrip("/") + "/run"
        start_time = time.time()
        response = requests.post(run_url, json=endpoint_body, headers=headers)
        response.raise_for_status()
        print(f"Request sent.")
        save_request_body(test_name, endpoint_body)
        print(f"Saved request body to ready-to-use/{test_name}.json")
        
        # Get job id
        job_data = response.json()
        job_id = job_data.get("id")
        if not job_id:
            print(f"No job id returned: {job_data}")
            return
        print(f"Job ID: {job_id}")

        # Poll for status
        if args.local:
            status_url = f"http://localhost:8000/status/{job_id}"
        else:
            status_url = endpoint.rstrip("/") + f"/status/{job_id}"
        while True:
            time.sleep(20)
            poll_response = requests.get(status_url, headers=headers)
            poll_response.raise_for_status()
            poll_data = poll_response.json()
            status = poll_data.get("status")
            print(f"Status: {status}")
            if status == "COMPLETED":
                end_time = time.time()
                duration = end_time - start_time
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                output = poll_data.get("output", {})
                message = output.get("message", {})
                public_id = message.get("public_id")
                secure_url = message.get("secure_url")
                print(f"Public ID: {public_id}")
                print(f"Secure URL: {secure_url}")
                print(f"Time taken: {minutes}m {seconds}s")
                break
            elif status in ("FAILED", "CANCELLED", "ERROR"):
                print(f"Job failed or cancelled: {poll_data}")
                break
            else:
                print(f"Job not complete yet. Will poll again in 20 seconds...")
    except Exception as e:
        print(f"Exception occurred: {e}")
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
    "LipSync": {
        "workflow_path": "ProductionWorkflow/LipSync/LipSyncV1-api.json",
        "modifications": [
            {
                "path": ["56", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg"
            },
            {
                "path": ["61", "inputs", "url"],
                "value": "https://res.cloudinary.com/prisma-forge/video/upload/v1746338002/comfyui-adae925e-5b5d-491d-bf48-fd6d081245ad-e1.mp3"
            },
            {
                "path": ["64", "inputs", "seed"],
                "value": random.randint(0, 2**16 - 1)
            },
            {
                "path": ["64", "inputs", "inference_steps"],
                "value": 1
            }            
        ]
    },
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
                # User's Speech Audio (CHANGED)
                "path": ["11", "inputs", "url"],
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
        test_endpoint(test_name, **params)
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


