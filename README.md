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

### Testing
To run the webapp on your machine, just type `we`. By default, it will run on
http://localhost:3000. To specify a port, use `we -t [port]` instead.

### Using HamlPy, CoffeeScript, and Sass
Webapp Enhanced has support for these languages. If you are not using HamlPy, we seriously recommend it.
As of now, HamlPy is required to use the `we -g`, which will be explained later in detail.

The command `we -c` compiles everything in `abstract/` and accordingly updates the `views/` directory. Although there is no watch command yet, here's a simple example to do the job:

    # In your .bash_profile or .bashrc
    
    we_watch () {
    while :
    do
        we -c   # Compile
        sleep 1
    done
    }

### Architecture
Webapp Enhanced uses an MVC (model-view-controller) structure, RESTful methods, and DRY code (don't repeat yourself).

After creating a project, you will notice the following structure inside:

    abstract/
    assets/
    controllers/
    lib/
    models/
    views/
    
    app.yaml
    main.py

#### Main script and configuration
Your configuration file is `app.yaml`. You will rarely touch this file, unless you're dealing with third-party software and static files.

Your main script is `main.py`. It basically starts your app, but it also works to customize your Jinja2 environment or to add more routes for your controllers.

#### Abstracts
If you're using HamlPy, CoffeeScript, or Sass, all the files will be located in the `abstract/` folder. You may want to add this folder to your `.gitignore` if you're using none of these. In contrast, if you're using all three languages, you may want to ignore both `assets/` and `views/`.

#### Assets
Stylesheets, javascripts, and images are located in the `assets/` folder. You may anything else, including directories, files, etc. to this folder.

By default, your favicon is configured in `app.yaml` so it will be located on `assets/img/favicon.ico`.

#### MVC
If you do not know anything about MVC, this may be confusing. A good explanation can be found [here](http://tomdalling.com/blog/software-design/model-view-controller-explained/). To explain briefly: your models purely represent data, your views are a means for the user to view and change the data, and your controllers are used manipulate the data.

Your controllers and models are each in single python files, located in the `controllers/` and `models/` folders, respectively. Views are located in the `views/` folder, but if you're working with HamlPy, you may ignore that folder– your views will be located in `abstract/haml/`.

### Deploying
Your app can be deployed to google app engine by using `we -d`.
You must have the domain registered on appengine beforehand.
In `app.yaml`, you must put the domain in `application:` as well.
