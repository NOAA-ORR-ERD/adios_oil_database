const USE_INI_CONFIG = true;

const path = require( "path" );
const childProcess = require( "child_process" );
const requestPromise = require( "request-promise" );
const dialog = require( "dialog" );
console.log(require.resolve('electron'))
const electron = require( "electron" );
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const isMac = process.platform === 'darwin';

// https://www.electronjs.org/docs/api/app#apprequestsingleinstancelock
const gotTheLock = app.requestSingleInstanceLock()
if ( !gotTheLock )
{
	app.quit();
}
else
{

electron.crashReporter.start( { companyName: "NOAA", submitURL: "https://response.restoration.noaa.gov/" } );

var fileServerProcess = null;
var mongoDbProcess = null;
var webApiProcess = null;
var mainWindow = null;

/*
const ref = require( "ref" );
const ffi = require( "ffi" );

var voidPtr = ref.refType( ref.types.void );
var stringPtr = ref.refType( ref.types.CString );

var user32 = ffi.Library(
	"user32.dll",
	{
		// EnumWindows : ['bool', [voidPtr, 'int32']],
		FindWindowW : [ "int", [ "string", "string"] ],
		// ShowWindow : ['int', ['int', 'int']],
		// CloseWindow  : ['long', ['long']],
		// GetWindowTextA  : ['long', ['long', stringPtr, 'long']],
		// GetWindowTextLengthA  : ['long', ['long']],
		// IsWindowVisible  : ['long', ['long']],
		// FindWindowW : ['int', ['string', 'string']],
		// ShowWindow : ['int', ['int', 'int']]
	}
);

function TEXT( text )
{
	return new Buffer( text, "ucs2").toString( "binary" );
}

function FindWindow( name )
{
	var text = TEXT( name );
	var handle = 0;

	//ensure accurate reading, sometimes returns 0 when window does exist
	for (var i = 0 ; i < 50 ; i++ )
	{
		handle = user32.FindWindowW( null, text );
		if ( handle != 0 )
		{
			break;
		}
	}

	return handle;
}
*/

// https://www.electronjs.org/docs/api/app#apprequestsingleinstancelock
app.on(
	"second-instance",
	function ( event, commandLine, workingDirectory )
	{
		// Someone tried to run a second instance, we should focus our window.
		if ( mainWindow != null )
		{
			if ( mainWindow.isMinimized() )
			{
				mainWindow.restore();
			}
			mainWindow.focus();
		}
	}
);

app.on(
	"ready",
	function()
	{
		/*
		if ( FindWindow( "Task Manager" ) != 0 )
		{
			dialog.err( "The program is already running.",
						"ADIOS Oil Database Error",
						function( code )
						{
							app.quit();
						}
			);
		}
		else
		*/
		{
			OpenWindow();
			AdvanceStartupSequence();
		}
	}
);

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

function AdvanceStartupSequence()
{
	console.log( "AdvanceStartupSequence()" );

	if ( fileServerProcess == null )
	{
		console.log( "AdvanceStartupSequence() calling StartFileServerProcess()" );
		StartFileServerProcess();
	}
	else if ( mongoDbProcess == null )
	{
		console.log( "AdvanceStartupSequence() calling StartMongoDbProcess()" );
		StartMongoDbProcess();
	}
	else if ( webApiProcess == null )
	{
		console.log( "AdvanceStartupSequence() calling StartWebApiProcess()" );
		StartWebApiProcess();
	}
	else if ( mainWindow != null )
	{
		console.log( "AdvanceStartupSequence() navigating to the application url" );
		// mainWindow.loadURL( "file://" + __dirname + "/index.html" );
		DefineFullApplicationMenu();
		mainWindow.loadURL( "http://localhost:8080" );
		// mainWindow.webContents.openDevTools();
	}
}

function StartFileServerProcess()
{
	console.log( "StartFileServerProcess()" );

	let cwd = path.join( path.resolve( __dirname, ".." ), "web_client", "dist" );
	fileServerProcess = childProcess.spawn( "python",
											[ "-m", "http.server", "8080" ],
											{ cwd: cwd } );
	fileServerProcess.on(
		"error",
		( err ) =>
			{
				QuitWithErrorMessage( "Failed to start the file server process." );
			}
	);
	// fileServerProcess.stdout.pipe( process.stdout )
	// fileServerProcess.stdout.on( "data", ( data ) => { console.log( "fileServerProcess: " + data ); } );

	TryToCallFileServer( 0 );
}

function TryToCallFileServer( numTries )
{
	console.log( "TryToCallFileServer() numTries = " + numTries );

	requestPromise( "http://localhost:8080" )
	.then(
		function( htmlString )
		{
			console.log( "file server started! (received HTML string of length " + htmlString.length + ")" );

			setTimeout( () => { AdvanceStartupSequence(); }, 0 );
		}
	)
	.catch(
		function( err )
		{
			console.log( "waiting for the file server to start, attempt = " + numTries + " ..." );

			if ( numTries >= 10 )
			{
				QuitWithErrorMessage( "Unable to call the file server process." );
			}
			else
			{
				setTimeout( () => { TryToCallFileServer( numTries + 1 ); }, 1000 );
			}
		}
	);
}

function StartMongoDbProcess()
{
	console.log( "StartMongoDbProcess()" );

	cwd = path.resolve( __dirname, ".." );
	mongoDbProcess = childProcess.spawn( "mongod",
										 [ "-f", "mongo_config_dev.yml" ],
										 { cwd: cwd } );

	// var subpy = require('child_process').spawn('./dist/server.exe');

	mongoDbProcess.on(
		"error",
		( err ) =>
			{
				QuitWithErrorMessage( "Failed to start the database process." );
			}
	);

	setTimeout( AdvanceStartupSequence, 250 );
}

function StartWebApiProcess()
{
	console.log( "StartWebApiProcess()" );

	let cwd = path.join( path.resolve( __dirname, ".." ), "web_api" );
	if ( USE_INI_CONFIG )
	{
		webApiProcess = childProcess.spawn( "python",
											[ "start_server.py", "config-example.ini" ],
											{ cwd: cwd } );
	}
	else
	{
		webApiProcess = childProcess.spawn( "python",
											[ "run_web_api.py", "stand_alone_config.json" ],
											{ cwd: cwd } );
	}
	
	webApiProcess.on(
		"error",
		( err ) =>
			{
				QuitWithErrorMessage( "Failed to start the web API process." );
			}
	);

	TryToCallWebApiServer( 0 );
}

function TryToCallWebApiServer( numTries )
{
	console.log( "TryToCallWebApiServer() numTries = " + numTries );

	requestPromise( "http://localhost:9898/categories" )
	.then(
		function( jsonString )
		{
			console.log( "web api server started! (received JSON string of length " + jsonString.length + ")" );

			setTimeout( () => { AdvanceStartupSequence(); }, 0 );
		}
	)
	.catch(
		function( err )
		{
			console.log( "waiting for the web api server to start, attempt = " + numTries + " ..." );

			if ( numTries >= 20 )
			{
				QuitWithErrorMessage( "Unable to call the web api server process." );
			}
			else
			{
				setTimeout( () => { TryToCallWebApiServer( numTries + 1 ); }, 1000 );
			}
		}
	);
}

function OpenWindow()
{
	console.log( "OpenWindow()" );

	DefineEmptyApplicationMenu();
	mainWindow = new BrowserWindow(
					{
						width: 800,
						height: 600,
						icon: path.join( __dirname, "oil-barrel.ico" ),
						title: "ADIOS Oil Database"
					} );
	mainWindow.on(
		"closed",
		function()
		{
			mainWindow = null;
			KillChildProcesses();
		}
	);

	let p = path.join( __dirname, "startup.html" );
	mainWindow.loadURL( "file://" + p );
};

function QuitWithErrorMessage( message )
{
	console.log( "QuitWithErrorMessage() message = " + message );

	dialog.err( message,
				"ADIOS Oil Database Error",
				function( code )
				{
					KillChildProcesses();
					app.quit();
				}
	);
}

function KillChildProcesses()
{
	if ( fileServerProcess != null )
	{
		// fileServerProcess.kill( "SIGINT" );
		fileServerProcess = null
	}
	if ( mongoDbProcess != null )
	{
		// mongoDbProcess.kill( "SIGINT" );
		mongoDbProcess = null;
	}
	if ( webApiProcess != null )
	{
		// webApiProcess.kill( "SIGINT" );
		webApiProcess = null;
	}
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////

const menuTemplate = [
  // { role: 'appMenu' }
  ...(isMac ? [{
    label: app.name,
    submenu: [
      { role: 'about' },
      { type: 'separator' },
      { role: 'services' },
      { type: 'separator' },
      { role: 'hide' },
      { role: 'hideothers' },
      { role: 'unhide' },
      { type: 'separator' },
      { role: 'quit' }
    ]
  }] : []),
  // { role: 'fileMenu' }
  {
    label: 'File',
    submenu: [
      isMac ? { role: 'close' } : { role: 'quit' }
    ]
  },
  // { role: 'editMenu' }
  {
    label: 'Edit',
    submenu: [
      { role: 'undo' },
      { role: 'redo' },
      { type: 'separator' },
      { role: 'cut' },
      { role: 'copy' },
      { role: 'paste' },
      ...(isMac ? [
        { role: 'pasteAndMatchStyle' },
        { role: 'delete' },
        { role: 'selectAll' },
        { type: 'separator' },
        {
          label: 'Speech',
          submenu: [
            { role: 'startspeaking' },
            { role: 'stopspeaking' }
          ]
        }
      ] : [
        { role: 'delete' },
        { type: 'separator' },
        { role: 'selectAll' }
      ])
    ]
  },
  // { role: 'viewMenu' }
  {
    label: 'View',
    submenu: [
      // { role: 'reload' },
      // { role: 'forcereload' },
      { role: 'toggledevtools' },
      { type: 'separator' },
      { role: 'resetzoom' },
      { role: 'zoomin' },
      { role: 'zoomout' },
      { type: 'separator' },
      { role: 'togglefullscreen' }
    ]
  },
  // { role: 'windowMenu' }
  {
    label: 'Window',
    submenu: [
      { role: 'minimize' },
      { role: 'zoom' },
      ...(isMac ? [
        { type: 'separator' },
        { role: 'front' },
        { type: 'separator' },
        { role: 'window' }
      ] : [
        { role: 'close' }
      ])
    ]
  },
  {
    role: 'help',
    submenu: [
      {
        label: 'Learn More',
        click: async () => {
          // const { shell } = require('electron');
          await electron.shell.openExternal( "https://electronjs.org" );
        }
      }
    ]
  }
];

function DefineEmptyApplicationMenu()
{
	const menu = electron.Menu.buildFromTemplate( [] );
	electron.Menu.setApplicationMenu( menu );
}

function DefineFullApplicationMenu()
{
	const menu = electron.Menu.buildFromTemplate( menuTemplate );
	electron.Menu.setApplicationMenu( menu );
}

}
