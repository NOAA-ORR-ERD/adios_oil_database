# README

This is a sample Electron app wrapping a Python server.

In this case, a flask app.

## Dependencies

nodejs: `conda install nodejs`

(or get it from your system package manager, or ...)

Then a few things installed with npm:

```
    npm install electron
    npm install request
    npm install request-promise
```

On the Python side:

python 3.7 (probably any python3 will do)

flask: `conda install flask` or `pip install flask`

# running the app:

`npm start`

should do it.

You can also run the flask app by itself with:

`python server.py`

And point your browser to: http://localhost:5000/index.html






