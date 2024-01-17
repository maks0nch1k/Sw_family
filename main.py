from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def main():
    return render_template("main.html", title="Умный бэ")


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")