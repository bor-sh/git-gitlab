## Intro

Simple git extension to raise merge request on GitLab from command line.

## Installation

~~~
sudo python setup.sh install
~~~

## Configuration

~~~
global:
git config --global gitlab.url    "http://your-server-url"
git config --global gitlab.token  "your-token"

local in each repository:
git config gitlab.url   "http://your-server-url"
git config gitlab.token "your-token"
~~~

## Usage

### All commands

~~~
git gitlab -h
~~~

### Merge request

~~~
git gitlab mr -h
~~~


