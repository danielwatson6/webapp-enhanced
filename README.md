# Webapp Enhanced
Webapp Enhanced is a library designed
to make python development with Google
App Engine easier. Currently, the library
only has basic features and is still
under development.

## Installing
To install, you may use pip or setuptools:

    pip install webapp-enhanced  # pip
    easy_install webapp-enhanced # setuptools

You may also clone this repository and run
`python setup.py install`

Webapp Enhanced also requires
[Python 2.7](https://www.python.org/download/releases/2.7),
[Google App Engine](https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python),
and [Jinja2](https://github.com/mitsuhiko/jinja2).

We strongly recommend using
and [HamlPy](https://github.com/jessemiller/HamlPy),
[CoffeeScript](http://coffeescript.org/#installation),
and [Sass](http://sass-lang.com/install). Support for other abstraction languages
is not yet supported, but it can be done manually.

## Getting started
Once installed, Webapp Enhanced can be
accessed in your console by using `we`.
The different commands can be seen by typing `we -h`.

### Creating the app
To create a new webapp, type `we -n [project name]`.
A new directory containing all the files will be created.

### Testing and deploying
To run the webapp on your machine, just type `we`. By default, it will run on
http://localhost:3000. To specify a port, use `we -t [port]` instead.

Your app can be deployed to google app engine by using `we -d`.
You must have the domain registered on appengine beforehand.
In `app.yaml`, you must put the domain in `application:` as well.
