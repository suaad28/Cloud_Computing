from flask import render_template, url_for, redirect,  session, request
from PIL import Image
from app.forms import LoginForm,RegistrationForm, JobSearch
from app import wc
from app import aws
from app import webapp
from lambdafunc import lambda_function
import base64

@webapp.route('/')

@webapp.route('/login', methods=['GET', 'POST'])
def login():
    session["verified"] = False
    session["username"] = ""
    
    form = LoginForm()
    if form.validate_on_submit():
        username = str(form.username.data)
        password = str(form.password.data)
        aws_object =  aws.dynamodb()
        verify_status = aws_object.verify_username(username, password)

        if verify_status==1:
            print("Authentication Passed!")
            
            session["verified"] = True
            session["username"] = username

            return render_template("main.html")

        else:
            error="Authentication Failed!"
            return render_template("login.html", form=form, error=error)
    return render_template("login.html",form=form,error="")

@webapp.route('/search', methods=['GET', 'POST'])
def search():
    form = JobSearch()

    if form.validate_on_submit():
        url_parsed = 'https://ca.indeed.com/jobs?q=' + form.job_title.data + '&l=' + form.location.data
        print("before lambda event")

        event = {"username":session["username"], "url": url_parsed}
        

        #return the 200 for right 400 for bad
        res = lambda_function.lambda_handler(event,"")
        if res["status"] == 200:
            print("Yes!")
        else:
            print("No!")
        

        print("post lambda event")

        return redirect(url_for('invokebk'))
    return render_template('search.html', form=form)

@webapp.route('/invokebk', methods=['GET', 'POST'])

def invokebk():
    print("START TO RETRIVE IMAGE!")

    #dynamodb 
    #scraper_info: (username, list_str)

    #save wc_obj -> local & upload to s3 & delete 
    image_wc = session["username"] + "_wc.png" #"jason_wc.png"
    #image_hist = session["username"] + "_hist.png"
    
    ####################SAVE TO S3 BUCKET#####################

    dy_sess = aws.dynamodb()
    ret = dy_sess.get_info("scraper_info", "username", session["username"])
    list_str = ret["list_str"]

    print("++++++++++++")
    print(list_str)
    s3 = aws.s3_client()
    s3_name = "ece1779-bucket-a3"

    #WC
    wc_obj = wc.generate_wc(list_str)
    filename = "C:/Users/suaad/" + session["username"] + "_wc.jpeg"
    wc_obj.to_file( filename )
    #imgbody = open( filename, 'r' ).read()
    # file_content = base64.b64encode(imgbody)
    namee = session["username"] + "_wc.jpeg"

    print("trying to Upload to S3")
    s3.client.upload_file(filename, s3_name, namee)  
    
    print("Uploaded to S3")
    #s3.client.put_object(Body = imgbody, Bucket = s3_name, Key = namee)
    #wc.delete_path("/tmp/" + session["username"] + "_wc.png")
    
    #HIST

    # dict_str = {x:list_str.count(x) for x in list_str}
    # filename2 = "C:/Users/suaad/" + session["username"] + "_hist.jpeg"
    # namee2 = session["username"] + "_hist.jpeg"
    # print("Dict is ", dict_str)
    # bins = []
    # nums = []ß
    # for key, value in list_str.items():
    #     bins.append(key)
    #     nums.append(value)
    # plt.bar(bins, nums, 0.7)
    # plt.ylabel('Frequency')
    # plt.xlabel('Job Title')
    # plt.savefig(filename)
    
    # s3.client.upload_file(filename2, s3_name, namee2)
    # wc.delete_path(filename)
    


    #download again with d_ 
    #s3 = aws.s3_client()
    #s3.client.download_file(s3.bucketName, image_wc, "/tmp/d_" + image_wc)
    
    img_obj = s3.client.get_object(Bucket = s3_name, Key = namee )
    #print("Key is ", session["username"] + "_wc.png")
    #s3.client.download_file(s3.bucketName, image_hist, "/tmp/d_" + image_hist)
    #print(img_obj['Body'])
    file_content = base64.b64encode(img_obj['Body'].read()).decode()
    # img_obj2 = s3.client.get_object(Bucket = s3_name, Key = namee2 )
    #img_wc_path = "/tmp/d_" + image_wc
    #img_hist_path = "/tmp/d_" + image_hist

    #TODO: get the object
    return render_template('results.html', img_data2 = file_content)


@webapp.route('/register_page', methods=['GET', 'POST'])
def register_page():
    session["verified"] = False
    session["username"] = ""
  
    form2 = RegistrationForm()
    if form2.validate_on_submit():
        #print("hello")
        aws_object =  aws.dynamodb()
        username = str(form2.username.data)
        password = str(form2.password.data)
        aws_object.create_account(username, password)
        success="Your account has been created!"
        return render_template("login.html", form=form2, success=success)
    return render_template("register.html", form=form2,error="")