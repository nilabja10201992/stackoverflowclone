import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from flask import Flask, request, redirect, render_template,url_for,flash

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.secret_key = os.urandom(24)
    app.config.from_pyfile('config.cfg')

    mail = Mail(app)

    S = URLSafeTimedSerializer('dasfegrhrdaUYUHHNJ&@IUJ')

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    @app.route('/register', methods=('GET', 'POST'))
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            db = get_db()
            error = None
            
            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif db.execute(
                'SELECT id FROM user WHERE username = ?', (username,)
            ).fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
            
            elif db.execute(
                'SELECT id FROM user WHERE email = ?', (email,)
            ).fetchone() is not None:
                error = 'User {} is already registered.'.format(username)
            
            if error is None:
                db.execute(
                    'INSERT INTO TempUser (username, password, email) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), email)
                )
                db.commit()
                token = S.dumps(email, salt='email-confirm')
                msg = Message('Confirm Email', sender="stackoverflow.iiith@gmail.com", recipients=[email])
                link = url_for('confirm_mail', token=token, _external=True)
                msg.body = 'Your Authentication link is : {}'.format(link)
                mail.send(msg)
                flash('Registration is successful. Please check your email for verification link.')

            flash(error)

        return render_template('auth/register.html')

    @app.route('/confirm/<token>')
    def confirm_mail(token):
        try:
            email = S.loads(token, salt='email-confirm', max_age=3600)
            # users.email_confirmation(email) 
            # TODO: move user from TempUser to user
            db=get_db()
            user = db.execute(
                'SELECT username, password, email FROM TempUser where email = ?',(email,)).fetchall()
            
            print(user[0])

            db.execute(
                    'INSERT INTO user (username, password, email) VALUES (?, ?, ?)',
                    (user[0][0], user[0][1], user[0][2])
                )

            db.commit()

            db.execute('DELETE from TempUser where email = ?',(email,))
            
            db.commit()
            return "Email confirmed."
            # return redirect(url_for(login'))

        except SignatureExpired:
            return "<h3> Token Expired !<h3>"


    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import question
    app.register_blueprint(question.bp)
    app.add_url_rule('/', endpoint='index')

    return app

