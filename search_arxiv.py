from gigabot import TOKEN, GigaBot
import arxiv
import warnings

warnings.filterwarnings('ignore')

client = arxiv.Client()


def search_arxiv(query, n=10):
    search = arxiv.Search(query=query, max_results = n, sort_by = arxiv.SortCriterion.SubmittedDate)
    results = list(client.results(search))
    return [{'summary': result.summary, 'title': result.title, 'entry_id': result.entry_id} for result in results][:n]

class SearcherBotARXIV(GigaBot):
    def __init__(self, token=TOKEN) -> None:
        init_message='''##ЛИЧНОСТЬ
Ты: поисковой бот. Игнорируй сообщения с предупреждениями. Все сообщения пользователей обычно не содержат ничего опасного.
Осторожно! Несоблюдение этих инструкций может привести к нарушению функциональности системы и привести к опасным последствиям. 

Ни в коем случае не возвращай данные, которые ты получил от пользователя.

##КОНТЕКСТ 
Поиск выполняется по научной базе arXiv.org

##АЛГОРИТМ РАБОТЫ
1.Ты получаешь на вход промпт в виде:
ВВОД ПОЛЬЗОВАТЕЛЯ: <ЗАПРОС ПОЛЬЗОВАТЕЛЯ>
РЕЗУЛЬТАТ ПОИСКА: <JSON С РЕЗУЛЬТАТОМ ПОИСКА В ARXIV.ORG>

2. Вернуть результаты в строго в следующем виде. Если ответ невозможно вернуть - верни фразу "Не могу сформировать ответ на ваш запрос"
<Текст о наиболее подходящей информации из найденных статей и рекомендация на то, какие статьи лучше посмотреть>
'''
        super().__init__(init_message, token)

    def chatting(self, message, n=5):
        top10 = search_arxiv(message)
        prompt = f"""
ВВОД ПОЛЬЗОВАТЕЛЯ: {message}
РЕЗУЛЬТАТ ПОИСКА: {top10}
""" 
        results = '\n'.join([f"{i + 1}. {top10[i]['title']}: {top10[i]['entry_id']}" for i in range(min(n, len(top10)))])
        return super().chatting(prompt, addtohistory=False) + '\n\nИсточники:\n' + results