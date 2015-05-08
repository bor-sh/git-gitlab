## Intro

Simple git extension to raise merge request on GitLab from command line.

## Installation

~~~
sudo python setup.sh install
~~~

Lates pyapi-gitlab is required: https://github.com/Itxaka/pyapi-gitlab

Probably it needs to be installed manually:
~~~
git clone https://github.com/Itxaka/pyapi-gitlab.git
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

In general only a user name is enough. Everything else will be derived from repository itself.
If a user name is found or similar to the provided input then we can select it from list.

~~~
git gitlab mr -h

git gitlab mr username
~~~
