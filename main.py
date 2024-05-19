import telebot
from jira import JIRA
from telebot import types

bot = telebot.TeleBot('7123961112:AAEM7EvLW9PAiVKge_tCWSUlmCjQYE4HU5I')

jira_options = {'server': 'https://pi311pract.atlassian.net'}
jira = JIRA("https://pi311pract.atlassian.net", basic_auth=("lasin470@gmail.com", "ATATT3xFfGF02B-2MCvoEgPMl4xZek9T56Mh6Falg5VeZGpJhu2AMa7zfaiHSmBFNv6Y-7XtITfC4Sl-2aaIq9L2GsiNcn9gtjv_LTbxez3rTZL8MBgSOynaomg6wTq6aaWplLWli2X22fJR8WQDXk4JUj1YSgqL5jFO9qt_f096hwEziWmZzUo=855B362D"))

@bot.message_handler(commands=["start"])
def bot_messages(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Создать задачу")
    markup.add(item1)
    item2 = types.KeyboardButton("Найти задачу")
    markup.add(item2)
    item3 = types.KeyboardButton("Открыть задачу")
    markup.add(item3)
    item4 = types.KeyboardButton("Изменить статус")
    markup.add(item4)
    item5 = types.KeyboardButton("Удалить задачу")
    markup.add(item5)

    bot.send_message(message.chat.id, 'Я могу исполнить 5 желаний:\n Создать задачу\n Найти задачу\n Открыть задачу\n Изменить статус\n Удалить задачу', reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'Создать задачу':
        bot.send_message(message.chat.id, 'Создание задачи. Введите название задачи.')
        bot.register_next_step_handler(message, get_create_issue_summary)
    elif message.text.strip() == 'Найти задачу':
        bot.send_message(message.chat.id, 'Введите ключевое слово для поиска задач.')
        bot.register_next_step_handler(message, get_search_issue)
    elif message.text.strip() == 'Открыть задачу':
        bot.send_message(message.chat.id, 'Открытые задачи. Введите номер задачи, например KAN-...')
        bot.register_next_step_handler(message, get_open_issue)
    elif message.text.strip() == 'Удалить задачу':
        bot.send_message(message.chat.id, 'Удаление задачи. Введите номер задачи KAN-...')
        bot.register_next_step_handler(message, delete_issue)
    elif message.text.strip() == 'Изменить статус':
        bot.send_message(message.chat.id, 'Изменение статуса. Введите номер задачи KAN-...')
        bot.register_next_step_handler(message, change)

#Добавление задачи
def get_create_issue_summary(message):
    global jira_summary
    jira_summary = message.text.strip()
    bot.send_message(message.chat.id, 'Создание задачи. Введите Статус.')
    bot.register_next_step_handler(message, get_create_issue_status)

def get_create_issue_status(message):
    global jira_status
    jira_status = message.text.strip()
    bot.send_message(message.chat.id, 'Создание задачи. Введите приоритет.')
    bot.register_next_step_handler(message, get_create_issue_priority)
def get_create_issue_priority(message):
    global jira_priority
    jira_priority = message.text.strip()
    bot.send_message(message.chat.id, 'Создание задачи. Введите описание')
    bot.register_next_step_handler(message, get_create_issue_description)

def get_create_issue_description(message):
    global jira_description
    jira_description = message.text.strip()
    bot.send_message(message.chat.id, 'Название: ' + jira_summary + '\n' +
                                      'Статус: ' + jira_priority + '\n' +
                                      'Приоритет: ' + jira_priority + '\n' +
                                      'Описание: ' + jira_description)
    bot.send_message(message.chat.id, 'Создать задачу? (Да/Нет)')
    bot.register_next_step_handler(message, get_create_issue)

def get_create_issue(message):
    if message.text.strip() == 'Да' :
        issue = jira.create_issue(project = 'KAN',
                                      summary= jira_summary,
                                      description = jira_description,
                                      issuetype= {'name': 'Task'},
                                      priority = {'name': jira_priority})
        bot.send_message(message.chat.id, 'Задача ' + issue.key + ' создана')
        if jira_status.upper() == 'TO DO':
            jira.transition_issue(issue.key, '11')
        elif jira_status.upper() == 'IN PROGRESS':
            jira.transition_issue(issue.key, '21')
        elif jira_status.upper() == 'DONE':
            jira.transition_issue(issue.key, '31')
    elif message.text.strip() == 'Нет':
        bot.send_message(message.chat.id, 'Создание задачи отменено.')

#Поиск задачи
def get_search_issue(message):
    search_text = message.text.strip()
    jql = f'text ~ "{search_text}"'
    issues = jira.search_issues(jql, maxResults=False)
    ans = []
    for issue in issues:
        ans.append(issue.key)
    bot.send_message(message.chat.id, 'Найдены задачи:' + '\n'.join(ans))

#Окрытие задачи
def get_open_issue(message):
    issue_key = message.text.strip().upper()
    if issue_key.startswith('KAN-'):
        try:
            issue = jira.issue(issue_key)
            desc = issue.fields.description if issue.fields.description is not None else '-'
            bot.send_message(message.chat.id, 'Ключ: ' + issue.key + '\n'
                                              'Название: ' + issue.fields.summary + '\n' +
                                              'Приоритет: ' + issue.fields.priority.name + '\n' +
                                              'Описание: ' + desc)
        except Exception as e:
            bot.send_message(message.chat.id, 'Ошибка при получении задачи: ' + str(e))
    else:
        bot.send_message(message.chat.id, 'Некорректный формат ключа задачи. Введите ключ в формате KAN-123.')

#Изменение статуса
def change(message):
    global issue_key
    issue_key = message.text.strip().upper()

    if issue_key.startswith('KAN-'):
        try:
            issue = jira.issue(issue_key)
            current_status = issue.fields.status.name
            bot.send_message(message.chat.id, f'Текущий статус задачи "{issue_key}": {current_status}')
            bot.send_message(message.chat.id, 'Введите статус, в который хотите перевести задачу: "TO DO","IN PROGRESS","DONE"')
            bot.register_next_step_handler(message, change_status)
        except Exception as e:
            bot.send_message(message.chat.id, 'Ошибка при получении статуса задачи: ' + str(e))
    else:
        bot.send_message(message.chat.id, 'Некорректный формат ключа задачи. Введите ключ в формате KAN-123.')


def change_status(message):
    change_s = message.text.strip().upper()
    if issue_key.startswith('KAN-'):
        try:
            issue = jira.issue(issue_key)
            if change_s == "TO DO":
                jira.transition_issue(issue.key, '11')
                bot.send_message(message.chat.id, 'Статус изменен.')
            elif change_s == "IN PROGRESS":
                jira.transition_issue(issue.key, '21')
                bot.send_message(message.chat.id, 'Статус изменен.')
            elif change_s == "DONE":
                jira.transition_issue(issue.key, '31')
                bot.send_message(message.chat.id, 'Статус изменен.')
            else:
                bot.send_message(message.chat.id, 'Некорректный статус. Введите один из: TO DO, IN PROGRESS, DONE')
        except Exception as e:
            bot.send_message(message.chat.id, 'Ошибка при изменении статуса: ' + str(e))
    else:
        bot.send_message(message.chat.id, 'Некорректный формат ключа задачи. Введите ключ в формате KAN-123.')

#Удаление задачи
def delete_issue(message):
    issue_key = message.text.strip().upper()
    if issue_key.startswith('KAN-'):
        try:
            issue = jira.issue(issue_key)
            issue.delete()
            bot.send_message(message.chat.id, 'Задача ' + issue_key + ' удалена.')
        except Exception as e:
            bot.send_message(message.chat.id, 'Ошибка при удалении задачи: ' + str(e))
    else:
        bot.send_message(message.chat.id, 'Некорректный формат ключа задачи. Введите ключ в формате KAN-123.')

if __name__ == '__main__':
    bot.infinity_polling()