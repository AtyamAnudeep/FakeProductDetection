import os
import sys
import numpy as np
import cv2
import sys
from flask import Flask, render_template, request,redirect,url_for
from werkzeug import secure_filename
import qrtools
from flask_mail import Mail, Message
app = Flask(__name__)
resize_w = 8
resize_h = 8

#Source: http://www.hackerfactor.com/blog/?/archives/432-Looks-Like-It.html

# We define all redeable files
dict = {"bottle.jpg":"bottle","lay.jpg":"lays"}

accepted = ['jpg','jpeg', 'png', 'tif','tiff', 'bmp']

@app.route('/upload',methods=['GET','POST'])
def upload_file1():
	if request.method=="POST":
		return render_template('upload_h.html')
		# flash('enter correct details')
		#return redirect(url_for('main1'))


def average2D(table2D):
	n = 0
	s = 0
	for i in table2D:
		s += len(i)
		for j in i:
			n += j
	return (n*1.0/s)

def hashTableA(table2D, averageHash):
	for i in range(0, len(table2D)):
		for j in range(0, len(table2D[i])):
			if (table2D[i][j] > averageHash):
				table2D[i][j] = '1'
			else:
				table2D[i][j] = '0'
	return (table2D)

def hashTableD(table2D):
	for i in range(0, len(table2D)):
		for j in range(0, len(table2D[i])-1):
			if (table2D[i][j] > table2D[i][j+1]):
				table2D[i][j] = 1
			else:
				table2D[i][j] = 0
	table2D = np.delete(table2D,np.s_[-1:],1)
	return (table2D)

def concatenation(table2D):
	table2D = [ y for x in table2D for y in x]
	table2D = ''.join(str(int(i)) for i in table2D)
	table2D = int(table2D, 2)
	table2D = hex(table2D)
	return table2D[2:-1]

def match(hash1, hash2):
	if hash1 == '':
		hash1 = '0'
	if hash2 == '':
		hash2 = '0'
	hex1 = int(hash1, 16)
	hex2 = int(hash2, 16)

	size = len(hash2) if hash1 <= hash2 else len(hash1)
	size *= 4
	similitude = (hex1 ^ hex2)
	similitude = bin(similitude)[2:]
	similitude = similitude.count('0') + size-len(similitude)
	

	percentage = similitude*100.0/size
	return percentage

def checkImage(img1, img2, path1, path2):
	if ((img1 is None) or (img2 is None)):
		if (img1 is None):
			print ("Error: " + path1 + " is not an image")
		if (img2 is None):
			print ("Error: " + path2 + " is not an image")
		sys.exit()

def aHash(path1,path2):
	# Import images
	# img1 = cv2.imread(path1)
	img1 = path1
	img2 = cv2.imread(path2)
	checkImage(img1, img2, path1, path2)

	# Resize them to 8x8
	img1resize = cv2.resize(img1, (resize_w, resize_h)) 
	img2resize = cv2.resize(img2, (resize_w, resize_h)) 

	# Change color to black and white	
	img1resize = cv2.cvtColor( img1resize, cv2.COLOR_BGR2GRAY );
	img2resize = cv2.cvtColor( img2resize, cv2.COLOR_BGR2GRAY );

	# Calculate average color value
	img1average = average2D(img1resize)
	img2average = average2D(img2resize)

	# Hash the image with the average color value
	img1hashed = hashTableA(img1resize, img1average)
	img2hashed = hashTableA(img2resize, img2average)

	# Generage the hash Value
	img1value = concatenation(img1hashed)
	img2value = concatenation(img2hashed)

	# Calculate the match between the two hash (in % )
	matching = match(img1value, img2value)
	print("Method A: " + str(round(matching, 2)) + "% match")
	return str(round(matching, 2))


def pHash(path1,path2):
	# Import images
	# img1 = cv2.imread(path1)
	img1 = path1
	img2 = cv2.imread(path2)
	checkImage(img1, img2, path1, path2)

	# Resize them to 8x8
	img1resize = cv2.resize(img1, (resize_w, resize_h)) 
	img2resize = cv2.resize(img2, (resize_w, resize_h)) 

	# Change color to black and white	
	img1resize = cv2.cvtColor( img1resize, cv2.COLOR_BGR2GRAY );
	img2resize = cv2.cvtColor( img2resize, cv2.COLOR_BGR2GRAY );

	# Calculate the DCT
	img1dct = cv2.dct(np.float32(img1resize)/255.0)
	img2dct = cv2.dct(np.float32(img2resize)/255.0)

	#Calculate average DCT
	img1avdct = average2D(img1dct)
	img2avdct = average2D(img1dct)

	#Hash the DCT
	img1dcthash = hashTableA(img1dct, img1avdct)
	img2dcthash = hashTableA(img2dct, img2avdct)

	# Generage the hash Value
	img1value = concatenation(img1dcthash)
	img2value = concatenation(img2dcthash)

	# Calculate the match between the two hash (in % )
	matching = match(img1value, img2value)
	print("Method P: " + str(round(matching, 2)) + "% match")
	return str(round(matching, 2))
	
def dHash(path1,path2):
	# Import images
	error = False
	# img1 = cv2.imread(path1)
	img1 = path1
	img2 = cv2.imread(path2)
	checkImage(img1, img2, path1, path2)

	# Resize them to 9x8
	img1resize = cv2.resize(img1, (resize_w+1, resize_h)) 
	img2resize = cv2.resize(img2, (resize_w+1, resize_h)) 

	# Change color to black and white	
	img1resize = cv2.cvtColor( img1resize, cv2.COLOR_BGR2GRAY );
	img2resize = cv2.cvtColor( img2resize, cv2.COLOR_BGR2GRAY );

	# Hash the image with the average next color value (8x8)
	img1hashed = hashTableD(img1resize)
	img2hashed = hashTableD(img2resize)

	# Generage the hash Value
	img1value = concatenation(img1hashed)
	img2value = concatenation(img2hashed)

	# Calculate the match between the two hash (in % )
	matching = match(img1value, img2value)
	print("Method D: " + str(round(matching, 2)) + "% match")
	return str(round(matching, 2))

def errorInput():
	print("Pleaser enter arguments as follow : image1, image2, algorithm")
	print('For the algorithm, you may use:')
	print("# 'a', Using the Average Hash algorithm (ahash)")
	print("# 'p' Using the Average Hash Perceptive (phash)")
	print("# 'd' Using the Difference Hash algorithm (dhash)")
	print("# 'all' for using all of the above")
	print("The images format accepted are 'jpg','jpeg', 'png', 'tif','tiff', 'bmp' ")

@app.route('/uploader', methods = ['GET', 'POST'])
def main():
	# if len(sys.argv) < 3:
	# 	errorInput()
	# 	sys.exit()

	# elif len(sys.argv) == 3:
	# 	arg3 = 'all' # hash algorithm

	# elif len(sys.argv) == 4:
	# 	arg3 = sys.argv[3] # hash algorithm

	# else:
	# 	errorInput()
	# 	sys.exit()
	# if request.method == 'POST':
	f1 = request.files['file1']
	f2 = request.form['f2']
	# print(f2)
	#f1 = f1 [13:]
	
	#f1 =f1[12:]
  	# print(f1.filename)
  	# print(f2)
  #   else:
		# errorInput()
		# sys.exit()  	
	# arg1 = sys.argv[1] # Picture 1
	# arg2 = sys.argv[2] # Picture 2
	npimg = np.fromstring(f1.read(),np.uint8)
	arg1 = cv2.imdecode(npimg,cv2.IMREAD_COLOR)

	# arg1 = f1.filename
	arg2 = str(f2)	
	print("--------------------------------")
	print(arg1)
	print(arg2)
	print("--------------------------------")
	arg3 = 'all'
	# print(arg1)
	# if (os.path.isfile(arg1) * os.path.isfile(arg2) == False):
	# 	if (os.path.isfile(arg1) * os.path.isfile(arg2) == False):
	# 		print("Image " + arg1 +" not found")
	# 	if (os.path.isfile(arg1) * os.path.isfile(arg2) == False):
	# 		print("Image " + arg2 +" not found")
	# 	sys.exit()

	if arg3 == 'a':
		a = aHash(arg1, arg2)
		return render_template('result.html',ans=a)
	elif arg3 == 'p':
		p = pHash(arg1, arg2)
		return render_template('result.html',ans=p)
	elif arg3 == 'd':
		d = dHash(arg1, arg2)
		return render_template('result.html',ans=d)

	elif arg3 == 'all':
		a1 = aHash(arg1, arg2)
		a2 = pHash(arg1, arg2)
		a3 = dHash(arg1, arg2)
		print(a1+a2+a3)
		a4=((float)(a1)+(float)(a2)+(float)(a3))/3
		print(a4)
		if ((float)(a4) > (75.00)):
			return render_template('result11.html',a4=a4,var = "original")
		else:
			return render_template('result11.html',a4=a4,var = "fake")	
	else:
	 	print ("Error in input algorithm argument !")
		# errorInput()
		# sys.exit()
	print ("Done !")
	return "enter some algorithm"





@app.route('/original',methods=['POST','GET'])
def dir_listing():
    BASE_DIR = 'static/Data/Categories'
    # req_path = ''
    # Joining the base and the requested path
    abs_path = BASE_DIR+'/'+request.form['cat']+'/'+request.form['brand']#os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)


    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('upload_h.html', files=files, path=abs_path)


@app.route('/',methods=['POST','GET'])
def main1():
	return render_template('index1.html')

@app.route('/barcode',methods=['POST','GET'])
def barcode1():
	print('enter barcode')
	return render_template('bar.html')	

@app.route('/decodebar',methods=['POST','GET'])
def barcode2():
	print('decode barcode')
	qr=qrtools.QR()
	b = request.files['bar1']
	b = b.filename
	print(b)
	qr.decode(b)
	if(qr.decode(b)==True):
		bar = qr.data
	if(qr.data in dict.values()):
		temp="Original Product"
		return render_template('displaybar.html',bar=bar,temp=temp)
	else:
		temp="Duplicate Product or not Present in the database"
		return render_template('displaybar.html',bar=bar,temp=temp)
		
	

@app.route('/sendmail')
def sendmail():
	return render_template('mail.html')

@app.route('/mailsent',methods=['POST','GET'])
def mailsent():
	if request.method=='POST':
		print('mailsent')
		app.config['MAIL_SERVER']='smtp.gmail.com'
		app.config['MAIL_PORT'] = 465
		app.config['MAIL_USERNAME'] = 'atyamanudeep7@gmail.com'
		app.config['MAIL_PASSWORD'] = 'Deepu@98'
		app.config['MAIL_USE_TLS'] = False
		app.config['MAIL_USE_SSL'] = True
		mail = Mail(app)
		img = request.files['absentimg']
		print(img)
		abimg = img.filename
		sendtext = request.form['sendtext']
		msg = Message('Request to add', sender = 'atyamanudeep7@gmail.com', recipients = ['atyam.anudeep@gmail.com'])
		msg.body=sendtext
		print(msg.body)
		with app.open_resource(abimg) as fp:
			print(abimg)
			msg.attach(abimg,"image/png",fp.read())
		mail.send(msg)
		return render_template('mailsent.html')
@app.route('/home',methods=['POST','GET'])
def home():
	if request.method=='POST':
		if request.form['uname']=='admin':
			if request.form['psd']=='admin':
				print('after login')
				print('home entered')
				return render_template('home.html')	

if __name__ == '__main__':
   app.run(debug = True)
