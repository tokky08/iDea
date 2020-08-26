from app import *

# ワードのログリスト作成
def words_log_func(session_id):
    words_log = []
    for id in users_log:
        if str(id) == str(session_id):
            words_log = users_log[id]
    return words_log

# ユーザごとのログリストの作成
def users_log_func(session_id, word):
    for id in users_log:
        if str(id) == str(session_id):
            users_log[id].append(word)