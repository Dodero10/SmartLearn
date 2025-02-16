import os
import sys
import time
import asyncio
from chat_query.question_type import QuestionType
from utils.database_manage import DatabaseManager

def query(question: str):
    client = QuestionType()
    try:
        question_type = client.question_classification(question=question)
        if question_type == "true":

            try:

                document_query = client.get_document_query(question)
              
                database_manager = DatabaseManager()

                document = database_manager.query_collection(questions=document_query)

                collected_result = ""
                for chunk in client.query_from_chatgpt(question=question, info=document):
                    collected_result += chunk
                    yield chunk
              
                if "Không tìm thấy dữ liệu về câu hỏi." in collected_result:
                  
                    yield "\n"
                    for chunk in client.query_relevant_question(question=question, info=document):
                        yield chunk

            except Exception as err:
                yield f'Error format from answer: {err}'
        else:
            answer = client.query_greeting(question=question)
            yield answer
            
    except Exception as e:
        yield f"Error when query: {e}"
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



