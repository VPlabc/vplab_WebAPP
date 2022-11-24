# python3 -m pip install --user virtualenv
# pip3 install virtualenv
# python -m venv env
#   env/bin/activate

# search cùng tháng
#__________________Nam__thang_ngay
#searchdate = date(2022,   5, 25)
#result_date= DBModels.query.filter_by(feild_db=searchdate).all()

#tạo thu mục
#os.makedirs(str(current_app.root_path) + "/"+ "Chọn")

# importing the modules
# import os
# import shutil

# origin = str(current_app.root_path) + "/"+ "Gốc"
# target = str(current_app.root_path) + "/"+ "Chọn"

# files = os.listdir(origin)

# for file_name in files:
#    shutil.copy(origin+file_name, target+file_name)
# print("Files are copied successfully")

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os

from flask_msearch import Search
from flask_login import LoginManager, current_user
from flask_migrate import Migrate


    
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY']='hfouewhfoiwefoquw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
app.config['PROFILE_PHOTOS_FOLDER'] = os.path.join(basedir, '/static/team/')
ALLOWED_EXTENSIONS = { 'jpg', 'jpeg', 'gif'}
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
search = Search()
search.init_app(app)

migrate = Migrate(app, db)
from flask_socketio import SocketIO
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

DTTCLH = "Đã Thanh Toán | chờ lấy hàng"
DTTCGH = "Đã Thanh Toán | chờ shiper"
DTTDLH = "Đã Thanh Toán | đã lấy hàng"
DTTDGH = "Đã Thanh Toán | Đang ship"

GHTTDG = "Giao hàng thanh toán | đã bàn giao cho shiper"
CKGHTN = "Chuyển khoản | Ship tận nơi"
CKDSNH = "Chuyển khoản | Đến cửa hàng lấy hàng"
TTNHDS = "Thanh Toán nhận hàng | Đến cửa hàng lấy hàng"
TTNHST = "Thanh Toán nhận hàng | Ship tận nơi"

DHCHT = "Đã huỷ và chờ giải quyết tài chính"
DHDN = "Đã huỷ đơn hàng"
CTTDH = "Chưa Thanh Toán"


def Access():
    user = 0
    if current_user.username == "Admin":
        user = 1
    if current_user.username == "Boss":
        user = 2
    if current_user.username == "Manager":
        user = 3
    if current_user.username == "Staff":
        user = 4
    if current_user.username == "Seller":
        user = 5
    return user

with app.app_context():
    if db.engine.url.drivername == "sqlite":
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = u"Please login first"


from shop.products import routes
from shop.admin import routes
from shop.carts import carts
from shop.customers import routes
from shop.photo import routes
