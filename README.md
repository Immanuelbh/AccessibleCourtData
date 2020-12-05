# Hebrew Court Verdicts Analyzer

# Development
## Installation
### Clone project
```
$ git clone --recurse-submodules https://github.com/Immanuelbh/HebrewCourtVerdictsAnalyzer.git
$ cd HebrewCourtVerdictsAnalyzer/
```
### Install required modules
#### MacOS
```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip3 install -r requirements/requirements.txt
```
#### Windows
```
$ python3 -m venv venv
$ venv\Scripts\activate.bat
(venv) $ pip3 install -r requirements/requirements.txt
```
### ELK stack
#### Version
Configured by changing the branch in the .gitmodules file.
```
branch = release-5.x
```
Update to different version
```
$ git submodule update --remote
```
#### Commands
##### Initialise
```
$ ./env/init_env.sh
```

##### Shutdown
```
$ ./env/shutdown_env.sh
```
### App
#### Commands
##### Run
```
$ ./init_app.sh
```
##### Shutdown
```
$ ./shutdown_app.sh
```


# Thank you
This project is part of the two-semester project for the [HIT Project Center](http://www.hitprojectscenter.com/), led by [Dr Yonathan Schler](https://www.hit.ac.il/faculty_staff/%D7%99%D7%94%D7%95%D7%A0%D7%AA%D7%9F_%D7%A9%D7%9C%D7%A8).

Based on: [AccessibleCourtData](https://github.com/liron7722/AccessibleCourtData) by [Liron Revah](https://github.com/liron7722) & [Baruh Shalumov](https://github.com/bstyle4ever).
