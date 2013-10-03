online concatenated screenshot generator
==

algorithm
--
> "When in doubt, use **brute force**." (Ken Thompson)

setup
--
````
$ sudo apt-get install libjpeg8 libjpeg8-dev
$ virtualenv --distribute venv
$ source ./venv/bin/activate
$ pip install http://sourceforge.net/projects/pychecker/files/pychecker/0.8.19/pychecker-0.8.19.tar.gz/download
$ pip install -r requirements.txt
````

sample
--
generate concatenated screenshot from separated images.
![screenshot](./sample/output.png)

license
--
MIT License.
copyright (c) 2013 honishi, hiroyuki onishi
