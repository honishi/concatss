online concatenated screenshot generator
==

matching algorithm
--
brute force.

prerequisite
--
* pyenv
    * https://github.com/yyuu/pyenv
    * python 3.3.x
* pyenv-virtualenv
    * https://github.com/yyuu/pyenv-virtualenv

setup
--
first, we need to install some required packages.
````
# debian
sudo apt-get install libjpeg8 libjpeg8-dev
# os x
brew install jpeg
````

then setup python runtime environment.
````
pyenv install 3.3.3
pyenv virtualenv 3.3.3 concatss-3.3.3
pyenv rehash
pip install -r requirements.txt
````

run
--
````
./main.py
````
by default, you can access the generator through `http://localhost:5000/`.

sample
--
generate concatenated screenshot from separated images.

![screenshot](./sample/output_resized.png)

license
--
MIT License.
copyright (c) 2013 honishi, hiroyuki onishi
