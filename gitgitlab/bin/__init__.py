#!/usr/bin/env python

import signal
import argparse
import ConfigParser
import os
import json
import sys

from opster import command, dispatch
from git import Repo, InvalidGitRepositoryError
from git.config import GitConfigParser

import libsaas_gitlab as gitlab

from git.db import (
    GitCmdObjectDB,
    GitDB
)

DefaultDBType = GitDB
if sys.version_info[:2] < (2, 5):     # python 2.4 compatiblity
    DefaultDBType = GitCmdObjectDB

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
        return self.extract_reponame(remotes[0].url)
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

  def extract_reponame(self, url):
      """
      Extract repo name from remote url address
      """
      url,splitted = self.__get_split(url, "://")
      url,splitted = self.__get_split(url, "@")
      url,splitted = self.__get_split(url, ":")
      if not splitted:
        url, splitted = self.__get_split(url, "/")

      reponame = url
      return reponame

  def __get_split(self, string, pattern):
      splitted = False
      split = string.split(pattern)
      if len(split) > 1:
        splitted = True
        string = '/'.join(split[1:])
      return string, splitted

class Helper(object):
  def __init__(self):
    self.name = "helper"

  def get_entry(self, entries, selection, identity = 'id'):
    """
    Get entry
    :param entries
    :param selection
    :param identity
    """
    if not entries:
      raise ValueError("No entries found")

    dictionary = {}
    for idx, entry in enumerate(entries):
      print "%i: %s" % (idx, entry[selection])
      dictionary.update({idx:entry[identity]})
    select = 0
    if len(dictionary) > 1:
      select = raw_input("Please select [number]:")
    else:
      print "One entry found and will be selected", entries[0][selection]
    try: 
      return dictionary[int(select)]
    except:
      raise ValueError("Wrong selection")

  def get_state_event(self):
    # actually seems like "merge" does not have any effect
    # will use it to trigger the merge request
    events = [
        {
          "event": "close",
        },
        {
          "event": "reopen",
        },
        {
          "event": "merge",
        }
        ]
    return self.get_entry(events, "event", "event")

  def get_current_state(self):
    # actually seems like "merge" does not have any effect
    # will use it to trigger the merge request
    events = [
        {
          "event": "opened",
        },
        {
          "event": "closed",
        },
        {
          "event": "merged",
        }
        ]
    return self.get_entry(events, "event", "event")

  def filter_list_by_entry(self, entry, collection, selection):
    """
    Filter list by entry
    :param entry
    :param collection
    :param selection
    """
    result_list = []
    for name in collection:
      if entry in name[selection]:
        result_list.append(name)
    return result_list

  def get_filtered_pages_lists(self, service, filtername, filterby, data = {}):
    """
    Get filtered pages based on provided service
    :param service
    :param filtername  
    :param filterby
    :return filtered pages
    """
    pages = []
    data.update({ 'page':1, 'per_page':100 })
    while True:
       page = service.get(data)
       if page:
         pages += self.filter_list_by_entry(filtername, page, filterby)
         data.update({ 'page': data['page'] + 1})
       else:
         break
    return pages

  def show_infos(self, info, title, *args):
    """
    Show infos based on argument collection
    :param title 
    :param several different entries to show
    """
    try:
      print "%s:" % title
      for arg in args:
        argument = arg
        argument = argument[0].upper()+argument[1:]
        print "-- %s: %s" % (str(argument), str(info[arg]))
    except:
      print "-- not set"
      pass

  def get_projects_id(self, reponame):
    """
    Get gitlab project id
    :param reponame - repo name path namespace/repo.git
    :return project id to given repo name
    """
    filterby = 'http_url_to_repo'
    projects, projects_alternative = self.__get_filtered_project_lists(reponame)
    if len(projects_alternative) == 1:
      print "One project found which is matching with appended .git", projects_alternative[0][filterby]
      return projects_alternative[0]['id']

    return self.get_entry(projects, filterby)

  def get_user_id(self, name):
    result = service.users().get({ 'search':name, 'page':1, 'per_page':100 })
    return self.get_entry(result, 'username')

  def __get_filtered_project_lists(self, reponame, filterby = 'http_url_to_repo'):
    """
    Get filtered project lists
    :param reponame - repo name path namespace/repo.git
    :param filterby
    :return project id to given repo name
    """
    projects              = []
    projects_alternative  = []
    data                  = { 'page':1, 'per_page':100 }
    reponame_alternative  = reponame + ".git"
    while True:
       page = service.projects().get(data)
       if page:
         projects             += self.filter_list_by_entry(reponame, page, filterby)
         projects_alternative += self.filter_list_by_entry(reponame_alternative, page, filterby)
         data.update({ 'page': data['page'] + 1})
       else:
         break
    return projects, projects_alternative

repo_client   = GitRepoClient()
url           = repo_client.get_config_gitlab_url()
token         = repo_client.get_config_gitlab_token()
try:
  service     = gitlab.Gitlab(url, token)
except Exception, e:
  raise ValueError("Gitlab could not be initialized - check connection or configuration")
helper        = Helper()

@command(usage='[-a NAME_PATTERN] [-t TITLE] [-s SOURCE_BRANCH] [-i TARGET_BRANCH] [-r REPOSITORY] [-f FORKED_REPO_NAME] [-d DESCRIPTION]')
def mr(assignee=("a", "", "search for user name pattern"),
       title=("t", "", "title provided or derived from branch name"), 
       source=("s",  "", "branch to merge provided or current active branch is taken"), 
       reponame=('r', "", "repository name with namespace/repo.git or derived from remote settings if cloned"), 
       into=('i', "master", "target branch"), 
       forkedname=('f', "", "forked project name"),
       description=('d', "", "description of the merge request")):
  """
  Create merge request
  """
  forked_id  = None

  data = {}

  if not reponame:
    reponame  = repo_client.get_reponame()
  if not source:
    source    = repo_client.get_current_branch()
  if title == "":
    title = source

  if assignee:
    assignee_id = helper.get_user_id(assignee)
    data.update( {'assignee_id':assignee_id} )

  project_id    = helper.get_projects_id(reponame)

  if forkedname:
    forked_id   = helper.get_projects_id(forkedname)

  repo_client.push_branch(source)

  data.update( {'title': title} )
  if into:
    data.update( {'target_branch':into} )
  if source:
    data.update( {'source_branch':source} )
  if description:
    data.update( {'description':description} )
  if forked_id:
    data.update( {'target_project_id':forked_id} ) 
  
  res = service.project(project_id).merge_requests().create(data)
  if res:
    print "Merge request created"
    helper.show_infos(res['author'], "Author infos" , "name")
    helper.show_infos(res['assignee'], "Assignee infos", "name")
    helper.show_infos(res, "Merge ID", "iid")
    helper.show_infos(res, "Further infos", "title", "description", "state", "source_branch", "target_branch" )
  else:
    print "Merge request seems to be already present"

@command(usage='[-a NAME_PATTERN] [-c [STATE]] [-d DESCRIPTION] [-e [STATE]] [-f FILTER_TITLE_PATTERN] [-s SOURCE_BRANCH] [-i TARGET_BRANCH] [-m MESSAGE] [-r REPOSITORY] [-t TITLE]')
def upmr(assignee=("a", "", "search for user name pattern"),
         current_state=('c', "opened", "Return all requests or just those that are merged, opened or closed"),
         description=('d', "", "description of the merge request"),
         state_change=('e', "", "New state (close|reopen|merge) change - merge will accept the request"),
         filter_title=('f', "", "Filter list by title"),
         into=('i', "", "target branch"),
         commit_message=("m", "", "alternative commit message if accepting merge request"),
         reponame=('r', "", "repository name with namespace/repo.git or derived from remote settings if cloned"),
         source=("s",  "", "branch to merge provided or current active branch is taken"),
         title=("t", "", "title update"),
         ):
  """
  Update merge request
  """

  current_states = ['opened', 'closed', 'merged']
  current_state = current_state if current_state in current_states else helper.get_current_state()

  if not reponame:
    reponame  = repo_client.get_reponame()

  project_id  = helper.get_projects_id(reponame)

  filterby   = "title"
  merge_list = helper.get_filtered_pages_lists(service.project(project_id).merge_requests(), filter_title, filterby, { 'state':current_state })
  merge_id   = helper.get_entry(merge_list, filterby)

  data = {}
  state_event = None
  if assignee:
    assignee_id   = helper.get_user_id(assignee)
    data.update( {"assignee_id":assignee_id} )
  if description:
    data.update( {"description":description} )
  if state_change:
    states = ['close', 'reopen', 'merge']
    if state_change not in states:
      state_change = helper.get_state_event()
    data.update( {"state_event": state_change} )
  if into:
    data.update( {"target_branch":into} )
  if source:
    data.update( {"source_branch":source} )
  if title:
    data.update( {"title":title} )

  service.project(project_id).merge_request(merge_id).update(data)

  if state_event == "merge":
    result = service.project(project_id).merge_request(merge_id).accept(commit_message)
    if result:
      print "Merge was OK"
    else:
      print "Merge failed"

@command(usage='[-c [STATE]] [-f FILTER_TITLE_PATTERN] [-r REPOSITORY] [-d]')
def shmr(current_state=('c', "opened", "Return all requests or just those that are merged, opened or closed"),
         filter_title=('f', "", "Filter list by title"),
         reponame=('r', "", "repository name with namespace/repo.git or derived from remote settings if cloned"),
         diffs=('d', False, "Show changes of merge request")
         ):
  """
  Show merge request infos
  """

  current_states = ['opened', 'closed', 'merged']
  current_state = current_state if current_state in current_states else helper.get_current_state()

  if not reponame:
    reponame  = repo_client.get_reponame()

  project_id  = helper.get_projects_id(reponame)

  filterby   = "title"
  merge_list = helper.get_filtered_pages_lists(service.project(project_id).merge_requests(), filter_title, filterby, { 'state':current_state })
  merge_id   = helper.get_entry(merge_list, filterby)

  merge_info = service.project(project_id).merge_request(merge_id).changes()
  helper.show_infos(merge_info['author'], "Author infos" , "name")
  helper.show_infos(merge_info['assignee'], "Assignee infos", "name")
  helper.show_infos(merge_info, "Further infos", "title", "description", "state", "source_branch", "target_branch")

  if diffs:
    for change in merge_info['changes']:
      helper.show_infos(change, "Changes for file - " + change['new_path'], "old_path", "diff")

@command(usage='NOTE_MESSAGE [-c [STATE]] [-f FILTER_TITLE_PATTERN] [-r REPOSITORY]')
def pocomr(note,
           current_state=('c', "opened", "Return all requests or just those that are merged, opened or closed"),
           filter_title=('f', "", "Filter merge request by title"),
           reponame=('r', "", "repository name with namespace/repo.git or derived from remote settings if cloned"),
           ):
  """
  Post note
  note - note which should be posted
  """

  current_states = ['opened', 'closed', 'merged']
  current_state = current_state if current_state in current_states else helper.get_current_state()

  data = {}
  if not reponame:
    reponame  = repo_client.get_reponame()

  project_id  = helper.get_projects_id(reponame)

  filterby   = "title"
  merge_list = helper.get_filtered_pages_lists(service.project(project_id).merge_requests(), filter_title, filterby, { 'state':current_state })
  merge_id   = helper.get_entry(merge_list, filterby)

  if note:
    data['note'] = note
    service.project(project_id).merge_request(merge_id).comments().create(data)

@command(usage='[-c [STATE]] [-f FILTER_TITLE_PATTERN] [-n FILTER_NOTE_PATTERN] [-r REPOSITORY]')
def shcomr(current_state=('c', "opened", "Return all requests or just those that are merged, opened or closed"),
           filter_title=('f', "", "Filter merge request by title"),
           filter_note=('n', "", "Filter notes by pattern"),
           reponame=('r', "", "repository name with namespace/repo.git or derived from remote settings if cloned"),
           ):
  """
  Show merge request comments
  """

  current_states = ['opened', 'closed', 'merged']
  current_state = current_state if current_state in current_states else helper.get_current_state()

  if not reponame:
    reponame  = repo_client.get_reponame()

  project_id  = helper.get_projects_id(reponame)

  filterby   = "title"
  merge_list = helper.get_filtered_pages_lists(service.project(project_id).merge_requests(), filter_title, filterby, { 'state':current_state })
  merge_id   = helper.get_entry(merge_list, filterby)

  filterby   = "note"
  merge_comments = helper.get_filtered_pages_lists(service.project(project_id).merge_request(merge_id).comments(), filter_note, filterby)

  for comment in merge_comments:
      helper.show_infos(comment, "Comment by " + comment['author']['name'], "note")

def main():
    signal.signal(signal.SIGINT, handler)
    try:
      dispatch()
    except Exception, e:
      sys.exit(e)

def handler(signum, frame):
    print "\nExiting ..."
    sys.exit(0)

if __name__ == '__main__':
  main()
