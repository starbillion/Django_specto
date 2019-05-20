# DJ-Specto **(v 0.1.2)
This is a Django based project and is primarily focussed on stock-market data.

### Modules
1. users
   1. User login/registration (support for XMLHTTP Requests and HTTP Requests)
   2. For user registration, custom user model is used, to enable email based login
      and not relying on usernames(as offerred outof the box by Django)
   3. User Profile/management
   4. Considering the basic use cases, i have implemented an abstraction by adding a
      *helpers.py* file. For now just a wrapper method to authenticate users, calling 
      the native authenitication.
   5. On each login  attempt, user IP & some crucial login details are added, wcan be viewed
      from the account-settings page after loggin in.
2. mainisite
   1. The layouts used by all the other templates are defined here.
3. stocks
   1. Stocks have been added from a bunch of popular companies.(Most of them)
   2. The data being diplayed is realtime, and accurate, refer to(/stocks) page and inidvidual
      company stock page, eg. (/stocks/PIH)
   3. Stocks favourite list is under work will be added soon. 

##Installation Guide
1. Install dependecies using pip, eg. pip install -r requirements.txt (Recommended to use a virtualenv, works otherwise as well).  
    * Bug fix with the django cart package
    * Update file site-packages/cart/cart.py
    At line 2
    - *from . import models* in place of the import declaration.
    *** Update file site-packages/cart/models.py
    At line 27
    replacement cart = models.ForeignKey(Cart, verbose_name=_('cart'), on_delete=models.CASCADE)
    At line 31
    replacement content_type = models.ForeignKey(ContentType,  on_delete=models.CASCADE)

2. Update DB settings inside /mainsite/mainsite/settings.py, 

>  1. Comment out DATABASES (around line 80)
>  2. Comment out from line 89-96
>  3. Remove comments from line 83-86
>  4. This is so that you can easily switch to the native SqliteDB, making the process of 
     running the application hasslefree

3. Now the DB needs to be filled with the required tables, using DB-Migrations, run 
   below #3 commands in the order listed
    1.  python manage.py makemigrations
    3.  python manage.py makemigrations subscriptions users stocks payment favourites
    7.  python manage.py makemigrations
    8.  python manage.py migrate
    9.  python manage.py cities_light --force-import-all

4. python manage.py runserver

5. URLS: (I haven't set the default index url, as dev proceeds, will configure it)
   1. /login
   2. /register
   3. /users/profile
   4. /logout
   5. /stocks
   6. /stocks/PIH (stock code, can be accessed from /stocks page)


## For Ongoing Dev/Testing Help

## Make sure you perform a pip install -R requirements.txt(some dependecies might have been missing on your machine to run this update)

## SuperUser
1. Url to create a superuser(that can login to Django)
   1. /create/superuser
   2. The credentials will work for Admin login(Non-Django)
## setting email server

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'tmp/')
# now we are crating temp file for sending email. if we send emil, we should change the above setting to the following in settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'host address of email server'
EMAIL_PORT = 'port'
EMAIL_HOST_USER = 'your email of email address of your server'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_USE_TLS = True

## Expiration status of subscribed plans
Field "status" of table named "subscriptions_subscription" determines whether subscription is expired or not
If true, not expired
If false, expired

# Super admin 
python manage.py createsuperuser
In this project, when creating super user, is_staff is set with "false"
So, change the value of this field to "true"

## Registration
1. Registrations on the app have now been added with the feature to verify the email before 
   being able to login to the app and having fun.
2. Admin can enable/disable and set expiry time for the registration via /mainsite/mainsite/settings.py
   To enable/disable set C_USER_EMAIL_VERIFICATION_STATUS=True|False
   Set the expiry time for the token: C_EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS=Integer(denotes hours from the time of being registered, eg for token to expire in 2 days set value to 48)
3. For testing, try to register, and until deployment, emails are set to be output inside text file,
   this will be the place to find out the email with link to activate account just registered
   1. Uri for email: /mainsite/tmp
   2. You may try to use the link directly and verify email by visiting the link, 
   3. Sample link to activate will look like: 127.0.0.1:8000/users/registration/verify/HKDUZA9L1AB6OCU8GUNDL6LRLV64PI/
   4. Once visited and accoutn email verified, the link and the token expires.

## Set the colors of stock values such as low, high, close and accuracy
    available in settings.py
    LOW_COLOR = '#3775dd'
    HIGH_COLOR = '#fb00ff'
    CLOSE_COLOR = '#B9FFA8'
    ACCURACY_COLOR = '#716aca'
## Set the remaining days until being expired
    EXPIRED_DAY = 95

## Password Recovery
1. Password recovery has been added by simply specifying the registered email, and a link is generated and emailed to the user's registered email.
2. Confogurations available inside settings.py include
    1. C_USER_PASSWORD_RECOVERY_STATUS = True|False
    2. C_USER_PASSWORD_RECOVERY_EMAIL_SUBJECT='String'
    3. C_PASSWORD_RECOVERY_TOKEN_EXPIRY_HOURS = Integer
    4. C_PASSWORD_RECOVERY_SENDER='senders@email'
3. For testing, it resembles the registration process, same directory receives a email with instructions to recover password.

## Stock
1. Url: stocks/load-db
2. Visit the above url to load the stocks to DB.
3. CRUD for the stocks that will be supported for the site has been added.
4. Login to Admin(Non-Django Admin) to manage the stock.

## Secret Admin (Non-Django admin)
1. Url: /secret-admin
2. Credentials, django admin credentials(using /create/superuser link) 

## Note:
1. The architecture for email templates have been designed as modular, and each of the email notification we will be having for the site will be inside separate editable tempaltes(uri: /mainsite/templates/emails)
2. Login, Registration & Forgot Password are added with AJAX-feature.
3. Please try to re-create migrations, as there has been considerably a lot of DB tweaks and data added.
4. Country, Region, State has been added, with DB. Smart Location is added as well, but can be tested later when site is deploed on a real/actual server.
5. After DB updation using python manage.py migrate, perform the following:
   python manage.py cities_light (To setup the Location related data in DB, this may take around 10-12 minutes or so)

### Who do I talk to? ###
* Gurpreet Chahal
* fb.com/preetchaahal
* preetchaahal@outlook.com

### Resources ###
1. Bootstrap Form Wizard https://jsfiddle.net/yeyene/59e5e1ya/,
https://codepen.io/lukezak/pen/LVJRva
2. Cart https://github.com/bmentges/django-cart.git


### Deployment DOC ###

Secifically for Ubuntu 16+

1. Install Packages from the Ubuntu Repositories
    Django with Python 3  
      `
        sudo apt-get update
        sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
      `
2. Configure a Python Virtual Environment
    a. With virtualenv installed, we can start deploying our project. Create a directory where you wish to keep your project and move into the directory: 
      `
        sudo pip install virtualenv
        mkdir ~/venv
        cd ~/venv
        virtualenv -p python3 dj_specto_env
      `

3. Setup the project using GIT or direct uploads to any location, preferably, `/var/www/html`

4. Activate the above created virtualenv and install the dependencies related to the project.
    a. `
      cd ~/venv
      source dj_specto_env/bin/activate
    `
    b. `
      cd /var/www/html/dj_specto/mainsite
      pip3 install -r requirements.txt
    `

    c. Package Cart has a bug for Python3 and requires an update to the following core file
    `
      ~/venv/lib/python3.X/site-packages/cart/cart.py
      from cart.models import cart 
    `

5. Update the DB settings as per the requirements.

6. Add a new site configuration for VirtualEnvironment (Apache2)
    `
      sudo nano /etc/apache2/sites-available/de_specto.conf
      ################################################################
      Listen {PORT} ##
      #NameVirtualHost \*:{PORT}
      ## Use this if you run into socket errors on linux
      <VirtualHost *:{PORT}>
         WSGIDaemonProcess dj_specto python-home="/var/www/html/dj_specto/mainsite/venv" python-path="/var/www/html/dj_specto/mainsite/mainsite"
         WSGIProcessGroup dj_specto
         WSGIScriptAlias / "/var/www/html/dj_specto/mainsite/mainsite/wsgi.py"
         ## Use this section only when enabling https for bots app
         #SSLEngine on
         #SSLCertificateFile /path/to/www.example.com.cert
         #SSLCertificateKeyFile /path/to/www.example.com.key
         Alias /media "/var/www/html/dj_specto/mainsite/media"
         ErrorLog /var/log/apache2/dj_specto.log
         <Directory /"var/www/html/dj_specto/mainsite">
              Order deny,allow
              Allow from all
         </Directory>
         Alias /static "/var/www/html/dj_specto/mainsite/mainsite/static"
         <Directory "/var/www/html/dj-specto/mainsite/media">
              Order deny,allow
              Allow from all
         </Directory>
      </VirtualHost>
    `

7. Enable the configuraiton for the app
    `
      sudo a2ensite dj_specto
      systemctl reload apache2
    `

8. Make the project directory accessible by Apache2
    `
      sudo chown :www-data ~/path/to/project/dj_specto
      service apache2 restart
    `