# OilDatabaseClient
===================

Javascript client that uses the OilDatabaseAPI to manage the NOAA  Oil Database
from a web browser.

## Application Requirements
* [OilDatabaseAPI Server](../web_api)
* [OilDatabase](../oil_db)

## System Requirments
* [Node.js](http://nodejs.org/)
* [npm](http://www.npmjs.org/)
* grunt-cli
* Some form of http server, webroot set to `./dist/build` and directory index set to `build.html` (created after running `grunt build`)

## Commands
`npm install`
> Installs all of the applications dependencies described in `package.json`. Calls `grunt install` upon completion.

`grunt install`
> Installs all client side dependancies from bower.

`grunt develop`
> Sets up a working development environment by reinstalling client side dependancies, compiling less files, starting a http server on port 8080, and setting up a watch task for the less to recompile on change.

`grunt build`
> Builds a compiled version of the application into a single index.html file (marginally supported currently, still has a few external image and font dependancies that are relatively pathed) located in `./dist/build/`.

`grunt build:lite`
> Simpler version of `grunt build`, sets up the applcation for requirejs based dynamic builds.

`grunt serve`
> Starts a http server on port 8080 for serving dynamic builds.

`grunt docs`
> Generate JSDoc based documentation. Located in `./dist/docs`.

`grunt lint`
> Runs jshint over application source files

`grunt test`
> Runs jshint over application source files, followed by a series of selenium tests. (Only works if you have a working client on your system running at `http://localhost:8080`).

`grunt test:demos`
> Similar to `grunt test` but only runs use case specific demo tests.
