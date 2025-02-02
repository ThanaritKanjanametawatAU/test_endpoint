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
workflowAPI["55"]["inputs"]["url"] = https://w0.peakpx.com/wallpaper/747/327/HD-wallpaper-tanjiro-pic-fan-art-anime-demon-slayer-kimetsu-no-yaiba.jpg
```

List of Image Address Online (May Have Copyright Issues, Beware):
- https://w0.peakpx.com/wallpaper/747/327/HD-wallpaper-tanjiro-pic-fan-art-anime-demon-slayer-kimetsu-no-yaiba.jpg
- https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/64a25159-0d78-46cb-9b15-5216894c4ddb/dhkmle5-dc2fffca-11d6-4003-bd2c-d37c08dd4ef5.png/v1/fill/w_776,h_1030,q_70,strp/jujutsu_kaisen___gojo_satoru_by_a1nime_dhkmle5-pre.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTcwMCIsInBhdGgiOiJcL2ZcLzY0YTI1MTU5LTBkNzgtNDZjYi05YjE1LTUyMTY4OTRjNGRkYlwvZGhrbWxlNS1kYzJmZmZjYS0xMWQ2LTQwMDMtYmQyYy1kMzdjMDhkZDRlZjUucG5nIiwid2lkdGgiOiI8PTEyODAifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6aW1hZ2Uub3BlcmF0aW9ucyJdfQ.RIC_CCyGDLvZqp52ka_GzXTxr2yN0H7FhYfpHRtDzg0
<br><br>



# Workflow #6: Hair Style (Format #2)

6.1 Modify the Seed for different results
```
workflowAPI["7"]["inputs"]["seed"]
```

<br>

6.2 Put any **Image Address Online** into this, example link down below (Reference for the Hair Style, **must be an image of a clear straight face**)
```
workflowAPI["15"]["inputs"]["url"]
```

List of Image Address Online (May Have Copyright Issues, Beware):
- https://i.imgur.com/6IU2ei9.jpeg
- https://i.imgur.com/TjtVYfa.png
- https://i.imgur.com/LRqiRgw.png
- https://i.imgur.com/6wA0mb4.png
- https://i.imgur.com/VQRaWCl.png
- https://i.imgur.com/9aSpX8O.png










