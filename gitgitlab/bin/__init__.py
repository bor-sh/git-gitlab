#!/usr/bin/env python

import argparse
import gitlab
import ConfigParser
import os
import json
import sys
from opster import command, dispatch
from git import Repo, InvalidGitRepositoryError
from git.config import GitConfigParser

from git.db import (
    GitCmdObjectDB,
    GitDB
)

DefaultDBType = GitDB
if sys.version_info[:2] < (2, 5):     # python 2.4 compatiblity
    DefaultDBType = GitCmdObjectDB

class GitlabClient(object):
  def __init__(self, url, token):
    try:
      self.git = gitlab.Gitlab(url, token)
    except Exception, e:
      raise ValueError("Gitlab could not be initialized - check connection or configuration")

  def get_projects_id(self, reponame):
    """
    Get gitlab project id
    :param reponame - repo name path namespace/repo.git
    :return project id to given repo name
    """
    projects = []
    project_id = None
    i = 1
    while True:
       page = self.git.getprojects(i, 100)
       if page:
        projects += page
        i += 1
       else:
        break
    for project in projects:
       if reponame in project['http_url_to_repo']:
         print "Project %s with ID:%i" % (project['http_url_to_repo'], project['id'])
         project_id = project['id']
         break
    if project_id == None:
      raise ValueError("No project id found")

    return project_id

  def create_mergerequest(self, project_id, source, target, title, assignee_id, target_project_id = None):
    res = self.git.createmergerequest(project_id, source, target, title, target_project_id, assignee_id)
    if res:
      print "Merge request created"
    else:
      print "Merge request seems to be already present"

  def check_user_id(self, name):
    users = {}
    result = self.git.getusers(name,1,100)
    for idx, user in enumerate(result):
      print "%i: %s" % (idx, user['username'])
      users.update({idx:user['id']})
    select = raw_input("Please select user: ")  
    try: 
      user = users[int(select)]
    except:
      raise ValueError("Wrong user selection")

class GitRepoClient(object):
  def __init__(self):
      self.name = "git repo client"    
      try:
        self.repo = Repo(None, DefaultDBType, True)
      except Exception, e:
        raise InvalidGitRepositoryError("Seems not to be a git repository")

  def get_current_branch(self):
      """
      Get current branch.
      """
      try:
        branch = self.repo.active_branch
      except:
        raise ValueError("Could not detect branch name")
      return branch.name

  def get_reponame(self):
      """
      Get repository name
      """
      remotes = self.repo.remotes
      # take only first should be enough we are only interested in the name
      try:
        url            = remotes[0].url
        filteredremote = url.replace("git@","").replace("https://","").replace("http://","")
        reponame       = filteredremote.split(":")[1]
        print "Repository name ", reponame
        return reponame
      except Exception:
        raise ValueError("No remote provided")

  def push_branch(self, branchname):
      """
      Push branch
      :param branchname
      """
      remotes = self.repo.remotes
      try:
        remotes[0].push(branchname)
      except:
        raise ValueError("Could not push")

  def get_config_gitlab_url(self):
      """
      Get global or local gitlab url.
      """
      return self.__get_config('gitlab', 'url')

  def get_config_gitlab_token(self):
      """
      Getting the token from global or local config.
      :return either local or global config gitlab token
      """
      return self.__get_config('gitlab', 'token')

  def __get_global_config(self):
      """
      Get global config
      :return object of GitConfigParser to ~/.gitconfig
      """
      return GitConfigParser(os.path.expanduser("~/.gitconfig"))

  def __get_config(self, name, entry):
      """
      Get global or local config entry.
      :param name 
      :param entry
      :return either local or global config
      """
      try: 
        config_reader = self.repo.config_reader()
        entry         = config_reader.get_value(name, entry) 
      except:
        try:
          config_reader = self.__get_global_config()
          entry         = config_reader.get_value(name, entry) 
        except:
          raise ValueError("No configuration provided")

      return entry

@command()
def mr(assignee, 
       title=("t", "", "title provided or derived from branch name"), 
       source=("s",  "", "branch to merge provided or current active branch is taken"), 
       reponame=('r', "", "repository name with namespace/repo.git or derived from remote settings if cloned"), 
       into=('i', "master", "target branch"), 
       forkedname=('f', "", "forked project name")):
  """
  Create merge request
  assignee - search for user which merge request should be assigned to
  """
  forked_id  = None

  repo_client = GitRepoClient()
  url         = repo_client.get_config_gitlab_url()
  token       = repo_client.get_config_gitlab_token()
  if not reponame:
    reponame  = repo_client.get_reponame()

  if not source:
    source    = repo_client.get_current_branch()
  if title == "":
    title = source

  repo_client.push_branch(source)  

  gitlab_client = GitlabClient(url, token)
  project_id    = gitlab_client.get_projects_id(reponame)
  assignee_id   = gitlab_client.check_user_id(assignee)
  if forkedname:
    forked_id   = gitlab_client.get_projects_id(forkedname)

  gitlab_client.create_mergerequest(project_id, source, into, title, forked_id, assignee_id)

def main():
    try:
        dispatch()
    except Exception, e:
        sys.exit(e)
 
if __name__ == '__main__':
  main()
