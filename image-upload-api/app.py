from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import oci
import uuid
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OCI config (works inside OCI VM)
config = oci.config.from_file("~/.oci/config", "DEFAULT")

object_storage = oci.object_storage.ObjectStorageClient(config)

NAMESPACE = object_storage.get_namespace().data
BUCKET_NAME = os.environ.get("OCI_BUCKET_NAME", "fake-news-buster")


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    object_name = f"{uuid.uuid4()}.{ext}"

    content = await file.read()

    object_storage.put_object(
        namespace_name=NAMESPACE,
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        put_object_body=content,
        content_type=file.content_type
    )

    public_url = (
        f"https://objectstorage.{config['region']}.oraclecloud.com"
        f"/n/{NAMESPACE}/b/{BUCKET_NAME}/o/{object_name}"
    )

    return {
        "image_url": public_url
    }
