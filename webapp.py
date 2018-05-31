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

@app.route('/',methods=['GET','POST'])
def home():
	form = ContactForm()
	productsList = session.query(ShopItems).all()
	loadMore = False

	products=[]
	if len(productsList) >= 8:
		for i in range(8) :
			products.append(productsList[i])
	else:
		products = productsList

	if len(products)<len(productsList) :
		loadMore = True

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

	return render_template('index.html', form=form,number=1, products=products, loadMore=loadMore)


@app.route('/<number>', methods=['GET','POST'])
def loadMore(number):
	form = ContactForm()
	productsList = session.query(ShopItems).all()
	loadMore = False

	products=[]
	if len(productsList) >= (8 * int(number)) :
		for i in range(8*number) :
				products.append(productsList[i])
	else:
		products = productsList

	if len(products)<len(productsList) :
		loadMore = True

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
		
	return render_template('index.html', form=form, number=number, products=products, loadMore=loadMore)

@app.route('/shop', methods=['GET','POST'])
def shop():
	products = session.query(ShopItems).all()
	return render_template('shop.html' , products = products)

@app.route('/about', methods=['GET','POST'])
def about():
	return render_template('about.html'	)









# Admin Portal
@app.route('/admin',methods=['GET','POST'])
def adminSignin():
	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]
		
		adminCheck=session.query(Admin).filter_by(username=username).first()

		if(adminCheck != None and adminCheck.password==password):
			# Logged in successfully
			return render_template('admin.html')
		else:
			return redirect(url_for('adminSignin'))
	else:
		return render_template('adminSignin.html')

if __name__ == '__main__':
	app.run(debug=True)
