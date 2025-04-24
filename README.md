# Repository For Testing Runpod API

<b>For a quick start in testing the endpoint in Postman, you can use the requests in ready-to-use folder as the body of the request.</b>

# Setup
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
python -m venv .venv && source .venv/bin/activate
```

Install the dependencies
```
pip install -r requirements.txt
```

Run Test Endpoint
```
python test_endpoint.py
```

Run Test Local Endpoint ( For Local Container Development Only)
```
python test_endpoint.py --local True
```

# How It Works

The script works by loading workflow JSON files and applying specified modifications before sending them to the Runpod endpoint. 

Input and output images are now handled via URLs instead of base64 encoding, making the process more efficient.

Each workflow requires specific modifications for customization:

## Workflow #1: DevBase (Basic Prompt, No Input Image)

1. Modify the prompt text:
```
["6", "inputs", "text"] = "Your custom prompt here"
```

2. Randomize for different results:
```
["25", "inputs", "noise_seed"] = random value
```

## Workflow #2: MooDeng (Requires Input Image)

1. Randomize for different results:
```
["25", "inputs", "noise_seed"] = random value
```

2. Set the input image URL:
```
["44", "inputs", "url"] = "https://your-image-url.jpg"
```

## Workflow #3: Christmas Themed (Requires Input Image)

Available variants: Christmas, Reindeer, Santa, Elf

1. Randomize for different results:
```
["25", "inputs", "noise_seed"] = random value
```

2. Set the input image URL:
```
["55", "inputs", "url"] = "https://your-image-url.jpg"
```

### Image References:
- Christmas: https://res.cloudinary.com/prisma-forge/image/upload/v1745416525/ChrismasSuit_rkh8tj.png
- Santa: https://res.cloudinary.com/prisma-forge/image/upload/v1745416525/santa_zogqfd.png
- Elf: https://res.cloudinary.com/prisma-forge/image/upload/v1745416525/elf_rg7had.png
- Reindeer: https://res.cloudinary.com/prisma-forge/image/upload/v1745416525/reindeer_kh57gc.png

## Workflow #4: Padoru (Requires Input Image)

1. Randomize for different results:
```
["3", "inputs", "seed"] = random value
```

2. Set the input image URL:
```
["61", "inputs", "url"] = "https://your-image-url.jpg"
```

Reference image: https://res.cloudinary.com/prisma-forge/image/upload/v1745416525/padoru_kc8d6h.png

## Workflow #5: Anime Transform (Requires Input Image)

1. [Optional] Modify the prompt for custom details:
```
["6", "inputs", "text"] = "Your custom prompt here"
```

2. Randomize for different results:
```
["25", "inputs", "noise_seed"] = random value
```

3. Set the reference style image URL:
```
["55", "inputs", "url"] = "https://example.com/anime-style-reference.jpg"
```

4. Set the input image URL:
```
["56", "inputs", "url"] = "https://your-image-url.jpg"
```

Reference style examples:
- https://w0.peakpx.com/wallpaper/747/327/HD-wallpaper-tanjiro-pic-fan-art-anime-demon-slayer-kimetsu-no-yaiba.jpg
- https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/64a25159-0d78-46cb-9b15-5216894c4ddb/dhkmle5-dc2fffca-11d6-4003-bd2c-d37c08dd4ef5.png/v1/fill/w_776,h_1030,q_70,strp/jujutsu_kaisen___gojo_satoru_by_a1nime_dhkmle5-pre.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9MTcwMCIsInBhdGgiOiJcL2ZcLzY0YTI1MTU5LTBkNzgtNDZjYi05YjE1LTUyMTY4OTRjNGRkYlwvZGhrbWxlNS1kYzJmZmZjYS0xMWQ2LTQwMDMtYmQyYy1kMzdjMDhkZDRlZjUucG5nIiwid2lkdGgiOiI8PTEyODAifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6aW1hZ2Uub3BlcmF0aW9ucyJdfQ.RIC_CCyGDLvZqp52ka_GzXTxr2yN0H7FhYfpHRtDzg0

## Workflow #6: Hair Style (Requires Input Image)

1. Randomize for different results:
```
["7", "inputs", "seed"] = random value
```

2. Set the reference hairstyle image URL (must be a clear straight face):
```
["15", "inputs", "url"] = "https://example.com/hairstyle-reference.jpg"
```

3. Set the input image URL:
```
["82", "inputs", "url"] = "https://your-image-url.jpg"
```

Reference hairstyle examples:
- https://i.imgur.com/6IU2ei9.jpeg
- https://i.imgur.com/TjtVYfa.png
- https://i.imgur.com/LRqiRgw.png
- https://i.imgur.com/6wA0mb4.png
- https://i.imgur.com/VQRaWCl.png
- https://i.imgur.com/9aSpX8O.png

# Default Test Input Image
The script uses this image as the default input:
https://res.cloudinary.com/prisma-forge/image/upload/v1745308700/current_enebuf.jpg










