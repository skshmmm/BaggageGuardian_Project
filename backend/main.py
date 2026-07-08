# backend/main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from damage_service import read_imagefile_to_cv2, analyze_all_images

app = FastAPI(
    title="Baggage Guardian API",
    description="YOLOv8 + OpenCV hybrid damage verification",
    version="0.1.0",
)

# CORS for your React frontend (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze")
async def analyze_baggage(
    pre_image: UploadFile = File(...),
    post_images: List[UploadFile] = File(...),
):
    """
    pre_image: single baseline photo (before flight)
    post_images: list of photos after flight
    """

    # Read pre image
    pre_bytes = await pre_image.read()
    pre_img = read_imagefile_to_cv2(pre_bytes)

    # Read all post images
    post_imgs = []
    post_filenames = []
    for f in post_images:
        bytes_ = await f.read()
        post_imgs.append(read_imagefile_to_cv2(bytes_))
        post_filenames.append(f.filename)

    # Run hybrid analysis
    agg = analyze_all_images(pre_img, post_imgs)

    # Build response with filenames for frontend
    images_out = []
    for idx, (res, fname) in enumerate(zip(agg["images"], post_filenames)):
        images_out.append(
            {
                "image_index": idx,
                "filename": fname,
                "image_width": res["image_width"],
                "image_height": res["image_height"],
                "image_severity": res["image_severity"],
                "detections": res["detections"],
                "used_fallback": res["used_fallback"],
            }
        )

    return {
        "global_severity": agg["global_severity"],      # "low"/"medium"/"high"/"none"
        "primary_image_index": agg["primary_image_index"],
        "images": images_out,
    }
