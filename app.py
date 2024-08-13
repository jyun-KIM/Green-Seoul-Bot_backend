from flask import Flask
from config import create_app
from chatbot import Chatbot

app, api = create_app()

api.add_namespace(Chatbot,'/chatbot')


if __name__ == '__main__':
    app.run(debug=True, port=8000)


#,host='0.0.0.0', port=8000
