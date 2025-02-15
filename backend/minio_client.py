from minio import Minio
import os
minio_client = Minio(
    "minio:9000",
    access_key=os.environ["ACCESS_KEY"],
    secret_key=os.environ["SECRET_KEY"],
    secure=False,
)
bucket_name = "files"

if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)