#!/usr/bin/env python3
# coding=utf-8

import os
import vk_api

import flask

app = flask.Flask(__name__)

GROUP_IDS = [int(gid.strip())
             for gid in os.environ.get("IDS", "0").split(',')]
CHECK_STRINGS = os.environ.get("CHECK_STRINGS", "").split(',')
TOKENS = os.environ.get("TOKENS", "").split(',')


class Community:
    def __init__(self, group_id: int, check_string, token):
        self.id: int = group_id
        self.check_string = check_string
        self.token = token

        self.api = vk_api.VkApi(token=self.token, api_version="5.80").get_api()

    def mark_important(self, message_id):
        self.api.messages.markAsImportant(message_ids=message_id, important=1)


def get_community(event: dict):
    group_id = event["group_id"]
    index = GROUP_IDS.index(group_id)
    check_string = CHECK_STRINGS[index]
    token = TOKENS[index]
    return Community(group_id, check_string, token)


@app.route("/callback", methods=["POST"])
def callback():
    event: dict = flask.request.get_json()
    community: Community = get_community(event)

    event_type = event["type"]
    if event_type == "confirmation":
        return community.check_string
    if event_type == "message_new":
        message = event["object"]
        if not message["from_id"] == -community.id:
            message_id = message["id"]
            community.mark_important(message_id)
    return "ok"


@app.route("/callback", methods=["GET"])
def howto():
    return flask.Markup("""<p>
    1. Зайди в Настройки группы -> Работа с API -> Callback API
    2. Вставь текущую ссылку в поле Адрес
    3. Нажми Подтвердить
    4. На вкладке Типы событий отметь Входящее сообщение
    5. ????
    6. PROFIT!

    (по всем вопросам обращайтесь <a href="https://vk.me/cybertailor">к Сайберу</a>)
    </p>""")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
