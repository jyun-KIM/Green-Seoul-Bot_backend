from flask import Flask
from config import create_app
from chatbot_service import chatbot_ns

app, api = create_app()

api.add_namespace(chatbot_ns,'/chatbot')


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8000)