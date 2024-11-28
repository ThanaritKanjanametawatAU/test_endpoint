# Repository For Testing Runpod API
First put these into your .env file
```
RUNPOD_ENDPOINT=
RUNPOD_BEARER_TOKEN=
```

To run python code, you need to install the dependencies
```
pip install requests io pillow base64 json random time
```

and then set temporary environment variables
```
set -a; source .env; set +a;
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

# Workflow #3: Chrismas (Format #2)

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






