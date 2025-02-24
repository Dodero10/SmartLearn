import os

CUR_DIRECTORY = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
SRC_DIRECTORY = os.path.dirname(CUR_DIRECTORY)
DB_DIRECTORY = SRC_DIRECTORY + "/chromadb"

BUCKET_NAME = "files"
BUCKET_NAME_SLIDE = "slides"
BUCKET_NAME_METADATA = "metadata"
BUCKET_NAME_SCRIPTS = "scripts"
BUCKET_NAME_AUDIO = "audios"
BUCKET_NAME_VIDEO = "videos"
