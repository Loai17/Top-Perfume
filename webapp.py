from flask import *
from flask import session as login_session
from sqlalchemy.exc import IntegrityError
from model import *
from werkzeug.utils import secure_filename
from forms import ContactForm

# Flask Mail
from flask_mail import Message, Mail
 
mail = Mail()

UPLOAD_FOLDER = 'static/productsImages'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.secret_key = "MY_SUPER_SECRET_KEY"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'loai.qubti@gmail.com'
app.config["MAIL_PASSWORD"] = 'Qloai1107'
 
mail.init_app(app)

# LOCAL
engine = create_engine('sqlite:///database.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def home():
	form = ContactForm()

	if request.method == 'POST':
	    if form.validate() == False:
	      	flash('All fields are required.')
	      	return render_template('index.html', form=form)
	    else:
	    	msg = Message("Website Message", sender='contactUs@example.com', recipients=['loai.qubti@gmail.com'])
      		msg.body = """
From: %s <%s>
Subject: %s
Message: %s
      		""" % (form.name.data, form.email.data, form.subject.data, form.message.data)
      		mail.send(msg)
	      	
	      	return render_template('index.html', success=True)
		
	return render_template('index.html', form=form)

@app.route('/shop', methods=['GET'])
def shop():
	products = session.query(ShopItems).all()
	return render_template('shop.html' , products = products)

if __name__ == '__main__':
    app.run(debug=True)
