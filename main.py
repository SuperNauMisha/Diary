from flask import Flask, render_template, redirect, request, make_response, session, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.marks import Marks
from data.subjects import Subjects
from forms.marks_form import MarksForm
from forms.user import RegisterForm
from forms.login_form import LoginForm
import datetime
import sqlalchemy
from data.db_session import SqlAlchemyBase


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        subjects = db_sess.query(Subjects)
        marks = db_sess.query(Marks).filter(
            (Marks.user_id == current_user.id))
        marks_subject_id  = []
        not_empty_subj = []
        for mark in marks:
            marks_subject_id.append(mark.subject_id)
        for sub in subjects:
            if sub.id in marks_subject_id and sub not in not_empty_subj:
                not_empty_subj.append(sub)
        return render_template("index.html", subjects=not_empty_subj, marks=marks)
    return render_template("index.html", subjects=[], marks=[])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            student=form.student.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/marks',  methods=['GET', 'POST'])
@login_required
def add_marks():
    form = MarksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        marks = Marks()
        marks.mark = form.mark.data
        if int(marks.mark) > 5 or int(marks.mark) < 1:
            return render_template('marks.html', title='Добавление оценки', form=form, message="Оценка можеты быть цифрой от 1 до 5")

        subjects = db_sess.query(Subjects)

        if form.subject.data not in [subject.name for subject in subjects]:
            subj = Subjects()
            subj.name = form.subject.data
            db_sess.add(subj)
            db_sess.commit()

        marks.subject_id = db_sess.query(Subjects).filter(Subjects.name == form.subject.data).first().id
        marks.user_id = current_user.id


        db_sess.add(marks)
        db_sess.commit()
        return redirect('/')
    return render_template('marks.html', title='Добавление оценки',
                           form=form)

@app.route('/marks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def marks_delete(id):
    db_sess = db_session.create_session()
    marks = db_sess.query(Marks).filter(Marks.subject_id == id,
                                      Marks.user_id == current_user.id)
    if marks:
        for i in marks:
            db_sess.delete(i)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')



def main():
    db_session.global_init("db/diary.sqlite")
    db_sess = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()
