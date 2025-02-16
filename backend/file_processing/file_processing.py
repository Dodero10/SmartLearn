from utils.parse_data import ParseHandler
from utils.chunking import Chunking
import os
import typing as tp
import copy

api_key = os.environ["OPENAI_API_KEY"]

def parsing(file_stream, pdf_path):
    parsehandler = ParseHandler.get_instance(api_key=api_key)
    image_base64s = parsehandler.pdf_to_images(file_stream, pdf_path)
    content= parsehandler.parse_pdf(image_base64s, pdf_path)
    return content

def chunking(content,filename):
    chunkhandler = Chunking()
    data, metadata, ids=chunkhandler.chunking_documents(content,filename)
    return  data, metadata, ids
