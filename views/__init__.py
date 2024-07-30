from flask import Flask
from .main_view import bp

app = Flask(__name__) # Flask 애플리케이션을 생성

app.register_blueprint(bp)






if __name__ == '__main__':
    app.run()