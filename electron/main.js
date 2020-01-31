const USE_INI_CONFIG = false;
const IS_INSTALLED_APPLICATION = false;

const path = require( "path" );
const childProcess = require( "child_process" );
const requestPromise = require( "request-promise" );
const dialog = require( "dialog" );
const windowStateKeeper = require( "electron-window-state" );
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
  		OpenWindow();
		AdvanceStartupSequence();
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

	let cwd = path.join( path.resolve( __dirname, ".." ), "StandAlone", "client_code" );
	let appPath = "python";
	if ( IS_INSTALLED_APPLICATION )
	{
		cwd = path.join( path.resolve( __dirname, "../../.." ), "oil_database", "StandAlone", "client_code" );
		appPath = "../../../adiosdb/python.exe";
	}
	fileServerProcess = childProcess.spawn( appPath,
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

	let cwd = path.resolve( __dirname, ".." );
	let appPath = "mongod";
	let configPath = "mongo_config_dev.yml";
	if ( IS_INSTALLED_APPLICATION )
	{
		cwd = path.join( path.resolve( __dirname, "../../.." ), "oil_database" );
		appPath = "../adiosdb/Library/bin/mongod.exe";
		configPath = "../oil_database/mongo_config_dev.yml";
	}
	
	mongoDbProcess = childProcess.spawn( appPath,
										 [ "-f", configPath ],
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
	let appPath = "python";
	if ( IS_INSTALLED_APPLICATION )
	{
		cwd = path.join( path.resolve( __dirname, "../../.." ), "oil_database", "web_api" );
		appPath = "../../adiosdb/python.exe";
	}
	if ( USE_INI_CONFIG )
	{
		webApiProcess = childProcess.spawn( "python",
											[ "start_server.py", "config-example.ini" ],
											{ cwd: cwd } );
	}
	else
	{
		webApiProcess = childProcess.spawn( appPath,
											[ "run_web_api.py", "standalone-config.json" ],
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
	// TODO: we can add the path to where the window state should be kept (in our data folder): https://github.com/mawie81/electron-window-state
	let mainWindowState = windowStateKeeper(
		{
			defaultWidth: 800,
			defaultHeight: 600
		}
	);
	mainWindow = new BrowserWindow(
					{
						x: mainWindowState.x,
						y: mainWindowState.y,
						width: mainWindowState.width,
						height: mainWindowState.height,
						icon: path.join( __dirname, "adiosdb.ico" ),
						title: "ADIOS Oil Database"
					} );
	mainWindowState.manage( mainWindow );
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
	// we don't need to kill the sub-processes because Node does it for us
	
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
