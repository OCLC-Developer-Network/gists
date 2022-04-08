# gists
Authentication code snippets in several languages

## PHP
### Install composer
https://getcomposer.org/download/

### Install dependencies
```bash
composer install
```

### Run the examples

ccgAuthExample.php can be run from the command line using

```bash
php ccgAuthExample.php
```

authCodeAuthExample.php can be run by starting a web server

```bash
php -S localhost:9090
```
Then open http://localhost:9090 in a web browser
## Python
### Install pip
https://pip.pypa.io/en/stable/installing/
### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the examples
ccgAuthExample.py can be run from the command line using

```bash
python ccgAuthExample.py
```

Both

- authCodeAuthExample.py - Login showing WAYF (Where are you from)
- authCodeWithAuthInstExample.py - Login to a particular institution

can be run by starting a web server

```bash
env FLASK_APP=authCodeAuthExample.py flask run
```

```bash
env FLASK_APP=authCodeWithAuthInstExample.py flask run
```

Then opening http://localhost:5000 in a web browser
