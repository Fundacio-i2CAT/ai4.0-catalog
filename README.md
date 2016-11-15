## Introduction
See doc

## Installation
## Si al instalar el entorno no funciona por un tema de imágenes hacer lo siguiente
```
## Desde la raíz
```
$ sudo apt-get install libjpeg-dev 
## Y ya podremos instalarlo (desde el virtualenv (venv) )

$ pip install -r requirements.txt
$ python setup.py install

```

## Run App
Create a configuration for prod or use prod-config.yaml

```
$ python wsgi.py --help
Initialising...
Usage: wsgi.py

Anella app

Options:
  --version            show program's version number and exit
  -h, --help           show this help message and exit
  -c FILE, --cfg=FILE  specify the full path to an alternate config FILE
  --debug              Debug mode

```


## Test
Create a configuration for test or use test-config.yaml

Run tests by:

```
$ python -m unittest discover -s tests

```
