# Cjudge

Cjudge is a CLI tool build in python that allows the user to download, test and submit problems from different online judges.

## Supported judges
This a list of the currently supported judges:
- ### [Kattis](https://open.kattis.com/)
- ### [¡Acepta el Reto!](https://aceptaelreto.com/)
- ### [Uva Judge](https://onlinejudge.org/)

## Installation
To install Cjudge just use `pip`:
```
pip install cjudge
```
__Note:__ If you want to download Kattis problem statements from kattis you must need `latexmk`.  [Get more information](https://github.com/NotTete/kattispdf/tree/main)

## Commands
### cjudge-create
Given a judge and a problem id it downloads the problem statement, test samples and creates a `main.cpp` from a configurable template.
```
cjudge-create judge problem
```
### cjudge-info
Given a problem folder or a judge and a problem id it displays information about the selected problem.
```
cjudge-info judge problem
```
or
```
cjudge-info problem-folder
```
### cjudge-test
Given a problem folder it runs the test samples located in the `samples` folder.
```
cjudge-test problem-folder
```
### cjudge-submit
Given a problem folder it submits your problem solution to the corresponding judge.
```
cjudge-submit problem-folder
```
__Note 1:__ It will require you to introduce login credentials every time you login. 

__Note 2:__ In Kattis the login uses a token you can get from kattis website. [Get more information]()




