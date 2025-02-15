import os
import sys

from datetime import datetime
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunking:
    def __init__(self, context="Trả lời bằng tiếng việt, đưa ra một đoạn tổng hợp ngắn."):
        # Load environment variables
        load_dotenv()
        self.open_api_key = os.environ.get('OPENAI_API_KEY')
        self.context = context
        self.chunk_size = int(os.environ.get('CHUNK_SIZE'))
        self.chunk_overlap = int(os.environ.get('CHUNK_OVERLAP'))

    def chunking_documents(self, document,filename):
        """Read and split a Markdown document, then summarize each section."""
        data = []
        metadata = []

        
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"), ("####", "Header 4")]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(document)

        text_splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\n\n",
                "\n",
                ".",
            ],
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        splits = text_splitter.split_documents(md_header_splits)
        for md_header_split in splits:
            md_header_split.metadata["filename"]=filename
        for md_header_split in splits:
            content = md_header_split.page_content
            mts = md_header_split.metadata
            for document in md_header_splits:
                text = document.page_content
                if content in text:
                    mts['raw_text'] = text
                    break
            header_order = ["Header 4", "Header 3", "Header 2", "Header 1"]

            for header in header_order:
                for item in mts:
                    if header == item:
                        content = f"Tiêu đề: {mts[item]} có nội dung là: {content}"

            content = f"Tài liệu {filename} có nội dung là: {content}"
            # summary_content = self._get_summary(content=content)
            content_with_summary = f"{content}"

            data.append(content_with_summary)
            # mts['summary'] = summary_content

            metadata.append(mts)
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        ids = [f"{current_time}_{i}" for i in range(1, len(data) + 1)]
        print(ids)
        return data, metadata, ids

