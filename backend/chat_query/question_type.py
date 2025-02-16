import os
import sys
import json
from utils.gpt_call import ChatGPTGen


def create_message(system_contents: str, user_contents: str, histories=None):
    messages = [{
        "role": "system",
        "content": [{"type": "text",
                     "text": f'{system_contents}'}]
    }]
    if histories:
        for history in histories:
            messages.append({
                "role": history["role"],
                "content": [{'type': "text",
                             "text": history['content']}]
            })

    messages.append({
        "role": "user",
        "content": [{"type": "text",
                     "text": f'{user_contents}'}]
    })
    return messages


class QuestionType:
    def __init__(self):
        self.client = ChatGPTGen()

    def question_classification(self, question: str) -> str:
        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ giáo dục.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến kiến thức học tập trong các môn học khác nhau.\n"
            "3. Đọc câu hỏi mà tôi đưa ra.\n"
            "4. Xác định xem câu hỏi đó có phải là câu chào hỏi thông thường (để làm quen, giới thiệu) hay không.\n"
            "5. Nếu là câu chào hỏi thông thường, hãy trả lời là 'false'.\n"
            "6. Nếu là câu hỏi về kiến thức học tập, hãy trả về 'true'.\n"
            "7. Chỉ trả lời là 'true' hoặc 'false'.\n"
            "8. Không được thêm thông tin gì ngoài ngữ cảnh tôi cung cấp.\n"
            "9. Ví dụ:\n"
            "   - 'Xin chào, bạn có khỏe không?' -> 'false'\n"
            "   - 'Định lý Pythagoras là gì?' -> 'true'\n"
            "   - 'Hôm nay thời tiết thế nào?' -> 'false'\n"
            "   - 'Ai là người phát minh ra bóng đèn?' -> 'true'"
        )

        messages = create_message(system_contents, user_contents=question)
        return self.client.default_chat_completion(messages)

    def improve_question(self, question: str) -> str:
        system_contents =  (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ giáo dục.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến kiến thức học tập trong các môn học khác nhau.\n"
            "3. Tóm tắt câu hỏi được đưa ra.\n"
            "4. Đưa ra chủ đề chính mà câu hỏi đề cập đến.\n"
            "5. Trả kết quả về dạng json chứa hai đối tượng là summary và topic, tương ứng với 3 và 4.\n"
            "6. Chỉ đưa ra nội dung tôi yêu cầu, không trả lời gì thêm.\n"
            "7. Không được thêm thông tin gì ngoài ngữ cảnh tôi cung cấp.\n"
            "8. Ví dụ về câu trả lời: {'summary': 'Giải thích định lý Pythagoras.', 'topic': 'Định lý Pythagoras'}"
        )
        messages = create_message(system_contents, user_contents=question)
        return self.client.default_chat_completion(messages)

    def query_greeting(self, question: str) -> str:
        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ giáo dục.\n"
            "2. Bạn được xây dựng bởi team AI.\n"
            "3. Bạn được xây dựng để trả lời các câu hỏi liên quan đến kiến thức học tập trong các môn học khác nhau.\n"
            "4. Đứng trên các vai trò trên, bạn hãy trả lời câu chào hỏi dưới đây khi người dùng gặp bạn.\n"
            "5. Trả lời bằng tiếng Việt."
        )

        messages = create_message(system_contents, user_contents=question)
        return self.client.default_chat_completion(messages)

    def query_relevant_question(self, question: str, info):
        """
            Struct of histories: a array of question and answer of system.
            Example: histories=[
                        {"role": "user", "content": "message 1 content."},
                        {"role": "assistant", "content": "message 2 content"},
                        {"role": "user", "content": "message 3 content"},
                        {"role": "assistant", "content": "message 4 content."},
                        {"role": "user", "content": "message 5 content."}
                         ],
            """

        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ giáo dục.\n"
            "2. Bạn được xây dựng bởi team AI.\n"
            "3. Bạn được xây dựng để trả lời các câu hỏi liên quan đến kiến thức học tập trong các môn học khác nhau.\n"
            "4. Trả lời bằng tiếng Việt.\n"
            "5. Đọc câu hỏi của user và thông tin được cung cấp.\n"
            "6. Từ thông tin được cung cấp, chọn ra 3 thông tin bạn cho là 'Gần nhất' với câu hỏi.\n"
            "7. Từ 3 thông tin đấy sinh ra ba câu hỏi có liên quan và câu trả lời tương ứng theo nội dung bạn đã chọn.\n"
            "8. Trả về các câu hỏi, câu trả lời trên theo thứ tự 1,2,3 dưới dạng Câu hỏi:'abc?', 'Câu trả lời':'xyz'.\n"
            "9. Không được trả về các thông tin không có trong nội dung được tôi cung cấp.\n"
            "10. Không trả lời lại câu hỏi đã cho."

        )
        user_contents = f' Câu hỏi: {question}, Thông tin liên quan:{info}'
        messages = create_message(system_contents, user_contents)

        for chunk in self.client.stream_chat_completion(messages):
            yield chunk

    def get_summary(self, content):
        """Summarize the content using OpenAI's API."""

        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ giáo dục.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến kiến thức học tập trong các môn học khác nhau.\n"
            "3. Đọc nội dung được tôi cung cấp và mô tả ngắn gọn lại nội dung đó.\n"
            "4. Bạn không được cung cấp thông tin gì thêm ngoài ngữ cảnh mà tôi cung cấp."
        )
        user_content = f'Mô tả ngắn gọn nội dung sau, ngoài ra không trả lời gì thêm: {content}'
        messages = create_message(system_contents, user_content)
        return self.client.default_chat_completion(messages)

    def hyDE_improve(self, question: str):
        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ giáo dục.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến kiến thức học tập trong các môn học khác nhau.\n"
            "3. Đọc câu hỏi được đưa ra.\n"
            "4. Viết một đoạn văn trả lời cho câu hỏi đó.\n"
            "5. Trả về đoạn văn chứa câu trả lời, ngoài ra không được đưa ra thêm bất kỳ thông tin gì.\n"
            "6. Trả lời bằng tiếng Việt."
        )
        messages = create_message(system_contents, question)
        return self.client.default_chat_completion(messages, token_output=150)

    
    def query_from_chatgpt(self, question: str, info, histories=None):
        """
            Struct of histories: a array of question and answer of system.
            Example: histories=[
                        {"role": "user", "content": "message 1 content."},
                        {"role": "assistant", "content": "message 2 content"},
                        {"role": "user", "content": "message 3 content"},
                        {"role": "assistant", "content": "message 4 content."},
                        {"role": "user", "content": "message 5 content."}
                         ],
            """
        systemt_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ giáo dục.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến kiến thức học tập trong các môn học khác nhau.\n"
            "3. Trả lời bằng tiếng Việt.\n"
            "4. Đọc câu hỏi của user và câu trả lời của assistant được cung cấp.\n"
            "5. Đọc câu hỏi được đưa ra. Trả lời câu hỏi của user, dựa trên câu hỏi của user, câu trả lời của assistant trước đó và thông tin được cung cấp ngay phía sau câu hỏi.\n"
            "6. Nếu tìm thấy dữ liệu có liên quan đến câu hỏi, dù ít hay nhiều thì đưa ra câu trả lời tương ứng.\n"
            "7. Nếu không tìm thấy dữ liệu cho câu hỏi thì trả về 'Không tìm thấy dữ liệu về câu hỏi.'.\n"
            "8. Không được trả về thông tin không có trong nội dung mà tôi không cung cấp."

        )

        user_contents = f' Câu hỏi: {question}, Thông tin liên quan:{info}'
        messages = create_message(systemt_contents, user_contents, histories)
        for chunk in self.client.stream_chat_completion(messages):
            yield chunk

    def get_document_query(self, question):
        document_query = []
        hypothetical_document = self.hyDE_improve(question)
        document_query.append(hypothetical_document)

        question_context = self.improve_question(question=question)
        question_context = question_context.replace("'", '"')
        question_context = json.loads(question_context)
        document_query.append(question_context['summary'])
        document_query.append(question_context['item'])
        return document_query
    def gen_question(self,content):
        systemt_contents=  f"""
            Bạn là một trợ lý AI chuyên tạo câu hỏi trắc nghiệm từ văn bản. 
            Nhiệm vụ của bạn là đọc đoạn văn sau và tạo ra **nhiều câu hỏi trắc nghiệm** với **4 lựa chọn trả lời**, trong đó chỉ có **một đáp án đúng** cho mỗi câu hỏi.  
            Hãy tự quyết định số lượng câu hỏi phù hợp dựa trên độ dài và nội dung của đoạn văn.  

            ## Văn bản đầu vào:
            "{content}"

            ## Định dạng đầu ra:
            Trả lời dưới dạng JSON danh sách câu hỏi như sau:
            [
            {{
                "question": "<Câu hỏi 1>",
                "options": ["<Đáp án A>", "<Đáp án B>", "<Đáp án C>", "<Đáp án D>"],
                "correct_answer": "<Đáp án đúng>"
            }},
            {{
                "question": "<Câu hỏi 2>",
                "options": ["<Đáp án A>", "<Đáp án B>", "<Đáp án C>", "<Đáp án D>"],
                "correct_answer": "<Đáp án đúng>"
            }}
            ]
            """
        user_contents = f' Thông tin để sinh ra câu hỏi: {content}'
        messages = create_message(systemt_contents, user_contents)
       
        try:
            response=self.client.default_chat_completion(messages)
            quizzes = eval(response)  # Chuyển JSON text sang list dict
        except:
            quizzes = [{"error": "Lỗi xử lý JSON từ AI."}]

        return quizzes