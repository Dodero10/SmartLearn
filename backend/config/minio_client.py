from minio import Minio
import os
minio_client = Minio(
    "minio:9000",
    access_key=os.environ["ACCESS_KEY"],
    secret_key=os.environ["SECRET_KEY"],
    secure=False,
)

bucket_name = "files"
bucket_name_slide = "slides"
bucket_name_video = "videos"
bucket_name_audio = "audios"
bucket_name_script = "scripts"

if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

if not minio_client.bucket_exists(bucket_name_slide):
    minio_client.make_bucket(bucket_name_slide)

if not minio_client.bucket_exists(bucket_name_video):
    minio_client.make_bucket(bucket_name_video)

if not minio_client.bucket_exists(bucket_name_audio):
    minio_client.make_bucket(bucket_name_audio)

if not minio_client.bucket_exists(bucket_name_script):
    minio_client.make_bucket(bucket_name_script)
