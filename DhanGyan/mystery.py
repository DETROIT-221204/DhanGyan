from flask import Flask, render_template, request

app = Flask(__name__)


remaining_chances = 10000

@app.route("/", methods=["GET", "POST"])
def home():
    global remaining_chances
    code = False
    message = ""

    if request.method == 'POST' and remaining_chances > 0:
        data = request.form['finalCode']
        remaining_chances -= 1

        if data in ['2019108&!$', '534121113*@%', '687151614(^#']:
            code = True
            message = "Congratulations! You won."
        elif remaining_chances == 0:
            message = "You have exhausted your chances."
        else:
            message = "Incorrect code. Try again."

    elif remaining_chances == 0:
        message = "You have exhausted your chances."

    return render_template('form.html', code=code, message=message, count=remaining_chances)

if __name__ == "__main__":
    app.run(debug=True)
