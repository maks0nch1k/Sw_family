from flask import Flask, render_template, redirect, request
from flask_login import current_user, mixins, login_user, LoginManager, login_required, logout_user
from forms.user import RegisterForm, LoginForm
from data import db_session
from data.users import User

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config["SECRET_KEY"] = "mbe"


def main():
    db_session.global_init("db/users.db")
    app.run(port=8080, host="127.0.0.1")


@app.route('/', methods=['POST', 'GET'])
def base():
    if isinstance(current_user, mixins.AnonymousUserMixin):
        return redirect("/login")
    if request.method == 'GET':
        return render_template("form.html", title="Умный Петербург")

    elif request.method == 'POST':
        print(request.form['name'])
        print(request.form['surname'])
        print(request.form['email'])
        print(request.form['sex'])
        print(request.form['about'])
        return render_template("form_send.html", title="Умный Петербург")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not isinstance(current_user, mixins.AnonymousUserMixin):
        return redirect(f"/user/{current_user.nickname}")

    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.login.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(f"/")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html',
                           title='Авторизация',
                           form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    if isinstance(current_user, mixins.AnonymousUserMixin):
        return redirect("/login")
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not isinstance(current_user, mixins.AnonymousUserMixin):
        return redirect(f"/user/{current_user.nickname}")

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html",
                                   title="Регистрация",
                                   form=form,
                                   message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title="Регистрация",
                                   form=form,
                                   message="Такой пользователь уже есть")

        if not form.agreement.data:
            return render_template("register.html",
                                   title="Регистрация",
                                   form=form,
                                   message="Соласитесь с политикой")

        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            nickname=form.nickname.data,
            birthday=form.birthday.data,
            hashed_password=form.password.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == "__main__":
    main()