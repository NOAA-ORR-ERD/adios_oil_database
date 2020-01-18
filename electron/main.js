const path = require( "path" );
const childProcess = require( "child_process" );
var requestPromise = require( "request-promise" );
var dialog = require( "dialog" );
const electron = require( "electron" );
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const isMac = process.platform === 'darwin';

electron.crashReporter.start( { companyName: "NOAA", submitURL: "https://google.com" } );

var fileServerProcess = null;
var mongoDbProcess = null;
var webApiProcess = null;
var mainWindow = null;

app.on( "ready", AdvanceStartupSequence );

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
	else if ( mainWindow == null )
	{
		console.log( "AdvanceStartupSequence() calling OpenWindow()" );
		OpenWindow();
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
			
			AdvanceStartupSequence();
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
	
	fileServerProcess.on(
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
	
	let cwd = path.resolve( __dirname, ".." );
	webApiProcess = childProcess.spawn( "pserve",
										[ "--reload", "web_api/config-example.ini" ],
										{ cwd: cwd } );
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
			
			AdvanceStartupSequence();
		}
	)
	.catch(
		function( err )
		{
			console.log( "waiting for the web api server to start, attempt = " + numTries + " ..." );
			
			if ( numTries >= 10 )
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
	
	DefineApplicationMenu();
	mainWindow = new BrowserWindow( { width: 800, height: 600, icon: path.join( __dirname, "oil-barrel.ico" ) } );
	mainWindow.on(
		"closed",
		function()
		{
			mainWindow = null;
			KillChildProcesses();
		}
	);
	// mainWindow.loadURL( "file://" + __dirname + "/index.html" );
	mainWindow.loadURL( "http://localhost:8080" );
	// mainWindow.webContents.openDevTools();
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

function DefineApplicationMenu()
{
	const menu = electron.Menu.buildFromTemplate( menuTemplate );
	electron.Menu.setApplicationMenu( menu );
}
