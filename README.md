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
ccgAuthExample.python can be run from the command line using

```bash
python ccgAuthExample.py
```

authCodeAuthExample.py can be run by starting a web server

```bash
env FLASK_APP=authCodeAuthExample.py flask run
```
Then opening http://localhost:5000 in a web browser
