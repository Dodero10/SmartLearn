import os

CUR_DIRECTORY = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
SRC_DIRECTORY = os.path.dirname(CUR_DIRECTORY)
DB_DIRECTORY = SRC_DIRECTORY + "/chromadb"
