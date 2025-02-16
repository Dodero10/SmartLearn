import asyncio
import os
import sys
import time

from chat_query.question_type import QuestionType
from utils.database_manage import DatabaseManager


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

                collected_result = ""
                for chunk in client.query_from_chatgpt(question=question, info=document):
                    collected_result += chunk
                    yield chunk
                
                if "Không tìm thấy dữ liệu về câu hỏi." in collected_result:
                    print("No data found, generating relevant questions")
                    yield "\n"
                    for chunk in client.query_relevant_question(question=question, info=document):
                        yield chunk

            except Exception as err:
                print(f"Error in knowledge processing: {str(err)}")
                yield f'Error processing question: {str(err)}'
        else:
            print("Processing greeting")
            answer = client.query_greeting(question=question)
            yield answer
            
    except Exception as e:
        print(f"Error in main query function: {str(e)}")
        yield f"Error in query: {str(e)}"
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



