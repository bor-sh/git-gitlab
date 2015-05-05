import unittest
import json
from bin import GitRepoClient 

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

if __name__ == '__main__':
    unittest.main()
