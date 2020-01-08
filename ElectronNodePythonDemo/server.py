# from __future__ import print_function
import os
import json
# import time
from flask import Flask, jsonify, request, Response

app = Flask( __name__ )

"""
@app.route('/')
def hello():
	return "Hello from Python!"

@app.route( "/<path:path>" )
def send( path ):
	app.send_static_file( path )
"""

@app.route( "/", defaults = { "path": "" }, methods = [ "GET", "POST" ] )
@app.route( "/<path:path>", methods = [ "GET", "POST" ] )
def Handle( path ):
	print( "the path is " + path )
	
	if ( path == "" ):
		return Response( "Hello from Python!", mimetype = "text/plain" )
	
	if ( path == "ajax" ):
		return Response( HandleAjax( request ), mimetype = "text/xml" )
	
	with open( path, "rb") as f:
		content = f.read()
	
	fileName, extension = os.path.splitext( path )
	
	mimeType = "text/" + extension[ 1 : ]
	print( "the mimeType is " + mimeType )
	
	return Response( content, mimetype = mimeType )

def HandleAjax( r ):
	print( "handling ajax" )
	s = r.data.decode( "utf-8" )
	d = json.loads( s )
	print( "operation = " + d[ "operation" ] )
	actions = []
	
	if ( d[ "operation" ] == "Calculate" ):
		a = float( d[ "a" ] )
		b = float( d[ "b" ] )
		sumN = a + b
		if ( b == 0 ):
			actions.append( { "action": "show-error", "message": "cannot divide by zero" } )
		else:
			quotientN = a / b
			if ( sumN < quotientN ):
				s = "the sum is less than the quotient"
			else:
				s = "the sum is not less than the quotient"
			
			actions.append( { "action": "calculated", "sum": sumN, "quotient": quotientN, "string": s } )
	
	else:
		actions.append( { "action": "show-error", "message": "unknown operation" } )
	
	return json.dumps( actions )

if __name__ == "__main__":
    print( "oh hello" )
    #time.sleep(5)
    app.run( host = "127.0.0.1", port = 5000 )
