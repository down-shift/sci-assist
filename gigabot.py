from langchain.chat_models.gigachat import GigaChat
from langchain.schema import HumanMessage, SystemMessage

import typing

TOKEN = "NTlkY2MyZmItM2Q4ZC00ZWMzLWE2NjAtNTI3MzZhOTk2ZjQzOjVhZGJiZDQxLTc0YjAtNDQxNi04YjAzLTUxZDVmYTY4NTkwNw=="

class GigaBot:
    def __init__(self, init_message='', token=TOKEN) -> None:
        self.model = GigaChat(credentials=token, scope="GIGACHAT_API_CORP", verify_ssl_certs=False)
        self.history = [
            SystemMessage(
                content=init_message
            )
        ]
        
    def append(self, text: str) -> None:
        self.history.append(text)
        
    def set_history(self, history: typing.List ) -> None:
        pass
    
    def pop(self, index=None) -> None:
        if index:
            return self.history.pop(index)
        return self.history.pop()
    
    def get_answer(self, addtohistory=True) -> str:
        answer = self.model(self.history)
        
        if addtohistory:
            self.append(answer)
        else: 
            self.pop()
            
        return answer.content
    
    def history_chatting(self, history: typing.List) -> str:
        return self.model(history).content
    
    def chatting(self, message, addtohistory=True) -> str:
        self.append(HumanMessage(message))
        answer = self.get_answer(addtohistory)
        return answer