# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_socketio import SocketIO, send
import pandas as pd
import pymysql
from gtts import gTTS
from playsound import playsound
import os

connection = pymysql.connect(host='localhost', port=3306, user='root',
                             password='1234', db='ocb', charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()
sql = "select query, rule, answer from chatbot"
cursor.execute(sql)
result = cursor.fetchall()
chatbot_data = pd.DataFrame(result)
chatbot_data = chatbot_data.drop_duplicates(['query'])

def Voice(text):
    comment_to_voice = gTTS(text=text, lang='ko')
    comment_to_voice.save("./voice/chat.mp3")
    playsound("./voice/chat.mp3")
    os.remove("./voice/chat.mp3")
    
    
def Chating(text):

    chat_dic = {}
    row = 0
    for rule in chatbot_data['rule']:
        chat_dic[row] = rule.split('|')
        row += 1

    def chat(req):
        for k, v in chat_dic.items():
            index = -1
            for word in v:
                try:
                    if index == -1:
                        index = req.index(word)
                    else:
                        if index < req.index(word, index):
                            index = req.index(word, index)
                        else:
                            index = -1
                            break
                except ValueError:
                    index = -1
                    break
            if index > -1:
                return chatbot_data['answer'][k]
        return '무슨 말인지 모르겠어요.'

    result = chat(text)
    return result


app = Flask(__name__)
app.secret_key = "mysecret"

socket_io = SocketIO(app)


@app.route('/')
def chatting():
    return render_template('index.html')


@app.route('/info')
def info():
    return render_template('info.html')


@socket_io.on("message")
def request(message):
    to_client = dict()
    Chat_Result = Chating(message)
    to_client['from_msg'] = message
    to_client['message'] = Chat_Result
    to_client['type'] = 'normal'
    send(to_client, broadcast=True)
    Voice(Chat_Result)
    

if __name__ == '__main__':
    socket_io.run(app, debug=True, port=8000)