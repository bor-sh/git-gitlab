## Intro

Simple git extension to interact with GitLab from command line.

API: https://github.com/gitlabhq/gitlabhq/tree/master/doc/api

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

### Commands

Merge request

~~~
git gitlab mr -h
# will be searched for some user and a selection is provided
git gitlab mr usernamepattern
~~~

Show merge request infos

~~~
git gitlab shmr -h
~~~

Update merge request

~~~
git gitlab upmr -h
~~~
