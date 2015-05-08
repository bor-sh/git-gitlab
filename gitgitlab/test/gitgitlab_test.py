import unittest
import json
import mock

from bin import GitRepoClient 
from bin import Helper 

class TestGitRepoClient(unittest.TestCase):
    """ Test class for GitRepoClient"""

    def setUp(self):
        self.user = "me"
        self.repo = GitRepoClient()

    def test_extract_remote_reponame(self):
        print "Get repo name from remote settings"
        self.assertEquals(self.repo.extract_reponame("https://gitlab.com/bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("http://gitlab.com:bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("ssh://git@gitlab.com/bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("ssh://git@gitlab.com:bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("git@gitlab.com:bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("git@gitlab.com/bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("gitlab.com:bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("gitlab.com/bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("sshsdfa://git@gitlab.com/bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")
        self.assertEquals(self.repo.extract_reponame("sshadf://git@gitlab.com:bor-sh/git-gitlab.git"),  "bor-sh/git-gitlab.git")

class TestGitlabClient(unittest.TestCase):
    """ Test class for GitlabClient"""

    def setUp(self):
        self.user = "me"
        self.help = Helper()

    def test_get_entry(self):
        print "Get entry"
        userlist =  json.loads(json.dumps([
                  {
                    "id": 1,
                    "username": "john_smith",
                  },
                  {
                    "id": 2,
                    "username": "jack_smith",
                  }
                ]))
        with mock.patch('__builtin__.raw_input', return_value='0'):
            assert self.help.get_entry(userlist, 'username') == 1
        with mock.patch('__builtin__.raw_input', return_value='1'):
            assert self.help.get_entry(userlist, 'username') == 2
        with mock.patch('__builtin__.raw_input', return_value='3'):
            self.assertRaises(ValueError)

        userlist =  json.loads(json.dumps([
                  {
                    "id": 1,
                    "username": "john_smith",
                  }
                ]))
        self.assertEquals( self.help.get_entry(userlist, 'username'), 1)

    def test_get_entry_project_id(self):
        print "Get entry project id"
        projects = json.loads(json.dumps([
          {
            "id": 4,
            "http_url_to_repo": "http://example.com/diaspora/diaspora-client.git",
          },
          {
            "id": 6,
            "http_url_to_repo": "http://example.com/brightbox/puppet.git",
          },
          {
            "id": 8,
            "http_url_to_repo": "http://example.com/birghtbox/puppet",
          }
          ]))

        with mock.patch('__builtin__.raw_input', return_value='0'):
            assert self.help.get_entry(projects, 'http_url_to_repo') == 4
        with mock.patch('__builtin__.raw_input', return_value='1'):
            assert self.help.get_entry(projects, 'http_url_to_repo') == 6
        with mock.patch('__builtin__.raw_input', return_value='3'):
            self.assertRaises(ValueError)

        reponame = "http://example.com/diaspora/diaspora-client.git"
        filtered = self.help.filter_list_by_entry(reponame, projects, 'http_url_to_repo')
        self.assertEquals(len(filtered), 1)
        self.assertEquals(filtered[0]['http_url_to_repo'], reponame)    

        projects = json.loads(json.dumps([
          {
            "id": 4,
            "http_url_to_repo": "http://example.com/diaspora/diaspora-client.git",
          },
          {
            "id": 6,
            "http_url_to_repo": "http://example.com/diaspora/diaspora",
          },
          {
            "id": 8,
            "http_url_to_repo": "http://example.com/diaspora/diaspora-client",
          },
          {
            "id": 10,
            "http_url_to_repo": "http://example.com/diaspora/diaspora.git",
          }
          ]))

        reponame = "http://example.com/diaspora/diaspora"
        filtered = self.help.filter_list_by_entry(reponame, projects, 'http_url_to_repo')
        self.assertEquals(len(filtered), 4)
        self.assertEquals(filtered[0]['http_url_to_repo'], "http://example.com/diaspora/diaspora-client.git")    

        reponame = "http://example.com/diaspora/diaspora.git"
        filtered = self.help.filter_list_by_entry(reponame, projects, 'http_url_to_repo')
        self.assertEquals(len(filtered), 1)
        self.assertEquals(filtered[0]['http_url_to_repo'], reponame)

        reponame = "http://example.com/diaspora/diasporasdfadf.git"
        filtered = self.help.filter_list_by_entry(reponame, projects, 'http_url_to_repo')
        self.assertEquals(len(filtered), 0)

if __name__ == '__main__':
    unittest.main()
