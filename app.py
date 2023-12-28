from flask import Flask, render_template, request, flash





app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chess/<pageName>', methods=["GET", "POST"])
def chess_page(pageName):
    return 'Chess is fun!'
@app.route('/wordle/<pageName>', methods=["GET", "POST"])
def wordle_page(pageName):
    return 'Wordle is kinda fun'

if __name__ == '__main__':
    app.run(port=8080, debug=False)