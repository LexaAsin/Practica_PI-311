import telebot
from jira import JIRA
from telebot import types

bot = telebot.TeleBot('7123961112:AAEM7EvLW9PAiVKge_tCWSUlmCjQYE4HU5I')

jira_options = {'server': 'https://pi311pract.atlassian.net'}
jira = JIRA("https://pi311pract.atlassian.net", basic_auth=("lasin470@gmail.com", "ATATT3xFfGF0kZqyBEFyOfixpslfLErNKziXeuurRlvulZ6w2z4RfVRvAhppwrteVN1lvZ0tzdfT9rIBsfej3-Bh2MESUXJeEvxK28gM8IEJowxJimXMTxZjKc1-cnWPPXfqo-N-2EK9T5pv87zj9v8VnVHk5t40aPBFtU1r3aQhHP7mOCbqITg=3FD6BE2A"))


@bot.message_handler(commands=["start"])
def bot_messages(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Создать задачу")
    markup.add(item1)
    item2 = types.KeyboardButton("Найти задачу")
    markup.add(item2)
    item3 = types.KeyboardButton("Открыть задачу")
    markup.add(item3)
    item4 = types.KeyboardButton("Удалить задачу")
    markup.add(item4)

    bot.send_message(message.chat.id, 'Я могу исполнить три желания:\n Создать задачу\n Найти задачу\n Открыть задачу\nУдалить задачу', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.strip() == 'Создать задачу':
        bot.send_message(message.chat.id, 'Создание задачи. Введите название задачи.')
        bot.register_next_step_handler(message, get_create_issue_summary)
    elif message.text.strip() == 'Найти задачу':
        bot.register_next_step_handler(message, get_search_issue)
    elif message.text.strip() == 'Открыть задачу':
        bot.send_message(message.chat.id, 'Открытые задачи. Введите номер задачи TJ-...')
        bot.register_next_step_handler(message, get_open_issue)
    elif message.text.strip() == 'Удалить задачу':
        bot.send_message(message.chat.id, 'Удаление задачи. Введите номер задачи KAN-...')
        bot.register_next_step_handler(message, delete_issue)


#Добавление задачи
def get_create_issue_summary(message):
    global jira_summary
    jira_summary = message.text.strip()
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
                                      'Приоритет: ' + jira_priority + '\n' +
                                      'Описание: ' + jira_description)
    bot.send_message(message.chat.id, 'Создать задачу? (Да/Нет)')
    bot.register_next_step_handler(message, get_create_issue)


def get_create_issue(message):
    if message.text.strip() == 'Да' :
        issue = jira.create_issue(project = 'KAN',
                                      summary= jira_summary,
                                      description = jira_description,
                                      #priority={'name': jira_priority}
                                      issuetype= {'name': 'Task'},)
        bot.send_message(message.chat.id, 'Задача ' + issue.key + ' создана')
    elif message.text.strip() == 'Нет' :
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
