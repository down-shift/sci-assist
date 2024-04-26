import telebot
from telebot.handler_backends import State, StatesGroup
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import StateMemoryStorage
from telebot import custom_filters
import typing

from gigabot import GigaBot
from langchain.schema import HumanMessage, SystemMessage
from latexify import LatexBuilder
from search_ddg import SearcherBotDDG
from search_arxiv import SearcherBotARXIV

TG_TOKEN = "7029262559:AAHESYrvvDyRunTvzb0DoDu_p_2oeRyECyE"
# https://t.me/GigaResearchAssistant_bot

class L18N_CONFIG:
    """
    класс локализации. в дальнейшем может быть заменен/расширен
    """
    start_msg = "Привет! Я - твой виртуальный научрук, которыый будет рад помочь с написанием/проверкой/оформлением твоей научной работы. Для создания нового проекта введи /new"
    cancel_msg = "Текущее действие отменено"
    new_research = "Хорошо, давай создадим агента для новой работы. Сейчас вам предложат ввести некоторые поля"
    new_subjects = "Принято! Теперь напиши через проблел предметные области, в которые входит твоя научная работа"
    new_notifications = "Хочешь переодически получать уведомления и \"нагоняй\", что бы не потеряться?"
    subject_area_response = "Вот какие области я распознал: "
    research_name_input = "Введите имя вашей научной работы"
    wrong_input = "Хорошо, попробуем еще разочек."
    correct_input = "Ура! Ваш проект %s добавлен."
    delete_proj = "Вот список ваших проектов, выберете который хотите удалить" # TODO
    research_clean_context = "Контекст очищен для %s"
    lst_proj = "Список ваших научных работ"

class ResearchStates(StatesGroup):
    """
    Состояния для тг бота
    """
    research_name = State()
    subjects = State() # TODO
    notifications = State()
    final_check = State()
    in_processing = State()    
    latex_build = State()
    search = State()
    arxiv_search = State()

#util
subj_giga = GigaBot(init_message="Следуй четко инструкции - на вход тебе подается пользовательский ввод через пробел, тебе нужно их привести к нормальной форме слова и выдать их в ответ через пробел")
def get_subjects(s: str) -> typing.List[str]:
    """утилита. нормализует пользовательский ввод через гигу

    Args:
        s (str): пользовательский ввод предметных областей

    Returns:
        typing.List[str]: нормализованный вывод
    """
    answ = subj_giga.chatting(s.replace("  ", " "))
    return answ.split()


state_storage = StateMemoryStorage() 
bot = telebot.TeleBot(TG_TOKEN, state_storage=state_storage)

user_giga = GigaBot()
data = {
    # user_id : {
    #    research_name : "", subjects : [], notifications : boot, history : [HumanMessage | SystemMessage]
    # }
}

# tg bot logic
# =====================================================================================

@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    bot.send_message(message.chat.id, L18N_CONFIG.start_msg)

# new
# research_name ========================================================================
@bot.message_handler(state="*", commands=['new'])
def new(message: Message) -> None:
    bot.send_message(message.chat.id, L18N_CONFIG.new_research)
    bot.send_message(message.chat.id, L18N_CONFIG.research_name_input)
    bot.set_state(message.chat.id, ResearchStates.research_name)
    data.update({
        message.chat.id : {
            "research_name" : "", "subjects" : [], "notifications" : False, "history" : [
                SystemMessage(
                    content="Ты - персональный научный руководитель для разработки научного проекта. твоя задача - максимально объективно отвечать на все запросы."
                )
            ]
        }
    })
    print(data)

#set research_name
@bot.message_handler(state=ResearchStates.research_name)
def set_research_name(message: Message) -> None:
    data[message.chat.id]['research_name'] = message.text.strip()

    bot.send_message(message.chat.id, L18N_CONFIG.new_subjects)
    bot.set_state(message.chat.id, ResearchStates.subjects)
# ======================================================================================

# set subjects
@bot.message_handler(state=ResearchStates.subjects)
def set_subjects(message: Message) -> None:
    subjects_response = get_subjects(message.text)
    keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton("✅ YEA ✅", callback_data="yes_sub"),
                    InlineKeyboardButton("❌ NOPE ❌", callback_data="no_sub")
                )
    keyboard.row_width = 2
    bot.send_message(message.chat.id, L18N_CONFIG.subject_area_response + ", ".join(subjects_response), reply_markup = keyboard)
    
    data[message.chat.id]['subjects'] = subjects_response

@bot.callback_query_handler(lambda x: x.data in set(["yes_sub", "no_sub"]))
def set_subjects_check(callback: CallbackQuery) -> None:
    if callback.data == "no_sub":
        set_subjects(callback.message)
        bot.set_state(callback.message.chat.id, ResearchStates.subjects)
        return
        
    bot.set_state(callback.message.chat.id, ResearchStates.notifications)
    set_notifications(callback.message)

# ======================================================================================

# set notifications
@bot.message_handler(state=ResearchStates.notifications)
def set_notifications(message: Message) -> None:
    keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton("✅ YEA ✅", callback_data="yes_notif"),
                    InlineKeyboardButton("❌ NOPE ❌", callback_data="no_notif")
                )
    keyboard.row_width = 2
    bot.send_message(message.chat.id, L18N_CONFIG.new_notifications, reply_markup = keyboard)

@bot.callback_query_handler(lambda x: x.data in set(["yes_notif", "no_notif"]))
def set_notifications_check(callback: CallbackQuery) -> None:
    data[callback.message.chat.id]["notifications"] = True if callback.data == "yes_notif" else False

    final_check(callback)
    

# =======================================================================================

# result
def final_check(callback: CallbackQuery) -> None:
    bot.set_state(callback.message.chat.id, ResearchStates.final_check)

    msg = ("Хорошо, сверяем показатели:\n"
            f"Имя работы: *{data.get(callback.message.chat.id).get('research_name')}*\n"
            f"Предметные области: *{', '.join(data.get(callback.message.chat.id).get('subjects'))}*\n"
            f"Уведомления : *{data.get(callback.message.chat.id).get('notifications')}* \n"
            f"Все верно?")
    
    keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton("✅ YEA ✅", callback_data="correct"),
                InlineKeyboardButton("❌ NOPE ❌", callback_data="incorrect")
            )
    bot.send_message(callback.message.chat.id, msg, parse_mode="markdown", reply_markup=keyboard)
        

@bot.callback_query_handler(lambda x: x.data in set(["correct", "incorrect"]))
def final_check_callback(callback: CallbackQuery) -> None:
    if callback.data == "correct":
        data[callback.message.chat.id]["history"] = [
                SystemMessage(
                    f"Ты теперь научрук проекта с названием {data[callback.message.chat.id]['research_name']}, твои предметные области: {data[callback.message.chat.id]['subjects']}"
                )
            ]
        
        bot.set_state(callback.message.chat.id, ResearchStates.in_processing)
        bot.send_message(callback.message.chat.id, "Проект вашей работы успешно добавлен.")
    
    elif callback.data == "incorrect":
        bot.send_message(callback.message.chat.id, L18N_CONFIG.wrong_input)
        bot.set_state(callback.message.chat.id, ResearchStates.research_name)
        bot.send_message(callback.message.chat.id, L18N_CONFIG.research_name_input)
        

# =========================================================================================

# processing
@bot.message_handler(state=ResearchStates.in_processing)
def process_user_querry(message: Message) -> None:
    history = data[message.chat.id]["history"]
    
    history.append(HumanMessage(content=message.text))
    answer = user_giga.history_chatting(history=history)
    data[message.chat.id]["history"] = history
    
    bot.send_message(message.chat.id, text="Гига говорит >"+answer)

# ==========================================================================================

# latex
@bot.message_handler(commands=["latex"])
def get_latex(message: Message) -> None:
    bot.send_message(message.chat.id, text="Пришлите мне черновик вашей статьи")
    bot.set_state(message.chat.id, ResearchStates.latex_build)
    
@bot.message_handler(state=ResearchStates.latex_build)
def build_latex(message: Message) -> None:
    bot.send_message(message.chat.id, text="Текстовый вывод tex >"+
                     f"""
                     '''
                     {LatexBuilder().chatting(message=message.text)}
                     '''
                     """
                     )
    bot.set_state(message.chat.id, ResearchStates.in_processing)

# ==========================================================================================

# search
@bot.message_handler(commands=["search"])
def get_search(message: Message) -> None:
    bot.send_message(message.chat.id, text="Постараюсь поискать для вас интересной информации. Пришлите мне поисковой запрос")
    bot.set_state(message.chat.id, ResearchStates.search)
    
@bot.message_handler(state=ResearchStates.search)
def search(message: Message) -> None:
    answer = SearcherBotDDG().chatting(message=message.text)
    bot.send_message(message.chat.id, "Результаты поиска: " + answer)

    bot.set_state(message.chat.id, ResearchStates.in_processing)

# search
@bot.message_handler(commands=["arxiv_search"])
def get_arxiv_search(message: Message) -> None:
    bot.send_message(message.chat.id, text="Постараюсь поискать для вас информации из arxiv. Пришлите мне поисковой запрос")
    bot.set_state(message.chat.id, ResearchStates.arxiv_search)
    
@bot.message_handler(state=ResearchStates.arxiv_search)
def arxiv_search(message: Message) -> None:
    answer = SearcherBotARXIV().chatting(message=message.text)
    bot.send_message(message.chat.id, "Результаты поиска: " + answer)
    
    bot.set_state(message.chat.id, ResearchStates.in_processing)


# ==========================================================================================

@bot.message_handler(commands=['cancel'])
def cancel(message: Message) -> None:
    bot.send_message(message.chat.id, L18N_CONFIG.cancel_msg)
    bot.delete_state(message.chat.id)

@bot.message_handler(commands=["clean_context"])
def clear_context(message: Message) -> None:
        data[message.chat.id]["history"] = [
                    SystemMessage(
                        f"Ты теперь научрук проекта с названием {data[message.chat.id]['research_name']}, твои предметные области: {data[message.chat.id]['subjects']}"
                    )
                ]
        bot.send_message(message.chat.id, L18N_CONFIG.research_clean_context.format(data[message.chat.id]["research_name"])) 



if __name__ == "__main__":
    print("bot started")
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling(skip_pending=True)