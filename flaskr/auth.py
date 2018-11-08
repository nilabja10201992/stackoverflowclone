import functools
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

S = URLSafeTimedSerializer('dasfegrhrdaUYUHHNJ&@IUJ')
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def init():
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None and user is not None:
            session.clear()
            session['user_id'] = user['id']
            session['picture']=user['profile_picture']
            print (session['picture'])
            print("hello")
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@bp.route('/<int:id>/profile')
def profile(id):
    db = get_db()
    posts=db.execute('SELECT * FROM post WHERE author_id = ?', (id,)).fetchall()
    ans1=db.execute('SELECT * FROM answer WHERE author_id = ?', (id,)).fetchall()
    result=db.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchall()
    ans=[]
    for i in ans1:
        ans.append(db.execute('SELECT * FROM post WHERE qid = ?', (i['qid'],)).fetchone())
    return render_template('auth/profile.html',result=result,posts=posts,ans=ans)

@bp.route('/<int:id>/update_profile', methods=('GET', 'POST'))
def update_profile(id):
    user=get_user(id)
    if request.method == 'POST':
        body = request.form['description_body']
        error = None
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user SET description = ?'
                ' WHERE id = ?',
                (body, id)
            )
            db.commit()
            return redirect(url_for('auth.profile',id=id))
    return render_template('auth/update_profile.html',user_data=user)


def get_user(id):
    user = get_db().execute('select * from user where id=?',(id,)).fetchone()
    if user is None:
        abort(404, "User id {0} doesn't exist.".format(id))
    return user



def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view