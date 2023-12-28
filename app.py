from flask import Flask, render_template, request, flash





app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chess')
@app.route('/chess/<pageName>', methods=["GET", "POST"])
def chess_page(pageName):
    match pageName:
        case 'home':
            if request.method == "POST":
                user_name = request.form.get("userName")

            return render_template('chess_home.html')
        case _:
            return f'No route found: josephroussos.dev/chess/{pageName}'
    return 'Chess is fun!'
@app.route('/wordle/<pageName>', methods=["GET", "POST"])
def wordle_page(pageName):
    return 'Wordle is kinda fun'

if __name__ == '__main__':
    app.run(port=8080, debug=False)