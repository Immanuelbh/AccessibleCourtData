# Hebrew Court Verdicts Analyzer

# Development

## Installation

### Clone project
```shell
$ git clone --recurse-submodules https://github.com/Immanuelbh/HebrewCourtVerdictsAnalyzer.git
$ cd HebrewCourtVerdictsAnalyzer/
```

### Install required modules

#### MacOS
```shell
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip3 install -r requirements/requirements.txt
```

#### Windows
```shell
$ python3 -m venv venv
$ venv\Scripts\activate.bat
(venv) $ pip3 install -r requirements/requirements.txt
```

### Tests
```shell
$ python -m unittest
```

### Pylint
```shell
$ pylint hcva
```

### ELK stack

#### Version
Configured by changing the branch in the .gitmodules file.
```shell
branch = release-5.x
```
Update to different version
```
$ git submodule update --remote
```

#### Commands

##### Initialise
```shell
$ cd env/
$ ./init_env.sh
```

##### Shutdown
```shell
$ cd env/
$ ./shutdown_env.sh
```

### App

#### Commands

##### Run
```shell
$ ./init_app.sh
```

##### Shutdown
```shell
$ ./shutdown_app.sh
```


# Thank you
This project is part of the two-semester project for the [HIT Project Center](http://www.hitprojectscenter.com/), led by [Dr Yonathan Schler](https://www.hit.ac.il/faculty_staff/%D7%99%D7%94%D7%95%D7%A0%D7%AA%D7%9F_%D7%A9%D7%9C%D7%A8).

Based on: [AccessibleCourtData](https://github.com/liron7722/AccessibleCourtData) by [Liron Revah](https://github.com/liron7722) & [Baruh Shalumov](https://github.com/bstyle4ever).
