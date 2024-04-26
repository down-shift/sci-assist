from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

TOKEN = "NTlkY2MyZmItM2Q4ZC00ZWMzLWE2NjAtNTI3MzZhOTk2ZjQzOjVhZGJiZDQxLTc0YjAtNDQxNi04YjAzLTUxZDVmYTY4NTkwNw=="


class GigaBot:
    def __init__(self, init_message='', token=TOKEN) -> None:
        self.model = GigaChat(credentials=token, scope="GIGACHAT_API_CORP", verify_ssl_certs=False)
        self.history = [
            SystemMessage(
                content=init_message
            )
        ]
        
    def append(self, text):
        self.history.append(text)
    
    def pop(self, index=None):
        if index:
            return self.history.pop(index)
        return self.history.pop()
    
    def get_answer(self, addtohistory=True):
        answer = self.model(self.history)
        
        if addtohistory:
            self.append(answer)
        else: 
            self.pop()
            
        return answer.content
        
    def chatting(self, message, addtohistory=True):
        self.append(HumanMessage(message))
        answer = self.get_answer(addtohistory)
        return answer
