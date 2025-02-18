import asyncio
import os
import re
import sys
import time

from chat_query.question_type import QuestionType
from utils.database_manage import DatabaseManager


def split_vietnamese_text(text):
    """Tách text tiếng Việt thành các từ có nghĩa"""
    # Tách theo dấu câu và khoảng trắng
    words = []
    # Tách câu trước
    sentences = re.split(r'([.!?]+)', text)
    for sentence in sentences:
        # Tách từ trong mỗi câu
        if sentence.strip():
            # Tách theo khoảng trắng nhưng giữ nguyên dấu câu
            if re.match(r'[.!?]+', sentence):
                words.append(sentence)
            else:
                words.extend(sentence.strip().split())
    return words

def query(question: str):
    print("Starting query function")
    client = QuestionType()
    try:
        question_type = client.question_classification(question=question)
        print(f"Question type: {question_type}")
        
        if question_type == "true":
            try:
                print("Processing knowledge question")
                document_query = client.get_document_query(question)
                print(f"Document query: {document_query}")
                
                database_manager = DatabaseManager()
                print("Querying database")
                document = database_manager.query_collection(questions=document_query)
                print(f"Database response length: {len(document) if document else 0}")

                # Xử lý câu trả lời từ chatgpt
                response_text = ""
                for chunk in client.query_from_chatgpt(question=question, info=document):
                    response_text += chunk

                # Tách response thành các từ và xử lý
                words = response_text.split()
                for i, word in enumerate(words):
                    # Trả về từng ký tự của từ
                    for char in word:
                        yield char
                        time.sleep(0.001)
                    # Thêm khoảng trắng sau mỗi từ (trừ từ cuối cùng)
                    if i < len(words) - 1:
                        yield " "
                        time.sleep(0.001)
                
                # Kiểm tra nếu không có dữ liệu
                if "Không tìm thấy dữ liệu về câu hỏi" in response_text:
                    print("No data found, generating relevant questions")
                    yield "\n"
                    relevant_text = ""
                    for chunk in client.query_relevant_question(question=question, info=document):
                        relevant_text += chunk
                    
                    # Tách relevant text thành các từ và xử lý
                    words = relevant_text.split()
                    for i, word in enumerate(words):
                        # Trả về từng ký tự của từ
                        for char in word:
                            yield char
                            time.sleep(0.01)
                        # Thêm khoảng trắng sau mỗi từ (trừ từ cuối cùng)
                        if i < len(words) - 1:
                            yield " "
                            time.sleep(0.01)

            except Exception as err:
                print(f"Error in knowledge processing: {str(err)}")
                error_msg = f'Error processing question: {str(err)}'
                words = error_msg.split()
                for i, word in enumerate(words):
                    for char in word:
                        yield char
                        time.sleep(0.01)
                    if i < len(words) - 1:
                        yield " "
                        time.sleep(0.01)
        else:
            print("Processing greeting")
            answer = client.query_greeting(question=question)
            words = answer.split()
            for i, word in enumerate(words):
                for char in word:
                    yield char
                    time.sleep(0.01)
                if i < len(words) - 1:
                    yield " "
                    time.sleep(0.01)
            
    except Exception as e:
        print(f"Error in main query function: {str(e)}")
        error_msg = f"Error in query: {str(e)}"
        words = error_msg.split()
        for i, word in enumerate(words):
            for char in word:
                yield char
                time.sleep(0.01)
            if i < len(words) - 1:
                yield " "
                time.sleep(0.01)

def gen_quiz(filenames:list[str]):
    client = QuestionType()
    content=[]
    quizzs=[]
    database_manager = DatabaseManager()
    for filename in filenames:
        collection=database_manager.collection.get(where={"filename":filename})
        content.extend(collection['documents'])
    for cont in content:
        quizz=client.gen_question(cont)
     
        if not quizz  or not isinstance(quizz, list):
            continue

        if any("error" in q for q in quizz):
            continue

        
        quizzs.extend(quizz)  

    return quizzs    



