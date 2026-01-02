from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import re

app = FastAPI(title="BLIP Image Tagging Service")

# ✅ Allow frontend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later if needed
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load BLIP once at startup
processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)

STOPWORDS = {
    "a", "an", "the", "of", "with", "and",
    "in", "on", "at", "for", "to"
}

def caption_to_tags(caption, max_tags=6):
    words = re.findall(r"[a-z]+", caption.lower())
    tags = [w for w in words if w not in STOPWORDS]
    return sorted(set(tags))[:max_tags]


@app.post("/image-to-tags")
async def image_to_tags(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    inputs = processor(image, return_tensors="pt")
    output = model.generate(**inputs, max_length=30)

    caption = processor.decode(
        output[0], skip_special_tokens=True
    )

    tags = caption_to_tags(caption)

    return {
        "tags": tags
    }
