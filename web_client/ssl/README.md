# Configuring Ember to serve https

If you need to configure your Ember development server (`ember serve`) to serve
https requests, you can follow these steps.

If something in these instructions is not working correctly, you can refer to
[this web page](https://medium.com/@bantic/serving-ember-and-rails-locally-with-ssl-tls-44640f615b95)


## Step 1: Generate an RSA Private Key

* `openssl genrsa -des3 -passout pass:xxxx -out server.pass.key 2048`

Where `xxxx` is a character string of at least 4 characters.


## Step 2: Generate a Corresponding Public Key

* `openssl rsa -passin pass:xxxx -in server.pass.key -out server.key`

Where `xxxx` is the same string used to generate the private key.


## Step 3: Create a Self Signed Certificate

This step is a bit more involved, as the command will ask a bunch of questions.
The answers mostly don't matter too much except the server fully qualified
domain name (FQDN).

If you are running Ember locally on your PC then it needs to be `localhost`

```console
user@ORR: ~/temp  $ openssl req -new -key server.key -out server.csr
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:US
State or Province Name (full name) [Some-State]:WA
Locality Name (eg, city) []:Seattle
Organization Name (eg, company) [Internet Widgits Pty Ltd]:NOAA-ERD-ORR
Organizational Unit Name (eg, section) []:ORR
Common Name (e.g. server FQDN or YOUR name) []:localhost
Email Address []:orr.adios@noaa.gov

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:
user@ORR: ~/temp  $ 
```


## Step 4: Self Sign Your Certificate

* `openssl x509 -req -sha256 -days 365 -in server.csr -signkey server.key -out server.crt`

## Step 5: Clean Up the Unneeded Files

At this point you have the key and certificate files you need, but there are
extra files that have been created in the process that you don't need.
I don't think they hurt anything, but you can safely remove them.

* `rm server.pass.key`
* `rm server.csr`


## Step 6: Copy the Files to the Ember SSL Folder

The files we have created should be located in the same folder as this
document (`<ember-project>/ssl/`).  If they are somewhere else, then move them
here.


## Step 7: Start the Ember Development Server

Starting the Ember development server so that it uses the ssl configuration
is as easy as adding a command-line option.

* `cd <ember-project>`
* `ember serve --ssl=true`

...and that's it.  You should now have an Ember development server serving
https requests.
