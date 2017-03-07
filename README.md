# CashFlow project - Instructions

To install CashFlow, you must to install virtualenv and a python version >= 3.4


### Unix OS 

####Creating a virtual environment

**Using pip**

    $ pip install -p python3 venv

    $ source venv/bin/activate

Also you can install your virtualenv with [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)

####Local deploy

Make sure you have previously installed all necessary packages on yout OS.

	$ (venv)$ pip install -r requirements/local-unix.txt

You can also install the requirements with the following command:

	$ (venv)$ pip install -r requirements/local.txt

This last command is used for Windows, but does not include the tool for class modeling.
	
####Production

    $ (venv)$ pip install -r requirements.txt

### Windows

####Creating a virtual environment

**Using pip**

	$ pip install venv

	$ venv/Scripts/activate

	(venv)$ pip install -r requirements/local.txt

Also you can install your virtualenv with [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper-win)

###Do you have questions about installing?
* [Quick installation of a project django with virtualenv](https://tutorial.djangogirls.org/es/django_installation/)
* [Do you have problemas installing virtualenvwrapper in windows?](https://docs.google.com/presentation/d/1hcTZYw8nJFJ4C59wHb9Z_c8U_oFSeL-nVX8yT0f-aKE/edit?usp=sharing)

or contact us: [digimundoweb@tescacorporation.com](mailto:digimundoweb@tescacorporation.com)
    