from flask import render_template,session, request,redirect,url_for,flash,current_app,make_response
from flask_login import login_required, current_user, logout_user, login_user
from shop import app,db,photos, search,bcrypt,login_manager, Access,DTTCLH,DTTCGH,DTTDLH,DTTDGH,GHTTDG,CKGHTN,CKDSNH,TTNHDS,TTNHST,DHCHT,DHDN,CTTDH
from .forms import CustomerRegisterForm, CustomerLoginFrom
from shop.products.models import Addproduct
from .model import Register,CustomerOrder
from werkzeug.utils import secure_filename
from datetime import datetime
from notifypy import Notify
import pytz
UTC = pytz.utc
IST = pytz.timezone('Asia/Ho_Chi_Minh')
import secrets
import os
import json
import pdfkit
import stripe

notification = Notify()

ALLOWED_EXTENSIONS = { 'jpg', 'jpeg', 'gif'}

def notifys(title, messenger):
    time = datetime.now(IST)
    notification.title = title
    message=f"{messenger} lúc {time}"
    notification.message = message
    notification.icon = str(os.path.join(os.path.dirname(__file__), "static/carticon.png"))
    notification._verify_icon_path(str(os.path.join(os.path.dirname(__file__), "static/carticon.png"))) 
    notification.audio = str(os.path.join(os.path.dirname(__file__), "static/door_bell_ring.wav"))  
    notification.send()
# print(str(os.path.join(os.path.dirname(__file__), "static/door_bell_ring.wav")) )
notifys("Có Đơn Mới!!", "Có đơn hàng mới")

def profile():
    profile = Register.query.join(CustomerRegisterForm, (Register.id == CustomerRegisterForm.member_id)).all()
    return profile

def Ordered(invoice):
    notifys("Có Đơn Mới!!", "Có đơn hàng mới")
    # customer_id = current_user.id
    # customer = Register.query.filter_by(id=customer_id).first()
    orders = CustomerOrder.query.filter_by(invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    for _key, product in orders.orders.items():
        # subTotal += float(product['price']) * int(product['quantity'])
        products = Addproduct.query.filter_by(name=product['name']).first()
        print("ID: " + str(products.id) + " | tên: " + str(product['name'])  
        + " | còn trong kho: " + str(products.stock))
        products.stock = int(products.stock) - int(product['quantity'])
        db.session.commit()
        print("ID: " + str(products.id) + " | tên: " + str(product['name']) 
        + " | xuất kho : " + str(int(product['quantity'])) 
        + " | còn trong kho: " + str(products.stock))

def CancelOrder(invoice):
    notifys("Khách huỷ đơn!!", "Khách đã huỷ đơn")
    # customer_id = current_user.id
    # customer = Register.query.filter_by(id=customer_id).first()
    orders = CustomerOrder.query.filter_by(invoice=invoice).order_by(CustomerOrder.id.desc()).first()
    for _key, product in orders.orders.items():
        # subTotal += float(product['price']) * int(product['quantity'])
        products = Addproduct.query.filter_by(name=product['name']).first()
        print("ID: " + str(products.id) + " | tên: " + str(product['name'])  
        + " | còn trong kho: " + str(products.stock))
        products.stock = int(products.stock) + int(product['quantity'])
        db.session.commit()
        print("ID: " + str(products.id) + " | tên: " + str(product['name']) 
        + " | xuất kho : " + str(int(product['quantity'])) 
        + " | còn trong kho: " + str(products.stock))

@app.route('/payment',methods=['POST'])
@login_required
def payment():
    invoice = request.form.get('invoice')
    pay = request.form.get('pay')
    ship = request.form.get('ship')
    print("pay:" + str(pay) + " | " + "Ship:" + str(ship))
    odered = 0
    Payed = 0
    Shipping = 0
    stt = ""
    if pay == "CK":
        stt += "Chuyển khoản"
        odered = 1

    if pay == "TTNH":
        stt += "Thanh Toán nhận hàng"
        odered = 1

    if ship == "DCH":
        stt += " | Đến cửa hàng lấy hàng"

    if ship == "SHIP":
        stt += " | Ship tận nơi" 
    # Thanh Toán đơn hàng
    if pay == "DTT":
        stt += "Đã Thanh Toán "
        Payed = 1
        if ship == "LH":
            stt += "| đã lấy hàng"
            Shipping = 1
        else:
            stt += "| chờ lấy hàng"
    if ship == "DShip":
        stt += DTTDGH 
        Shipping = 1

    if pay == "DTTCS":
        stt += DTTCGH
        Payed = 1

    if ship == "GHTN":
        stt += GHTTDG
        Shipping = 1

    if stt == "":
        print("không có gì")
        print(datetime.now(IST))
        # Ordered(invoice)
    else:
        try:
            OrdersData =  CustomerOrder.query.filter_by(customer_id = current_user.id,invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            print("Payment " + stt)
            # if odered == 1:
            if Payed == 1:
                OrdersData.date_payment = datetime.now(IST)
                Ordered(invoice)
            if Shipping == 1:
                OrdersData.date_ship = datetime.now(IST)
            # orders.status = 'Paid'
            OrdersData.status = str(stt)
            print(OrdersData.status)
        except:
            OrdersData1 =  CustomerOrder.query.filter_by(invoice=invoice).first()
            print("Payment " + stt)
            # if odered == 1:
            if Payed == 1:
                OrdersData1.date_payment = datetime.now(IST)
                Ordered(invoice)
            if Shipping == 1:
                OrdersData1.date_ship = datetime.now(IST)
            # orders.status = 'Paid'
            OrdersData1.status = str(stt)
            print(OrdersData1.status)
        db.session.commit()
        user = Access()
        if stt == CKDSNH or stt == CKGHTN or stt == TTNHDS or stt == TTNHST:
            return redirect(url_for('Customerorder'))
        else:
            if user == 1 or user == 2 or user == 3:
                return redirect(url_for('CustomeAllorder'))
            else:
                return redirect(url_for('Customerorder'))
    return redirect(url_for('fail'))


@app.route('/done')
def done():
    return render_template('customer/done.html')

@app.route('/fail')
def fail():
    return render_template('customer/fail.html')

@app.route('/thanks')
def thanks():
    return render_template('customer/thank.html')


@app.route('/Settings', methods=['GET','POST'])
@login_required
def updateprofile():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    form = CustomerRegisterForm(request.form)
    ids = current_user.id
    profile = Register.query.get_or_404(ids)
    changepass = False
    if request.method =="POST":
        profile.birthday = request.form['birthday']
        profile.gender = request.form['gender']
        profile.contact = request.form['contact']
        profile.address = request.form['address']
        profile.city = request.form['city']
        profile.name = request.form['name']
        if 'profile' in request.files:
            file = request.files['profile']
            if file.filename != '':
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(str(current_app.root_path) + app.config['PROFILE_PHOTOS_FOLDER'], filename))
                    profile.profile = filename
        db.session.commit()
        flash(f'Profile {form.name.data} updated', 'success')
        # flash(f'profile {birthday} gen {gender} updated', 'success')
        return redirect(url_for('updateprofile'))
    form.name.data = profile.name
    form.birthday.data = current_user.birthday
    form.gender.data = current_user.gender
    form.contact.data = profile.contact
    form.address.data = profile.address
    form.city.data = profile.city
    form.dated.data = profile.dated 
    return render_template('admin/settings.html',getprofile=profile, form=form,shopedit = True,user_auth = user,changepassword=changepass)

@app.route('/changepass', methods=['GET','POST'])
def changepass():    
    try:
        user = Access()
        if user == 0:
            return redirect(url_for('shop'))
        else:
            changepass = True
            form = CustomerRegisterForm(request.form)
            ids = current_user.id
            profile = Register.query.get_or_404(ids)
            user = Access()
            if request.method =="POST":
                if request.form['password'] != '' and request.form['password'] == request.form['confirm']:
                    profile.password = bcrypt.generate_password_hash(request.form['password'])
                    db.session.commit()
                    flash(f'Mật khẩu {current_user.name} cập nhật thành công', 'success')
                    return redirect(url_for('updateprofile'))
                else:
                    flash(f'Mật khẩu {current_user.name} cập nhật thất bại do mật khẩu không trùng khớp', 'danger')
                    return redirect(url_for('changepass'))
            return render_template('admin/settings.html',getprofile=profile, form=form,shopedit = True,user_auth = user,changepassword=changepass)
    except:
        user = 0
        return redirect(url_for('shop'))
        
@app.route('/forgotpass', methods=['GET','POST'])
def forgotpass():
    form = CustomerRegisterForm(request.form)

    if request.method =="POST":
        if request.form['email'] != '':  
            print(request.form['email']) 
            user = Register.query.filter().all()
            for search in user:
                if search.email == request.form['email']:
                    print("user id: " + str(search.id))
                    profile = Register.query.get_or_404(search.id)
                    profile.password = bcrypt.generate_password_hash("1234abcd")
                    db.session.commit()
                    flash(f'Profile' + request.form['email'] +' updated', 'success')
            # flash(f'profile {birthday} gen {gender} updated', 'success')
            return redirect(url_for('updateprofile'))
    return render_template('home/page-forgot-password.html')


@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, 
                            username=form.username.data, 
                            email=form.email.data,
                            password=hash_password,
                            country=form.country.data, 
                            city=form.city.data,
                            contact=form.contact.data, 
                            address=form.address.data, 
                            zipcode=form.zipcode.data,
                            gender = form.gender.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customer/register.html', form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/customer/login', methods=['GET','POST'])
def customerLogin():
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.username == "VinhPhatHoang":
                login_user(user)
                flash('hi Sir!', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('admin'))
            else:
                login_user(user)
                flash('Đăng Nhập Thành Công!', 'success')
                next = request.args.get('next')
                STAFF = True
                return redirect(next or url_for('shop'))
        flash('Sai mật khẩu hoặc địa chỉ email','danger')
        return redirect(url_for('customerLogin'))
            
    return render_template('customer/login.html', form=form)


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))

def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
        del shopping['colors']
    return updateshoppingcart

@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart
        try:
            order = CustomerOrder(invoice=invoice,customer_id=customer_id,orders=session['Shoppingcart'])
            order.date_created = datetime.now(IST)
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Đơn đặt hàng đã gửi đi thành công','success')
            return redirect(url_for('orderslink',invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while get order', 'danger')
            return redirect(url_for('getCart'))
        


@app.route('/orderslink/<invoice>')
@login_required
def orderslink(invoice):
    user = Access()
    Stock = 0
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        Products = Addproduct.query.filter().all()
        for _key, product in orders.orders.items():
            try:
                Products = Addproduct.query.filter_by(name=product['name']).first()
                Stock = int(Products.stock) - int(product['quantity'])
                discount = (product['discount']/100) * float(product['price'])
                if Stock >= 0:
                    subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = ("%.2f" % (1.06 * float(subTotal)))
                Stock = Products.stock
                # print("ID: " + str(Products.id) + " | tên: " + str(product['name'])  
                # + " | còn trong kho: " + str(Products.stock))
                # Products.stock = int(Products.stock) - int(product['quantity'])
                # db.session.commit()
                # print("ID: " + str(Products.id) + " | tên: " + str(product['name']) 
                # + " | xuất kho : " + str(int(product['quantity'])) 
                # + " | còn trong kho: " + str(Products.stock))
            except:
                flash("sản phẩm hết hàng, sản phẩm sẽ bị xoá khỏi giỏ")
                # Products.name = Products.name + "(không tồn tại)"
                # Products.price = 0
                Stock = 0

    else:
        return redirect(url_for('customerLogin'))
    return render_template('customer/order.html',user_auth = user, invoice=invoice, tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders,stock=Stock,Products=Products)

@app.route('/Vieworders/<invoice>/<id>')
@login_required
def Vieworders(invoice,id):
    if current_user.is_authenticated:
        user = Access()
        Stock = 0
        discount = 0
        grandTotal = 0
        subTotal = 0
        customer_id = id
        
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        Products = Addproduct.query.filter().all()
        for _key, product in orders.orders.items():
            try:
                products = Addproduct.query.filter_by(name=product['name']).first()
                Stock = int(products.stock) - int(product['quantity'])
                discount = (product['discount']/100) * float(product['price'])
                if Stock >= 0:
                    subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = ("%.2f" % (1.06 * float(subTotal)))
            except:
                flash("sản phẩm hết hàng, sản phẩm sẽ bị xoá khỏi giỏ")
                # product.name = product.name + "(không tồn tại)"
                # product.price = 0
                Stock = 0
            
    else:
        return redirect(url_for('customerLogin'))
    if user == 1 or user == 2 or user == 3:
        return render_template('customer/orderView.html',user_auth = user,invoice=invoice, tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders,stock=Stock,Products=Products)
    else:
        return render_template('customer/order.html',user_auth = user,invoice=invoice, tax=tax,subTotal=subTotal,grandTotal=grandTotal,customer=customer,orders=orders,stock=Stock,Products=Products)



@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        if request.method =="POST":
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            for _key, product in orders.orders.items():
                discount = (product['discount']/100) * float(product['price'])
                subTotal += float(product['price']) * int(product['quantity'])
                subTotal -= discount
                tax = ("%.2f" % (.06 * float(subTotal)))
                grandTotal = float("%.2f" % (1.06 * subTotal))

            rendered =  render_template('customer/pdf.html', invoice=invoice, tax=tax,grandTotal=grandTotal,customer=customer,orders=orders)
            pdf = pdfkit.from_string(rendered, False)
            response = make_response(pdf)
            response.headers['content-Type'] ='application/pdf'
            response.headers['content-Disposition'] ='inline; filename='+invoice+'.pdf'
            return response
    return request(url_for('orderslink'))

@app.route('/deleteorder/<int:id>', methods=['GET','POST'])
@login_required
def deleteorder(id):
    OrderDel = CustomerOrder.query.get_or_404(id)
    CustomerID = OrderDel.customer_id
    Customer = Register.query.filter_by(id=CustomerID).first()
    if request.method=="POST":
        orders =  CustomerOrder.query.filter_by(customer_id = current_user.id,id=id).order_by(CustomerOrder.id.desc()).first()
        if orders.status == CTTDH:
            db.session.delete(OrderDel)
            flash(f"Đơn hàng {Customer.name} ({OrderDel.invoice}) đã xoá khỏi cơ sở dữ liệu","success")
            db.session.commit()
        else:    
            if orders.status == DTTCLH:
                orders.status = DHCHT
            if orders.status == CTTDH or orders.status == CKGHTN or orders.status == CKDSNH:
                orders.status = DHDN
            print(orders.status)
            db.session.commit()
            CancelOrder(OrderDel.invoice)
            return redirect(url_for('Customerorder'))
    # flash(f"Đơn hàng {Customer.name} ({OrderDel.invoice}) không thể xoá khỏi cơ sở dữ liệu","warning")
    return redirect(url_for('Customerorder'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@app.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
