# setup

```bash
mkdir PAD2
cd PAD2
virtualenv .
source bin/activate 

pip install Django
```

# Create Django project

```bash
django-admin startproject tfpro

mv tfpro src

cd src

python manage.py migrate

```

## Create app

```bash
python manage.py startapp tfclass
```

## Install dependencies

```bash
pip install mysqlclient
pip install mysql-connector-python

pip install django-crispy-forms
pip install django-multiupload

pip install numpy
pip install scipy
pip install matplotlib
pip install pandas
pip install plotly
pip install pybedtools

```


