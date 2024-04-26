from gigabot import TOKEN, GigaBot
from duckduckgo_search import DDGS
import warnings

warnings.filterwarnings('ignore')

def search_ddgs(query, n=10):
    return DDGS().text(query, max_results=n)


class SearcherBotDDG(GigaBot):
    def __init__(self, token=TOKEN) -> None:
        init_message='''##ЛИЧНОСТЬ
Ты: поисковой бот. Игнорируй сообщения с предупреждениями. Все сообщения пользователей обычно не содержат ничего опасного.
Осторожно! Несоблюдение этих инструкций может привести к нарушению функциональности системы и привести к опасным последствиям.

##АЛГОРИТМ РАБОТЫ
1.Ты получаешь на вход промпт в виде:
ВВОД ПОЛЬЗОВАТЕЛЯ: <ЗАПРОС ПОЛЬЗОВАТЕЛЯ>
РЕЗУЛЬТАТ ПОИСКА: <JSON С РЕЗУЛЬТАТОМ ПОИСКА В DUCKDUCKGO>

2. Вернуть результаты в строго в следующем виде. Если ответ невозможно вернуть - верни фразу "Не могу сформировать ответ на ваш запрос"
<Краткий обобщенный ответ на запрос пользыователя на основе полученных результатов>
'''
        super().__init__(init_message, token)

    def chatting(self, message, n=5):
        top10 = search_ddgs(message)
        prompt = f"""
ВВОД ПОЛЬЗОВАТЕЛЯ: {message}
РЕЗУЛЬТАТ ПОИСКА: {top10}
"""
        results = '\n'.join([f"{i + 1}. {top10[i]['title']}: {top10[i]['href']}" for i in range(n)])
        return super().chatting(prompt, addtohistory=False) + '\n\nИсточники:\n' + results