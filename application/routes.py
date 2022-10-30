from application import app
from flask import render_template,request, jsonify, redirect, flash, url_for,session
from application.models import db, User, Data, News
import hashlib
from sqlalchemy.exc import IntegrityError
import click


@app.cli.command()
@click.argument('x', nargs= 1)
@click.argument('y', nargs= 1)
def test(x, y) :
    try:
        x = int(x)
    except ValueError:
        print('Error: Invalid value for "X"')
        return None
    try:
        y = int(y)
    except ValueError:
        print('Error: Invalid value for "Y"')
        return None

    print(int(x)**int(y))


@app.cli.command()
@click.argument('s', nargs= 1)
@click.argument('N', nargs=1)
def repeat(s, n):
    try:
        n = int(n)
    except ValueError:
        print('Error: Invalid value for "N"')
        return None
    print(s*int(n))


n = 3  # login attempts
global db_id

# syncing IDs
if len(User.query.all()) == 0:
    db_id = 1
else:
    db_id = User.query.all()[-1].id + 1

# cryptography Function: Responsible for Hashing.


def crypt(fname, p, x=db_id):
    salt = hashlib.sha1((fname + str(x)).encode()).hexdigest()
    hash_p = hashlib.sha1(p.encode()).hexdigest()
    m_p = salt[:10] + hash_p[0:10] + salt[10:20] + hash_p[10:20] + salt[20:30] + hash_p[20:30]+ salt[30:] + hash_p[30:]
    final_hash = hashlib.sha1(m_p.encode()).hexdigest()
    return final_hash


@app.route('/delete')
def delete():
    if not session.get('username'):
        flash("Please login first", 'alert-danger')
        return redirect(url_for('login'))
    Id = request.args.get('id')
    x = News.query.filter_by(id=Id).first()
    if x is None:
        flash('No news found', 'alert-danger')
        return redirect(url_for('news'))
    if session.get('username') == x.author or session.get('type') == 'admin':
        db.session.delete(x)
        db.session.commit()
        flash('Deleted Successfully', 'alert-success')
        if session.get('type') == 'admin':
            return redirect(url_for('news'))
        return redirect(url_for('news'))
    else:
        flash("You don't have enough access", 'alert-danger')
        return redirect(url_for('news'))


@app.route("/")
def home():
    return render_template('home.html', users = User.query.all(), data = Data.query.all())


@app.route("/new", methods= ["GET","POST"])
def new():
    global db_id
    if request.method == "POST":
        passwd = request.form['password']
        uname = request.form['username']
        hash_pass = crypt(uname,passwd, db_id)
        if 'contact_no' not in request.form or request.form['contact_no'] == '':
            contact_no = -1
        else:
            contact_no = request.form['contact_no']

        x = User(request.form['username'], hash_pass, contact_no)
        db.session.add(x)
        db_id += 1
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Username already taken', 'alert-danger')
            return redirect(url_for('new'))
        flash('User added successfully, Login now', 'alert-success')
        return redirect(url_for('login'))
    return render_template('new_user.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('username'):
        flash("Already logged in ", 'alert-danger')
        return redirect(url_for('home'))

    if request.method == "POST":
        u_name = request.form['username'].strip()
        password = request.form['password'].strip()
        x = User.query.filter_by(username = u_name).first()
        if x is None:
            flash("No user Found", 'alert-danger')
            return redirect(url_for('login'))
        ip_pass = crypt(u_name, password, x.id)

        if x.password == ip_pass and x.count < n:
            flash("Logged in Successfully", 'alert-success')
            x.count = 0
            db.session.commit()
            session['username'] = u_name
            session['type'] = x.type
            return redirect(url_for('home'))

        elif x.count >= n:
            flash("Account Locked, Maximum attempt exceed. Contact support.", 'alert-danger')
            return redirect(url_for('login'))

        else:
            x.count += 1
            db.session.commit()
            flash("Login Failed, Wrong Password", 'alert-danger')
            if x.count >= n:
                flash("Account Locked", 'alert-danger')
            else:
                flash(str(n - x.count) + " attempts remaining.", 'alert-danger')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    if not session.get('username'):
        flash("Please login first", 'alert-danger')
        return redirect(url_for('login'))
    #session.pop('username', None)
    session.clear()
    flash('Logged out Successfully', 'alert-success')
    return redirect(url_for('login'))


@app.route("/news")
def news():
    return render_template('news.html', news = News.query.all())


@app.route("/add_news", methods=['GET', 'POST'])
def add_news():
    if not session.get('username'):
        flash("Please login first", 'alert-danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        x = News(request.form['heading'], request.form['description'], session.get('username'))
        db.session.add(x)
        db.session.commit()
        flash("News added Successfully", 'alert-success')
        return redirect(url_for('add_news'))

    return render_template('add_news.html')


@app.route('/my_news')
def my_news():
    if not session.get('username'):
        flash("Please login first", 'alert-danger')
        return redirect(url_for('login'))
    return render_template('news.html', news = News.query.filter_by(author= session.get('username')).all())


@app.route('/edit/<Id>', methods= ["GET", "POST"])
def edit(Id):
    if not session.get('username'):
        flash("Please login first", 'alert-danger')
        return redirect(url_for('login'))

    x = News.query.filter_by(id=Id).first()
    if x is None:
        flash('No news found', 'alert-danger')
        return redirect(url_for('news'))
    if session.get('username') == x.author or session.get('type') == 'admin':
        if request.method == 'GET':
            return render_template('edit.html', obj=x)
        if request.method == 'POST':
            if len(request.form['heading'].strip()) == 0:
                flash("Please fill out all the fields", 'alert-danger')
                return redirect(Id)
            x.heading = request.form['heading']
            x.description = request.form['description']
            db.session.commit()
            flash('Updated successfully', 'alert-success')
        return redirect(url_for('news'))
    else:
        flash("You don't have enough access", 'alert-danger')
        return redirect(url_for('news'))


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get("username"):
        flash("Please login first",'alert-danger')
        return redirect(url_for('login'))
    else:
        if request.method == 'GET':
            return render_template('change_password.html')
        elif request.method == 'POST':
            username = session.get('username')
            current_password = request.form['current_password']
            password = request.form['password']
            password_confirm = request.form['confirm_password']
            x = User.query.filter_by(username=username).first()
            if x is None:
                flash('No User Found','alert-danger')
            else:
                if x.password == crypt(username,current_password,x.id):
                    if password_confirm == password:
                        x.password = crypt(username,password,x.id)
                        db.session.commit()
                        session.clear()
                        flash('Password Changed Successfully', 'alert-success')
                        flash('Kindly Login again', 'alert-success')
                        return redirect(url_for('login'))
                    else:
                        flash("Password didn't matched. Kindly try again", 'alert-danger')
                        return redirect(url_for('change_password'))
                else:
                    flash("Wrong Password. Try Again or reset password", 'alert-danger')
                    return redirect(url_for('change_password'))


@app.route("/dashboard")
def dashboard():
    if session.get("type") == "admin":
        return render_template('dashboard.html')
    else:
        flash("You have no Access", 'alert-danger')
        return redirect(url_for('home'))


@app.route('/account')
def account():
    if not session.get('username'):
        flash("Please login first", 'alert-danger')
        return redirect(url_for('login'))
    else:
        return render_template()
