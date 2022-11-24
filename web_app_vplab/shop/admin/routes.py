from flask import render_template,session, request,redirect,url_for,flash, jsonify
from shop import app,db,bcrypt, Access
from .forms import RegistrationForm,LoginForm
from .models import User,Calendar
from shop.customers.model import Register,CustomerOrder
from shop.products.models import Addproduct,Category,Brand

from flask_login import login_required, current_user, logout_user, login_user

@app.route('/admin')
@login_required
def admin():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        products = Addproduct.query.all()
        return render_template('admin/index.html', title='Admin page',products=products,shopedit=True,user_auth = user)

@app.route('/brands')
@login_required
def brands():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        brands = Brand.query.order_by(Brand.id.desc()).all()
        return render_template('admin/brand.html', title='brands',brands=brands,shopedit=True,user_auth = user)


@app.route('/categories')
@login_required
def categories():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        categories = Category.query.order_by(Category.id.desc()).all()
        return render_template('admin/brand.html', title='categories',categories=categories,shopedit=True,user_auth = user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Tài khoản này đã đăng kí")
            return render_template('admin/register.html',
                                   msg='Tài khoản này đã đăng kí',
                                   success=False,
                                   form=form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email này đã đăng kí")
            return render_template('admin/register.html',
                                   msg='Email này đã đăng kí',
                                   success=False,
                                   form=form)
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data,username=form.username.data, email=form.email.data,
                    password=hash_password)
        db.session.add(user)
        flash(f'welcome {form.name.data} Thanks for registering','success')
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('admin/register.html',title='Register user', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'welcome {form.email.data} you are logedin now','success')
            
            return redirect(url_for('admin'))
        else:
            flash(f'Wrong email and password', 'danger')
            return redirect(url_for('login'))
    return render_template('admin/login.html',msg='Đăng nhập quản trị',form=form)

# for admin - manager - boss
@app.route('/CustomerAllOrder')
@login_required
def CustomeAllorder():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        CUSTOMERORDER = CustomerOrder.query.all()
        # CUSTOMERORDER = CustomerOrder.query.filter_by(status = "Chưa Thanh Toán").all()
        customer = Register.query.all()
        #customer = Register.query.filter_by(id=customer_id).first()
        host = True
        return render_template('admin/Customerorder.html',customerorder=CUSTOMERORDER,customer=customer, title='categories',shopedit=True,user_auth = user,host=host)
# for customer
@app.route('/CustomerOrder')
@login_required
def Customerorder():
    user = Access()
    CUSTOMERORDER = CustomerOrder.query.filter_by(customer_id = current_user.id).all()
    customer = Register.query.all()
    #customer = Register.query.filter_by(id=customer_id).first()
    host = False
    return render_template('admin/Customerorder.html',customerorder=CUSTOMERORDER,customer=customer, title='categories',shopedit=True,user_auth = user,host=host)




events = [
    {
        'title' : 'TestEvent',
        'start' : '2022-11-24', 
        'end' : '',
        'url' : 'https://youtube.com'
    },
    {
        'title' : 'Another TestEvent',
        'start' : '2022-11-25', 
        'end' : '2022-10-27',
        'url' : 'https://google.com'
    },
    {
        'title' : 'Another ',
        'start' : '2022-11-02', 
        'end' : '2022-11-02',
        'url' : 'https://google.com'
    }
]

@app.route('/addevent', methods=['GET', "POST"])
def add():
    if current_user.is_authenticated:
        if request.method == "POST":
            title = request.form['title']
            start = request.form['start']
            end = request.form['end']
            url = request.form['url']
            if end == '':
                end=start
            events.append({
                'title' : title,
                'start' : start,
                'end' : end,
                'url' : url
            },
            )
        return render_template("admin/add.html")
    else:
        return redirect(url_for('customerLogin'))

@app.route('/calendar')
def calendar():
    try:
        user = Access()
    except:
        return redirect(url_for('customerLogin'))
    if user == 1 or user == 2 or user == 3 or user == 4 or user == 5:
        return render_template('admin/calendar.html', events=events, user_auth = user)

