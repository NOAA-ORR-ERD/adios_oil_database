appGlobals =
	{
		ajaxSerialNumber: -1
	};

function Initialize()
{
	$( ".CalculateButton" ).click( HandleCalculateButtonClick );
	$( ".DownloadFileButton" ).click( HandleDownloadFileButtonClick );
	$( ".UploadFileButton" ).click( HandleUploadFileButtonClick );
}

function HandleCalculateButtonClick( e )
{
	var o =
		{
			a: $( ".A" ).val(),
			b: $( ".B" ).val()
		};
	
	CallAjaxFunction( "Calculate", o );
}

function HandleDownloadFileButtonClick( e )
{
	var e = $( "<a>Downloading...</a>" );
	var json = "{ \"a\": 1, \"b\": \"apple\" }";
	var blob = new Blob( [ json ], { type: "text/json" } );
	e.attr( "href", window.URL.createObjectURL( blob ) );
	e.attr( "download", "myfile.json" );
	$( "body" ).append( e );
	e[ 0 ].click();
	e.remove();
}

function HandleUploadFileButtonClick( e )
{
	let file = $( ".FileInput" )[ 0 ].files[ 0 ];
	// alert( file.path );
	// let formData = new FormData();
	// formData.append( "file", file );
	let reader = new FileReader();
	reader.onload = HandleFileLoad;
	reader.readAsText( file );
}

function HandleFileLoad( evt )
{
	$( ".FileText" ).text( evt.target.result );
	
	// CallAjaxFunction( "Calculate", o );
	// fetch( "/ajax", { method: "POST", body: formData } );
}

/////////////////////////////////////////////////////////////////////////////////////////////////////

function ExecuteJSONCommand( command )
{
	if ( command.action == "none" )
	{
		return;
	}
	
	// console.log( "ExecuteJSONCommand( " + command.action + ")" );
	switch ( command.action )
	{
		case "calculated":
		{
			$( ".Sum" ).text( command.hasOwnProperty( "sum" ) ? command.sum.toString() : "" );
			$( ".Quotient" ).text( command.hasOwnProperty( "quotient" ) ? command.quotient.toString() : "" );
			$( ".String" ).text( command.string );
			break;
		}
		
		case "show-error":
		{
			alert( command.message );
		}
	}
}

/////////////////////////////////////////////////////////////////////////////////////////////////////

function CallAjaxFunction( operation, postData )
{
	appGlobals.ajaxSerialNumber += 1;
	
    var n = appGlobals.ajaxSerialNumber;
    /*
	if ( !useAjaxSerialNumber )
    {
        n = -1;
    }
	*/
	postData.operation = operation;
	postData.ajaxSerialNumber = n;
    $.ajax( {
		type: "POST",
		dataType: "text",
        data: JSON.stringify( postData ),
        contentType: "text",
        // processData: false,
		url: "ajax",
		success:
			function( jsonText )
			{
				ExecuteJSONCommands( jsonText );
			},
		error:
			function( jqXHR, textStatus, errorThrown )
			{
                var s = "";
                for ( var k in jqXHR )
                {
                    if ( s != "" )
                    {
                        s += ", ";
                    }
                    s += k + " = " + String( jqXHR[ k ] ).substring( 0, 32 ) + "\r\n";
                }
				// GuiAlert( "error in CallAjaxFunction for function " + functionAndParameters + ": " + s + ", " + textStatus + ", " + errorThrown );
				// if ( !functionAndParameters.startsWith( "Poll" ) )
				{
					alert( "Unable to communicate with the server: " + s );
				}
			}
	} );
}

function ExecuteJSONCommands( jsonText )
{
	// var data = json_parse( jsonText );
	var data;
	
	try
	{
		if ( jsonText != "[ { \"action\": \"none\" } ]" )
		{
			console.log( jsonText );
		}
		
		// NOTE: this could be done more safely using a JSON parser,
		// but the two JSON parsers I found were buggy
		// data = jsonParse( jsonText );
		data = eval( "(" + jsonText + ")" );
	}
	catch ( e )
	{
		console.log( "unable to parse json text: " + jsonText + "; error = " + e );
		
		return;
	}
	
	var n = data.length;
	for ( var i = 0 ; i < n ; i++ )
	{
		ExecuteJSONCommand( data[ i ] );
	}
}
