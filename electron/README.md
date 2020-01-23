# README

This is the Electron client for the ADOIS oil DB program.

## Dependencies

nodejs:

```
conda install nodejs
```

(or get it from your system package manager, or ...)

Then a few things installed with npm:

```
    npm install electron
    npm install request
    npm install request-promise
    npm install dialog
	npm install --save electron-window-state
```

# running the app:

```
npm start
```

The Node main.js script works by starting each of the three dependencies:

* Python static file server
* MongoDB
* Python web_api server

It starts the servers in that order. For the static file server and the web_api server, it repeatedly tries to send an HTTP request to the server, and it only advances to the next once a response has been successfully received. When a successful response has been received from the web_api server, it opens the Electron browser window and the application starts.

----------------

To build the standalone electron app, follow the instructions on https://github.com/electron/electron-packager

(1) `npm install electron-packager -g`

(2) From the electron subdirectory: `electron-packager . --icon .\oil-barrel.ico`

(Note also that we've added "productName": "ADIOS Oil Database" to package.json.)

(Note also that "electron" has moved from "dependencies" to "devDependencies" because it is not needed for runtime because the builder uses a pre-made version of electron for distribution.)

This creates the folder ADIOS Oil Database-win32-x64 in the electron directory, which contains ADIOS Oil Database.exe and the files needed to run it.
