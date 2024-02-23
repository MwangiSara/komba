from flask import * 
import pymysql
import sms


app=Flask(__name__)

connect=pymysql.connect(host='localhost',user='root',password='',database='komba_soko_garden')
cursor = connect.cursor() #cursor() allows code to execute sql command in a database session
app.secret_key="mysecretkey" #we have to set secret key to secure our session/make it unique

@app.route('/')
def home():
    connect=pymysql.connect(host='localhost',user='root',password='',database='komba_soko_garden') #we are conncting to our database
    sql= "SELECT * FROM products WHERE product_category='Smartphones'"
    cursor=connect.cursor()
    cursor.execute(sql) #execute() helps to execute the query inside variable sql
    data=cursor.fetchall()
    #fetchall() is used to fetch all the remaing rows from the result set of a query. fetchmany(size=20) is used to fetch a specified number of rows fro the result set in the query, ie, 20. fetchone() is used to fetch a single row from the result set in the query

    #fetching electronics
    sql2="SELECT * FROM products WHERE product_category='Electronics'"
    cursor.execute(sql2)
    data2=cursor.fetchall()

    return render_template('index.html',category_smartphone=data,category_electronics=data2)

@app.route('/upload', methods=['POST','GET'])
def upload():
    #HERE WE ARE GOING TO CONNECT TO OUR DATABASE AND SEND/SUBMITT OUR DATA TO KOMBA_SOKO_GARDEN
    if request.method == 'POST':
        #we will be receiving variables sent/submitted from the form here
        product_name = request.form['product_name']
        product_desc = request.form['product_desc']
        product_cost = request.form['product_cost']
        product_category = request.form['product_category']
        product_image_name = request.files['product_image_name']
        product_image_name.save('static/images/'+product_image_name.filename) #saves the image file in images folder which is in static folder

        #connecting to database
        connect=pymysql.connect(host='localhost',user='root',password='',database='komba_soko_garden')
        cursor = connect.cursor() #cursor() allows code to execute sql command in a database session

        data = (product_name, product_desc,product_cost, product_category, product_image_name.filename) #we are preparing our data, so that we can send it to the database
        sql = "INSERT INTO products (`product_name`, `product_desc`, `product_cost`, `product_category`, `product_image_name`) VALUES (%s,%s,%s,%s,%s) " #%s is used as a placeholder to be replced by the data above
        cursor.execute(sql,data)
        connect.commit() #commit() writes changes to database
        return render_template('upload.html',message='Product Added Successfully')
    else:
        # below renders the template when a user accesses the /upload route, it shows the upload.html so that the user can input product details and POST/submit
        return render_template('upload.html',message='Please Add Poducts Details')

@app.route('/single_item/<product_id>')
def single_item(product_id):
    my_query='SELECT * FROM products WHERE product_id=%s'
    cursor.execute(my_query,product_id)
    product=cursor.fetchone()

    return render_template('single_item.html',my_product=product)

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        username=request.form['username']
        email=request.form['email']
        phone=request.form['phone']
        password1=request.form['password1']
        password2=request.form['password2']

        #validate our passwords
        if len(password1) <8:
            return render_template('signup.html',error='PASSWORD MUST BE MORE THAN 8 CHARACTERS')
        elif password1 != password2:
            return render_template('signup.html',error1='PASSWORDS DON\'T MATCH')
        else:
            sql='''INSERT INTO users (`username`, `password`, `email`, `phone`) VALUES (%s,%s,%s,%s)'''
            cursor.execute(sql,(username,password1,email,phone))
            connect.commit()
            
            sms.send_sms(phone, "Thank you for Registering")
            return render_template('signup.html',success='SUCCESSFULLY SIGNED UP')
        
    else:
        return render_template('signup.html')
    
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=="POST":
        username=request.form['username']
        password1=request.form['password1']

        login_query="SELECT * FROM users WHERE username= %s AND password= %s"
        cursor.execute(login_query,(username,password1))

        if cursor.rowcount == 0:
            return render_template('login.html',error='INVALID CREDENTIALS')
        else:
            session['key'] = username #we are linking the session key with the username
            return redirect('/')
    else:
        return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.clear() #we are clearing the session
    return redirect('/login')

@app.route('/mpesa',methods=['POST','GET'])
def mpesa():
    #request the amount and phone from single_item.html
    phone=request.form['phone']
    amount=request.form['amount']

    #import mpesa.py module
    import mpesa

    #call the stk_push function present in mpesa.py
    mpesa.stk_push(phone,amount)

    #return a message
    return '<h3>Please Complete Payment In Your Phone And We Will Deliver In Minutes</h3>'\
    '<a href= >Back To Home</a>'


if __name__=='__main__':
    app.run(debug=True)

