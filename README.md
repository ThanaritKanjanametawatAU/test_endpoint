# Repository For Testing Runpod API
First put these into your .env file
```
RUNPOD_ENDPOINT=
RUNPOD_BEARER_TOKEN=
```

Then set the environment variables
```
set -a && source .env && set +a
```

To run python code, you need to install the dependencies

[Optional] Create Virtual Environment
```
python -m venv venv && source venv/bin/activate
```

Install the dependencies
```
pip install -r requirements.txt
```

Run Test Endpoint
```
python test_endpoint.py
```

Run Test Local Endpoint
```
python test_local_endpoint.py
```

or 
```
python test_endpoint.py --local true
```


# Formats

Note: The V1-api in the ProductionWorkflow folder is only the "workflow", not the body of the whole thing we send to endpoint. The Whole Format is like this

## Format #1: No Image

```
endpoint_body = 
{
    "input": {
        "workflow": (load workflow-api.json)
        }
}
```



## Format #2: With Image

If the workflow requires an image, base64 is required to be put like this.

```
endpoint_body = 
{
    "input": {
        "workflow": (load workflow-api.json)
        },
    "images": [
        {
            "name": "current.jpg",
            "image": (base64 of image)
        }
    ]
}
```

Note: Will support image link in the future


Each workflow-api.json will require some modification for the user to input their own prompt, random seed, etc.
So modify it first before putting it in the endpoint_body.


<br><br><br><br>
Here are what should be modified (I'll inform when this is changed in the future)

# Workflow #1: Base (Format #1)

1.1 Modify this for the user's prompt 
```
workflowAPI["6"]["inputs"]["text"]
```


<br>

1.2 Randomize this for different results

```
workflowAPI["25"]["inputs"]["noise_seed"]
```

<br><br>

# Workflow #2: MooDeng (Format #2)

2.1 [Optional], Don't have to modify this for now.
```
 workflowAPI["6"]["inputs"]["text"]
```


<br>

2.2 Randomize this for different results

```
workflowAPI["25"]["inputs"]["noise_seed"]
```

<br>

and only then, put this workflow and base64 image into the endpoint_body

<br><br>

# Workflow #3: Chrismas, Reindeer, Santa, Elf (Format #2)

3.1 [Optional] Don't have to modify this for now.
```
workflowAPI["6"]["inputs"]["text"]
```

<br>

3.2 Randomize this for different results
```
workflowAPI["25"]["inputs"]["noise_seed"]
```

<br>
and only then, put this workflow and base64 image into the endpoint_body

<br><br>

# Workflow #4: Padoru (Format #2)

3.1 Randomize this for different results
```
workflowAPI["3"]["inputs"]["seed"]
```

<br><br>

# Workflow #5: Anime Transform (Format #2)

5.1 [Optional] Modify this for the user's prompt (To describe the specific details of the result image)
```
workflowAPI["6"]["inputs"]["text"]
```

5.2 Randomize this for different results
```
workflowAPI["25"]["inputs"]["noise_seed"]
```

<br>

5.3 Put any **Image Address Online** into this, example link down below (Reference image for the Transformation)
```
workflowAPI["55"]["inputs"]["url"] = https://imgs.search.brave.com/nXZmSaMrB3oLjQ-EQED7gRUoGn2TO5sHCBjdfkdUR-A/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly93MC5w/ZWFrcHguY29tL3dh/bGxwYXBlci83NDcv/MzI3L0hELXdhbGxw/YXBlci10YW5qaXJv/LXBpYy1mYW4tYXJ0/LWFuaW1lLWRlbW9u/LXNsYXllci1raW1l/dHN1LW5vLXlhaWJh/LmpwZw 
```

<br><br>



# Workflow #6: Hair Style (Format #2)

6.1 Modify the Seed for different results
```
workflowAPI["7"]["inputs"]["seed"]
```

<br>

6.2 Put any **Image Address Online** into this, example link down below (Reference for the Hair Style, must be an image of a clear straight face)
```
workflowAPI["15"]["inputs"]["url"]
```












