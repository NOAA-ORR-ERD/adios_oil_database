const electron = require( "electron" );
// console.log( electron );
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
electron.crashReporter.start( { companyName: "NOAA", submitURL: "https://google.com" } );

var mainWindow = null;

app.on(
	"window-all-closed",
	function()
	{
		// if ( process.platform != "darwin" )
		{
			app.quit();
		}
	}
);

app.on(
	"ready",
	function()
	{
		var subpy = require( "child_process" ).spawn( "python", [ "./server.py" ] );
		// var subpy = require('child_process').spawn('./dist/server.exe');
		var rp = require( "request-promise" );
		var mainAddr = "http://localhost:5000";
		
		var OpenWindow = function()
		{
			mainWindow = new BrowserWindow( { width: 800, height: 600 } );
			// mainWindow.loadURL( "file://" + __dirname + "/index.html" );
			mainWindow.loadURL( "http://localhost:5000/index.html" );
			// mainWindow.webContents.openDevTools();
			mainWindow.on(
				"closed",
				function()
				{
					mainWindow = null;
					subpy.kill( "SIGINT" );
				}
			);
		};
		
		var StartUp = function()
		{
			// this call is just to make sure the server is up and responding
			rp( mainAddr )
			.then(
				function( htmlString )
				{
					console.log( "server started! htmlString = " + htmlString );
					OpenWindow();
				}
			)
			.catch(
				function( err )
				{
					console.log( "waiting for the server start..." );
					// potential stack overflow
					StartUp();
				}
			);
		};
		
		// fire!
		StartUp();
	}
);
