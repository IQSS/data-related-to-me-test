# data-related-to-me-test

Proof of concept scratch for data related to me feature.  
- See related [google doc](https://docs.google.com/a/harvard.edu/document/d/1UcCtsPMxfHBd9ncXsFhbaofzkgn1NyiGzrZ0b0KqlWU/edit?usp=sharing)

## To Run


## Local Install (on OS X)

This is a quick checklist to install virtualenv and virtualevnwrapper on an OS X machine. 

#### Install [pip](http://pip.readthedocs.org/en/latest/installing.html)

* use sudo if needed
    * OS X: ```pip install -U pip```

#### Install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)

* depends on pip
    * OS X: ```sudo pip install virtualenvwrapper```
* remember to set the (shell startup file)[http://virtualenvwrapper.readthedocs.org/en/latest/install.html#shell-startup-file]
```
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh
``` 
or, on windows, [this](http://stackoverflow.com/questions/2615968/installing-virtualenvwrapper-on-windows) might be helpful.

#### Pull down this repostitory [data-related-to-me-test repository](https://github.com/iqss/data-related-to-me-test)

* Use the [mac client](https://mac.github.com/) if desired or [windows client](https://windows.github.com/)

### Setup on the local machine

#### cd into the ```basic-python-example``` repository

```
cd ~\data-related-to-me-test
```

#### Install the virtualenv and the requirements

This may take a minute or two.  On Mac: Xcode needs to be installed.
    
```
mkvirtualenv mydata
pip install -r requirements/base.txt
```

If you run into Xcode (or other errors) when running the install, google it.  Sometimes the [Xcode license agreement hasn't been accepted](http://stackoverflow.com/questions/26197347/agreeing-to-the-xcode-ios-license-requires-admin-privileges-please-re-run-as-r/26197363#26197363)

#### Set postactivate variable

- Open the postactivate script (in any editor--example below is ```vim```)
```
vim $VIRTUAL_ENV/bin/postactivate
```

- Add these lines to the bottom, save file, and return to the Terminal
```
export DJANGO_DEBUG=True
export DJANGO_SETTINGS_MODULE=mydata.settings.local
```

- Test it:
```
deactivate
workon mydata
echo $DJANGO_SETTINGS_MODULE
```

You should have seen: ```mydata.settings.local```
 

## Working with the project (post installation)

```
cd ~/data-related-to-me-test/mydata/mydata
workon mydata
python manage.py runserver
```


### Step 1 (from [google doc](https://docs.google.com/a/harvard.edu/document/d/1UcCtsPMxfHBd9ncXsFhbaofzkgn1NyiGzrZ0b0KqlWU/edit?usp=sharing))

- Go to: http://127.0.0.1:8000/step1/dataverseAdmin
   - ```dataverseAdmin``` may be any username
