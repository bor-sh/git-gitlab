## Intro

Simple git extension to interact with GitLab from command line.

API: https://gitlab.com/gitlab-org/gitlab-ce/tree/master/doc/api

### Prerequisite

Libsaas package and gitlab extension see:
https://gitlab.com/bor-sh-infrastructure/libsaas_gitlab/tree/master#README

### Installation if prerequisites are met

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

For each command get help by git gitlab command -h
and further infos what needs to be done is provided.

For example creating merge request.
If you are on the repository cloned and tracked on any gitlab server
referenced as remote.

~~~
git gitlab mr
~~~

All parameters are optional source, target branch and title 
if not provided will be derived from repository and current 
branch itself.

