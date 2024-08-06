from flask import Flask, render_template
from config import create_app

app = create_app()

# html로 기능 테스트
@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
