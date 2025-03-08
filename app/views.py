from flask import render_template, redirect, url_for, flash, request, send_file, send_from_directory
from app import app
from app.forms import ChooseForm, LoginForm, ChangePasswordForm, RegisterForm, SubmitForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User
from urllib.parse import urlsplit
import csv
import io

'''4. Extend the previous exercise to add buttons (choose appropriate Bootcamp Icons for them) to each row
of the admin list:
• A delete/bin button that when clicked deletes the chosen user. However, it is not allowed to delete
the last admin user in the system.
• A change role button that toggles the chosen user to “Admin” if they were “Normal” and “Normal”
if they were “Admin”. Again, it is not allowed to toggle the role of the last admin user
In both of these cases, if the user affected is the current user, they should be logged out and re-directed
to the home page.'''

@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html', title="Account")

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_authenticated or not current_user.role == 'admin':
        return redirect('/account')

    form = SubmitForm()
    form.toggle.label.text = 'Toggle Privileges'

    q = db.select(User.id, User.username, User.email, User.role)
    users = db.session.execute(q).all()

    if form.validate_on_submit():
        user_id = form.choose.data
        if 'delete' in request.form:
            delete = request.form.get('delete')
            print(delete)
        else:
            delete = False
        toggle = form.toggle.data

        user = User.query.filter_by(id=user_id).first()
        admin_count = User.query.filter_by(role='admin').count()
        if user:
            if user.role == 'admin' and admin_count <= 1:
                flash('No changes were made.'
                      'There must always be at least 1 admin', 'danger')
            else:
                if toggle:
                    if user.role == 'admin':
                        user.role = 'normal'
                    else:
                        user.role = 'admin'
                elif delete:
                    db.session.delete(user)
                else:
                    flash('Button choice not detected - no changes were made.', 'danger')

        db.session.commit()
        if delete:
            db.session.expunge_all()

        q = db.select(User.id, User.username, User.email, User.role)
        users = db.session.execute(q).all()

        if user.id == current_user.id:
            logout_user()
            return redirect(url_for('home'))


        return render_template( 'admin.html', title='Admin', users=users, form=form)


    return render_template('admin.html', title='Admin', users=users, form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('generic_form.html', title='Sign In', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old_password = form.old_password.data
        password = form.password.data

        if not current_user.check_password(old_password):
            flash('Password entered does not match our records, please try again', 'danger')
        else:
            current_user.set_password(password)
            flash('Password has been updated', 'success')

        return render_template('change_password.html', title="Account", form=form)

    return render_template('change_password.html', title="Account", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        role = form.role.data
        errors = 0
        qu = db.select(User).where(User.username == username)
        qe = db.select(User).where(User.email == email)
        if db.session.scalar(qu):
            form.username.errors.append('This username is already in use')
            errors += 1
        if db.session.scalar(qe):
            form.email.errors.append('This email is already in use')
            errors += 1
        if errors == 0:
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            user.role = role
            db.session.add(user)
            db.session.commit()
        else:
            flash('Error with information input, please try again', 'danger')
            return render_template('register.html', title='Register', form=form)

        current_user = db.session.scalar(sa.Select(User).where(User.username == username))
        if current_user is None or not current_user.check_password(form.password.data):
            flash('Error retrieving details', 'danger')
            return redirect(url_for('login'))

        login_user(current_user)

        return redirect(url_for('home'))



    return render_template('register.html', title='Register', form=form)

# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500