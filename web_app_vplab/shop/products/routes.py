from flask import render_template,session, request,redirect,url_for,flash,current_app, \
    copy_current_request_context
from shop import app,db,photos, search, login_manager,socketio, Access,DTTCLH,DTTCGH,DTTDLH,DTTDGH,GHTTDG,CKGHTN,CKDSNH,TTNHDS,TTNHST,DHCHT,DHDN,CTTDH
from flask_login import current_user
from sqlalchemy import func
from .models import Category,Brand,Addproduct
from shop.customers.model import CustomerOrder
from shop.products.forms import Addproducts
from shop.customers.forms import Register
from flask_login import login_required
import secrets
import os
#//////////////// SocketIO \\\\\\\\\\\\\\
from random import random
from threading import Lock
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect


import pandas as pd
import json



thread = None
thread_lock = Lock()


@app.route('/')
def home():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        return redirect(url_for('main'))

def brands():
    brands = Brand.query.join(Addproduct, (Brand.id == Addproduct.brand_id)).all()
    return brands

def categories():
    categories = Category.query.join(Addproduct,(Category.id == Addproduct.category_id)).all()
    return categories

@app.route('/socket')
def index():
    print('Server started')
    return render_template('index1.html', async_mode=socketio.async_mode)



@app.route('/dashboard')
@login_required
def main():
    totalcustomers = 0
    totalmember = 0
    totalorder = 0
    DoanhThu = 0

    Stock = 0
    discount = 0
    grandTotal = 0
    subTotal = 0
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        Members = Register.query.filter().all()
        # products = Addproduct.query.filter(Addproduct).all()
        customerOrder = CustomerOrder.query.all()
        customer = Register.query.all()
        dates = db.session.query(db.func.sum(Register.dated), Register.date_created).group_by(Register.date_created).order_by(Register.date_created).all()
        #customer = Register.query.filter_by(id=customer_id).first()
        #Tong Thanh Vien Va Khach Hang
        for totalcustom in customer:
            if totalcustom.username != "Admin" and totalcustom.username != "Manager" and totalcustom.username != "Boss" and totalcustom.username != "Staff" and totalcustom.username != "Sale":
                totalcustomers = totalcustomers + 1
            if totalcustom.username == "Admin" or totalcustom.username == "Manager" or totalcustom.username == "Boss" or totalcustom.username == "Staff" or totalcustom.username == "Sale":
                totalmember = totalmember + 1
        # Tong Doanh Thu 
        for totalOrder in customerOrder:
            if totalOrder.status != CTTDH and totalOrder.status != CKGHTN  and totalOrder.status != CKDSNH and totalOrder.status != TTNHST and totalOrder.status != TTNHDS and totalOrder.status != DHCHT and totalOrder.status != DHDN:
                totalorder = totalorder + 1 
                customer_id = totalOrder.customer_id
                invoice = totalOrder.invoice
                orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
                for _key, product in orders.orders.items():
                    try:
                        Products = Addproduct.query.filter_by(name=product['name']).first()
                        Stock = int(Products.stock) - int(product['quantity'])
                        discount = (product['discount']/100) * float(product['price'])
                        if Stock >= 0:
                            subTotal += float(product['price']) * int(product['quantity'])
                        subTotal -= discount
                        tax = ("%.2f" % (.06 * float(subTotal)))
                        grandTotal = ("%.2f" % (1 * float(subTotal)))        
                        DoanhThu =  float(grandTotal)
                        # print("invoice: " + str(invoice) + "---" + str(grandTotal))
                    except:
                        print("invoice: " + str(invoice) + "--- error" )
        dataChart = []
        dates_label = []
        for dated, date_created in dates:
            dates_label.append(date_created.strftime("%d-%m-%y"))
            dataChart.append(dated)
        # Tong Doanh Thu Theo Ngay
        # for totalOrder in customerOrder:
        #     if totalOrder.status != CTTDH and totalOrder.status != CKGHTN  and totalOrder.status != CKDSNH and totalOrder.status != TTNHST and totalOrder.status != TTNHDS and totalOrder.status != DHCHT and totalOrder.status != DHDN:
        #         totalorder = totalorder + 1 
        #         customer_id = totalOrder.customer_id
        #         invoice = totalOrder.invoice
        #         orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        #         for _key, product in orders.orders.items():
        #             try:
        #                 Products = Addproduct.query.filter_by(name=product['name']).first()
        #                 Stock = int(Products.stock) - int(product['quantity'])
        #                 discount = (product['discount']/100) * float(product['price'])
        #                 if Stock >= 0:
        #                     subTotal += float(product['price']) * int(product['quantity'])
        #                 subTotal -= discount
        #                 tax = ("%.2f" % (.06 * float(subTotal)))
        #                 grandTotal = ("%.2f" % (1 * float(subTotal)))        
        #                 DoanhThu =  float(grandTotal)
        #                 # print("invoice: " + str(invoice) + "---" + str(grandTotal))
        #             except:
        #                 print("invoice: " + str(invoice) + "--- error" )
                        
        if user == 1 or user == 2 or user == 1:
            host = True
        else:
            host = False
        return render_template('home/dashboard.html',dates_label=json.dumps(dates_label),dataChart=json.dumps(dataChart),DoanhThu=DoanhThu,totalorder=totalorder,totalmember=totalmember,host = host,customer=customer,user_auth = user,members=Members,totalcustomers=totalcustomers)

@app.route('/members')
@login_required
def members():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        Members = Register.query.filter().all()
        return render_template('admin/Members.html',user_auth = user,members=Members)

@app.route('/shop')
def shop():
    try:
        user = Access()
    except:
        user = 6
    page = request.args.get('page',1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/index.html', products=products,brands=brands(),categories=categories() ,shoppage=True,user_auth = user)

@app.route('/result')
def result():
    try:
        user = Access()
    except:
        user = 6
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name','desc'] , limit=6)
    return render_template('products/result.html',products=products,brands=brands(),categories=categories(),shoppage=True,user_auth = user)

@app.route('/product/<int:id>')
def single_page(id):
    try:
        user = Access()
    except:
        user = 6
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html',product=product,brands=brands(),categories=categories(),shoppage=True,user_auth = user)




@app.route('/brand/<int:id>')
def get_brand(id):
    try:
        user = Access()
    except:
        user = 6
    page = request.args.get('page',1, type=int)
    get_brand = Brand.query.filter_by(id=id).first_or_404()
    brand = Addproduct.query.filter_by(brand=get_brand).paginate(page=page, per_page=8)
    return render_template('products/index.html',products=brand,brands=brands(),categories=categories(),get_brand=get_brand,shoppage=True,user_auth = user)


@app.route('/categories/<int:id>')
def get_category(id):
    try:
        user = Access()
    except:
        user = 6
    page = request.args.get('page',1, type=int)
    get_cat = Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=8)
    return render_template('products/index.html',products=get_cat_prod,brands=brands(),categories=categories(),get_cat=get_cat,shoppage=True,user_auth = user)


@app.route('/addbrand',methods=['GET','POST'])
@login_required
def addbrand():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        if request.method =="POST":
            user = Access()
            getbrand = request.form.get('brand')
            brand = Brand(name=getbrand)
            db.session.add(brand)
            flash(f'The brand {getbrand} was added to your database','success')
            db.session.commit()
            return redirect(url_for('brands'))
        return render_template('products/addbrand.html', title='Add brand',brands='brands',shopedit = True,user_auth = user)

@app.route('/updatebrand/<int:id>',methods=['GET','POST'])
@login_required
def updatebrand(id):
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        if 'email' not in session:
            flash('Login first please','danger')
            return redirect(url_for('customerLogin'))
        updatebrand = Brand.query.get_or_404(id)
        brand = request.form.get('brand')
        if request.method =="POST":
            updatebrand.name = brand
            flash(f'The brand {updatebrand.name} was changed to {brand}','success')
            db.session.commit()
            return redirect(url_for('brands'))
        brand = updatebrand.name
        return render_template('products/addbrand.html', title='Udate brand',brands='brands',updatebrand=updatebrand,shopedit = True,user_auth = user)


@app.route('/deletebrand/<int:id>', methods=['GET','POST'])
@login_required
def deletebrand(id):
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        brand = Brand.query.get_or_404(id)
        if request.method=="POST":
            db.session.delete(brand)
            flash(f"The brand {brand.name} was deleted from your database","success")
            db.session.commit()
            return redirect(url_for('admin'))
        flash(f"The brand {brand.name} can't be  deleted from your database","warning")
        return redirect(url_for('admin'))

@app.route('/addcat',methods=['GET','POST'])
@login_required
def addcat():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        if request.method =="POST":
            user = Access()
            getcat = request.form.get('category')
            category = Category(name=getcat)
            db.session.add(category)
            flash(f'The brand {getcat} was added to your database','success')
            db.session.commit()
            return redirect(url_for('categories'))
        return render_template('products/addbrand.html', title='Add category',shopedit = True,user_auth = user)


@app.route('/updatecat/<int:id>',methods=['GET','POST'])
@login_required
def updatecat(id):
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        if 'email' not in session:
            flash('Login first please','danger')
            return redirect(url_for('customerLogin'))
        updatecat = Category.query.get_or_404(id)
        category = request.form.get('category')  
        if request.method =="POST":
            user = Access()
            updatecat.name = category
            flash(f'The category {updatecat.name} was changed to {category}','success')
            db.session.commit()
            return redirect(url_for('categories'))
        category = updatecat.name
        return render_template('products/addbrand.html', title='Update cat',updatecat=updatecat,shopedit = True,user_auth = user)



@app.route('/deletecat/<int:id>', methods=['GET','POST'])
@login_required
def deletecat(id):
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        category = Category.query.get_or_404(id)
        if request.method=="POST":
            db.session.delete(category)
            flash(f"The brand {category.name} was deleted from your database","success")
            db.session.commit()
            return redirect(url_for('admin'))
        flash(f"The brand {category.name} can't be  deleted from your database","warning")
        return redirect(url_for('admin'))


@app.route('/addproduct', methods=['GET','POST'])
@login_required
def addproduct():
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        form = Addproducts(request.form)
        brands = Brand.query.all()
        categories = Category.query.all()
        if request.method=="POST"and 'image_1' in request.files:
            user = Access()
            name = form.name.data
            price = form.price.data
            discount = form.discount.data
            stock = form.stock.data
            colors = form.colors.data
            desc = form.discription.data
            brand = request.form.get('brand')
            category = request.form.get('category')
            image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            addproduct = Addproduct(name=name,price=price,discount=discount,stock=stock,colors=colors,desc=desc,category_id=category,brand_id=brand,image_1=image_1,image_2=image_2,image_3=image_3)
            db.session.add(addproduct)
            flash(f'The product {name} was added in database','success')
            db.session.commit()
            return redirect(url_for('admin'))
        return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,categories=categories,shopedit = True,user_auth = user)




@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
@login_required
def updateproduct(id):
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        form = Addproducts(request.form)
        product = Addproduct.query.get_or_404(id)
        brands = Brand.query.all()
        categories = Category.query.all()
        brand = request.form.get('brand')
        category = request.form.get('category')
        user = Access()
        if request.method =="POST":
            product.name = form.name.data 
            product.price = form.price.data
            product.discount = form.discount.data
            product.stock = form.stock.data 
            product.colors = form.colors.data
            product.desc = form.discription.data
            product.category_id = category
            product.brand_id = brand
            if request.files.get('image_1'):
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                    product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
                except:
                    product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            if request.files.get('image_2'):
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                    product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
                except:
                    product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            if request.files.get('image_3'):
                try:
                    os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                    product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
                except:
                    product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")

            flash('The product was updated','success')
            db.session.commit()
            return redirect(url_for('admin'))
        form.name.data = product.name
        form.price.data = product.price
        form.discount.data = product.discount
        form.stock.data = product.stock
        form.colors.data = product.colors
        form.discription.data = product.desc
        brand = product.brand.name
        category = product.category.name
        return render_template('products/addproduct.html', form=form, title='Update Product',getproduct=product, brands=brands,categories=categories,shopedit = True,user_auth = user)


@app.route('/deleteproduct/<int:id>', methods=['POST'])
@login_required
def deleteproduct(id):
    try:
        user = Access()
    except:
        user = 6
    if user >= 6 or user == 0:
        return redirect(url_for('shop'))
    if user < 6:
        product = Addproduct.query.get_or_404(id)
        if request.method =="POST":
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
            except Exception as e:
                print(e)
            db.session.delete(product)
            db.session.commit()
            flash(f'The product {product.name} was delete from your record','success')
            return redirect(url_for('admin'))
        flash(f'Can not delete the product','success')
        return redirect(url_for('admin'))


def background_task_func():
    """Example of how to send server generated events to clients."""

    socketio.sleep(5)
    print("send")
   
    data = {'Name': ['Tom', 'Joseph', 'Krish', 'John','Shadz'], 'Age': [20, 21, 19, 18,36]} 

    data_2= pd.DataFrame(data)
    
    df_json=data_2.to_json(orient='records')
    result = {"objects": json.loads(df_json)}
    socketio.emit('my_response1',result, broadcast=True)

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        dummy_sensor_value = round(random() * 100, 3)
        socketio.emit('updateSensorData', {'value': dummy_sensor_value, "date": get_current_datetime()})

        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')

class MyNamespace(Namespace):
    def on_my_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']})

    def on_my_broadcast_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             broadcast=True)

    def on_join(self, message):
        join_room(message['room'])
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    def on_leave(self, message):
        leave_room(message['room'])
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    def on_close_room(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                             'count': session['receive_count']},
             room=message['room'])
        close_room(message['room'])

    def on_my_room_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             room=message['room'])

    def on_disconnect_request(self):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'Disconnected!', 'count': session['receive_count']})
        disconnect()

    def on_my_ping(self):
        emit('my_pong')

    def on_connect(self):
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_thread)
        emit('my_response', {'data': 'Connected', 'count': 0})

    def on_disconnect(self):
        print('Client disconnected', request.sid)


socketio.on_namespace(MyNamespace('/'))

