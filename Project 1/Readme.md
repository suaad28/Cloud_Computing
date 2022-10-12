
 
## Project Summary

To create a website that allows users to upload an image with a corresponding key. Once uploaded, the key will be stored in a database. If an image with the same key exists, it will be replaced in the file system to reflect the new image. A list of all the available keys stored in the database is also displayed. Users can search for an image by entering a key from this list and the resulting image will be displayed. The front end also shows the current statistics for the mem-cache which is also stored in the database. 


## Features of the Front End
1.  Upload image with corresponding key
2.  Search for an image by entering key
3.  Display of Mem-cache statistics
4.  Changing the memcache size
5.  Refreshing the memcache configuration
6.  Changing the memcache policy
7.  Display of all keys in database

## Packages Required
1.  Python 3
2.  Flask
3.  Flask – render_template
4.  MySQL connector

All the packages can be installed using pip.


## Running the web application
1.  Assuming the MySQL server is connected, from the desktop, run ./start.sh to deploy the web application. The start.sh script exists on the home directory which is /home/ubuntu. The start.sh will create a folder in /home/ubuntu/images so that we can download the images. It will start the two flask  applications using gunicorn library.

## Functionality of the Code


![main_diagram](https://user-images.githubusercontent.com/80457657/195421537-2f672ef5-eca4-44ca-8d99-9da669913ada.PNG)

![put_request](https://user-images.githubusercontent.com/80457657/195422278-310ced93-235c-4e5f-aa98-bfa249b92ca2.PNG)

## Database Schema

We are using a remote MySQL server. 

The following images show the skeleton on the tables created in the database.
![image](https://user-images.githubusercontent.com/80457657/195425130-422f9a18-8b88-4f86-8593-f8d3747884ec.png)

![image](https://user-images.githubusercontent.com/80457657/195425581-226ab432-4a99-466b-b546-96642edbd72c.png)

## Users
1. Go to <IP:5000/> which opens the web page.
2. You can upload new images by clicking on the Upload button. On success, you will be directed to page with ‘Upload Done’ and the images will be saved on /home/ubuntu/saved_images
3. Alternatively, you can search for a particular key by entering the key parameter. If the entered key exists, the corresponding image will be displayed on the web page.
4. Users can change the memcache policy, memcache size and refresh the configuration to the default values as well.
 
## Developers
For developers, there are 2 main parts that are documented here: the frontend, and the backend.

### Web Frontend

The functions of each directory and file that are used in the frontend are listed here:

Templates – These are HTML templates that are used when each route is called. 

1. index.html - The is the main html file used for the web front end. It consists of form actions for various functions such as upload, find, refresh configurations, memcache capacity and policy change. It also displays the key entries which are being fetched from the database

2. display.html - This html is used to display the image when the corresponding key is entered. If for the entered key, an image does not exist, an error message is shown
3. go_back.html - This is used to give the user a convenient interface to go back to the main web page

4. upload.html - Interface to confirm that image upload is successful
 
### Backend

The backend uses two Flask instances; web_app and cache_app. Both instances communicate with the other to showcase the results.

For the web front end there exists a flask instance. The web_routes module contains all the routes (the different URLs) implemented in the application. The handlers for the application routes (URLs) are written in the form of Python functions commonly referred to as "view functions". The view functions are mapped to one or more URLs defined in the @app.route('URL') decorators above the view function. The @app.route decorator creates an association between the URL given as an argument and the view function. Each file with their respective functions is described below

All functions have two routes. One renders a html template and the other route (/api/<endpoints>) displays a json response for testing purposes.
	
1.  __init__.py – A ‘constructor’ module of sorts that runs every time the application is run. It instantiates a Flask instance 
2.  web_routes.py – This handles all the route requests from the website. A brief description of each route and function is given below:
	
	1. @web_app.route('/index')
    def index()   
This is the homepage of the web front end. It connects to the database and displays the current list of keys along with their local file system path, stored in the database

	2. @web_app.route('/upload', methods=['POST'])/
    def upload()  
This function handles uploading the image with its corresponding key. The key is fetched from the html form interface. The image is being converted to its bytes format which is saved as its “value”. A ‘post’ request is sent to the cache to ensure that there is enough memory. The function renders a template to show the success message and a convenient interface to go to the home page. The function also saves the uploaded image to the user's storage folder (the folder that gets created in the filesystem for the user during initialization).
The json response of this api endpoint will contain either success or failure. 

	3. @web_app.route('/key/', methods=['POST'])
    def key()
This function handles searching for an image by its corresponding key. The key is fetched from the html form interface. This function in turn sends a ‘get’ request to the  memcache. The get() searches for this specific key in the database. On a successful match, considered as a ‘hit’, the counter for the number of hits is incremented and a successful response is returned to the front end. If the status code reflects 200, its renders the ‘display.html’ which displays the corresponding image in a scaled width and height of 300x300. 
If an image does not exist for that particular key, it is considered as a ‘miss’  the counter for the number of misses is incremented and an unsuccessful response is returned to the front end. An error message is displayed. 
	
	4. @web_app.route('/cap',methods=['POST'])
    def cap()
This function handles the change in memcache capacity requested by the user. A post request is sent to memcache where the memcache size is changed. If the function detects a non-integer value, an error message is displayed.

	5. @web_app.route('/refresh',methods=['POST'])
    def refresh()
This function refreshes the memcache configuration back to its default values. The function sends a post request to the cache and resets the required values. On successful change, a message is displayed. 

3.  cache.py – This handles all the route requests from the front end flask instance. 
	1. @cache_app.route('/get',methods=['POST'])
def get():
This function tries to access images in memcache first. If the key is not found in memcache, it will try to find the path of those demanding images in the database. If those images are not in the database, this access will count as a miss. And the webpage will show “Unknown Key”. Otherwise, the action will be counted as a hit. With a hit access, the page will return the corresponding image. If the image is in mem cache,  it directly shows the value of the image. If the image is in the local disk, the function will read the path through the database ,read the path in the database and return the image on the local disk.

	2. @cache_app.route('/put',methods=['POST'])
def put():
The function tries to save images in mem cache with a unique key. The mem cache can be with random change or least recently used policy when the capacity is full. All information here will be stored in the database (id, key, path, size). The cache will hold all images if the capacity limit is not reached. When different images come to the mem cache with some existing key in the database. The function will search in the database for duplication and replace all information with new images. Old information and images on the local disk will be all replaced. For each of the following images, no matter the replace or new entry, the function will update available capacity dynamically.

	3. @cache_app.route('/refresh',methods=['POST'])
def refresh():
The function refreshes the cache settings and changes them back to the default values.

	4. @cache_app.route('/invalidate',methods=['POST'])
def invalidate():

This function nukes image information  in memcache and database. Once a function is called. The image information and local disk  with a specific key will all be gone.. 















