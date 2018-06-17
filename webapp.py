from flask import *
from flask import session as login_session
from sqlalchemy.exc import IntegrityError
from model import *
from werkzeug.utils import secure_filename
from forms import ContactForm
import json, ast
import pyperclip

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

def autoBrand():
	products = session.query(ShopItems).all()
	brands=[]
	for product in products:
		flag=True
		for brand in brands:
			if brand == product.brand:
				flag=False
		if flag:
			brands.append(product.brand)

	if brands == []:
		return "Sorry about that. Looks like you don't have any products yet."
	return brands


@app.route('/',methods=['GET','POST'])
def home():
	form = ContactForm()
	productsList = session.query(ShopItems).all()
	loadMore = False
	brands = ast.literal_eval(json.dumps(autoBrand()))

	products=[]
	if len(productsList) >= 8:
		for i in range(8) :
			products.append(productsList[i])
	else:
		products = productsList

	if len(products)<len(productsList) :
		loadMore = True

	if request.method == 'POST':
		form.name = request.form['name']
		form.email = request.form['email']
		form.message = request.form['message']
		
		if form.name != "" and form.email!= "" and form.message != "":
			msg = Message("Website Message", sender='contactUs@example.com', recipients=['loai.qubti@gmail.com'])
			msg.body = """
			From: %s <%s>
			Message: %s
			""" % (form.name, form.email, form.message)
			mail.send(msg)
			print("message sent")

			return render_template('index.html', success=True)
		else :
			return render_template('index.html')


	return render_template('index.html', form=form ,number=1, products=products, loadMore=loadMore, brands=brands)


@app.route('/<number>', methods=['GET','POST'])
def loadMore(number):
	form = ContactForm()
	productsList = session.query(ShopItems).all()
	loadMore = False
	brands = ast.literal_eval(json.dumps(autoBrand()))

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
			Message: %s
			""" % (form.name.data, form.email.data, form.message.data)
			mail.send(msg)

			return render_template('index.html', success=True)
		
	return render_template('index.html', form=form, number=number, products=products, loadMore=loadMore, brands=brands)

@app.route('/subscribe', methods=['POST'])
def subscribe():
	if request.form['email'] != "":
		email = Emails(email=request.form['email'])
		session.add(email)
		session.commit()
	return redirect(url_for('home'))

@app.route('/shop', methods=['GET','POST'])
def shop():
	products = session.query(ShopItems).all()
	return render_template('shop.html' , products = products)

@app.route('/about', methods=['GET','POST'])
def about():
	return render_template('about.html'	)

@app.route('/product/<id>',methods=['GET','POST'])
def product(id):
	product = session.query(ShopItems).filter_by(id=id).one()
	return render_template('product.html' , product=product)







# Admin Portal
@app.route('/admin',methods=['GET','POST'])
def adminSignin():
	if 'idAdmin' in login_session:
		admin = session.query(Admin).filter_by(id=login_session['idAdmin']).one()
		return redirect(url_for('admin'))

	if request.method == 'POST':
		username = request.form["username"]
		password = request.form["password"]
		
		adminCheck=session.query(Admin).filter_by(username=username).first()

		if(adminCheck != None and adminCheck.password==password):
			# Logged in successfully
			login_session['idAdmin'] = adminCheck.id
			return redirect(url_for('admin'))
		else:
			return redirect(url_for('adminSignin'))
	else:
		return render_template('adminSignin.html')


@app.route('/admin-panel-secret-login', methods=['GET','POST'])
def admin():
	if 'idAdmin' in login_session:
		products = session.query(ShopItems).all()
		emails = session.query(Emails).all()

		if request.method== 'POST':
			return render_template('admin.html', products=products, emails=emails)
		return render_template('admin.html' , products=products, emails=emails)
	else:
		return redirect(url_for('adminSignin'))


@app.route('/addProduct', methods=['GET','POST'])
def addProduct():
	if 'idAdmin' in login_session:
		if request.method == 'POST':
			name = request.form['name']
			gender = request.form['gender']
			brand = request.form['brand']
			price = request.form['price']
			description = request.form['description']
			thumbnail = "none"
			images = "none"

			product = ShopItems(name=name,gender=gender,brand=brand,description=description,price=price,thumbnail=thumbnail,images=images)
			session.add(product)
			session.commit()

			return redirect(url_for('admin'))

		return render_template('AddEditProduct.html')
	return redirect(url_for('adminSignin'))

@app.route('/editProduct/<id>', methods=['GET','POST'])
def editProduct(id):
	if 'idAdmin' in login_session:
		product = session.query(ShopItems).filter_by(id=id).one()

		if request.method == 'POST':
			name = request.form['name']
			gender = request.form['gender']
			brand = request.form['brand']
			price = request.form['price']
			description = request.form['description']
			thumbnail = "none"
			images = "none"

			product.name=name
			product.gender=gender
			product.brand=brand
			product.price=price
			product.description=description
			product.thumbnail=thumbnail
			product.images=images
			session.commit()

			return redirect(url_for('admin'))

		return render_template('AddEditProduct.html' , edit=True, product=product)
	return redirect(url_for('adminSignin'))

@app.route('/logout', methods=['GET','POST'])
def logout():
	if 'idAdmin' in login_session:
		del login_session['idAdmin']
	return redirect(url_for('adminSignin'))

@app.route('/copyEmails',methods=['GET','POST'])
def copyEmails():
	if 'idAdmin' in login_session:
		emails = session.query(Emails).all()

		emailsList=[]
		for email in emails:
			emailsList.append(str(email.email))

		emailsToCopy = ",".join(emailsList)

		pyperclip.copy(emailsToCopy)

		return redirect(url_for('admin'))
	else:
		return redirect(url_for('adminSignin'))



if __name__ == '__main__':
	app.run(debug=True)
