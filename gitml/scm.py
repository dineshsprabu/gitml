import git
import os
from codecs import open

from .exceptions import GitMLException
from .util import log_message, touch

class InvalidGitRepositoryError(GitMLException):
    pass


class FileNotInRepoError(GitMLException):
    pass


class SCMError(GitMLException):
    pass


class Git(object):

    IGNORE_FILE = ".gitignore"

    DIR = ".git"

    @classmethod
    def _is_repo(cls, root_dir):
        git_dir = os.path.join(root_dir, Git.DIR)
        return os.path.isdir(git_dir)


    def __init__(self, root_dir=os.curdir):
        self.root_dir = os.path.abspath(os.path.realpath(root_dir))
        self.ignore_file = os.path.join(self.root_dir, 
            self.IGNORE_FILE)
        self.git_dir = os.path.join(self.root_dir, self.DIR)
        self.is_repo = Git._is_repo(self.root_dir)
        # Initialize repo, if not already one.
        if not self.is_repo: 
            git.Repo.init(root_dir)
        self.repo = git.Repo(self.root_dir)


    def _ignore_file_exist(self):
        return os.path.exists(self.ignore_file)


    def _create_ignore_file(self):
        if not self._ignore_file_exist():
            open(self.ignore_file, "a", "utf-8").close()
        return self.ignore_file


    def _is_branch_exist(self, branch):
        for b in self.repo.branches:
            if b.name == branch:
                return True
        return False


    def gitignore(self):
        if not _ignore_file_exist():
            self._create_ignore_file()
        # Returns ignore file object.
        return open(self.ignore_file, "w+", "utf-8")


    @classmethod
    def init(cls, root_dir, initial_ignores=[]):
        _git = Git(root_dir)
        if not Git._is_repo(root_dir):
           
            # Creates a branch on the new repo.
            _git.checkout("master")
        _git.add_ignores(initial_ignores)
        _git.commit_all("GitML Project initialised. Visit "+ \
            "https://gitml.com.")
        return _git


    def add(self, paths):
        self.repo.index.add(paths)


    def add_all(self):
        self.repo.git.add("-A")


    def commit(self, msg):
        # Returns commit id.
        return str(self.repo.index.commit(msg))


    def commit_all(self, msg):
        self.add_all()
        return self.commit(msg)


    def checkout(self, branch):
        if self._is_branch_exist(branch):
            self.repo.git.checkout(branch)
        else:
            # Zero commits in repo. No HEAD available.
            if self.repo.heads:
                self.repo.git.checkout("HEAD", b=branch)
            else:
                self.repo.git.checkout(b=branch)


    def branch(self, branch):
        self.repo.git.branch(branch)


    def add_tag(self, tag, commit=None):
        if not commit:
            # Adds tag to latest commit.
            self.repo.git.tag(tag)
        else:
            # Adds tag to the given commit.
            self.repo.git.tag(tag, commit)


    def get_commit_by_tag(self, tag):
        # Returns commit hash of a commit with given tag.
        return self.repo.git.show(tag, q=True, format="%H")


    def current_branch(self):
        return self.repo.active_branch.name


    def restore_file(self, commit_hash, file_path):
        self.repo.git.checkout(commit_hash, file_path)


    def stash(self):
        # Stashes work.
        self.repo.git.stash("save")


    def restore_stash(self, pop=False):
        if pop: return self.repo.git.stash("pop")
        # Restores last stash.
        self.repo.git.stash("apply")


    def stashed_files(self):
        files = map(lambda x: x.split(" ")[1], 
            self.repo.git.stash("show").split("\n"))
        if files: files = files[:-1]
        return files


    def resolve_with_theirs(self):
        self.repo.git.checkout(".", theirs=True)
        self.add_all()


    def restore_stash_clean(self):
        # Restoring stash skipping conflicts.
        try: self.restore_stash()
        except: pass
        # Resolving with theirs.
        self.resolve_with_theirs()


    def list_working_copy(self):
        files = self.repo.git.diff('HEAD', name_only=True)
        if not files.strip(): return []
        return files.split("\n")


    def cherry_pick(self, commit_hash):
        try: self.repo.git.cherry_pick(commit_hash)
        except: pass


    def staged_files(self):
        files = self.repo.git.diff('HEAD', name_only=True, 
            cached=True)
        if not files.strip(): return []
        return files.split("\n")


    def cherry_pick_abort(self):
        try: self.repo.git.cherry_pick(abort=True)
        except: pass


    def get_ignores(self):
        if not os.path.exists(self.ignore_file): return []

        with open(self.ignore_file, "r+") as ig_file:
            ignores = ig_file.read()

        # Strip new lines at the end of file.
        ignores = ignores.strip(" ").strip("\n").split("\n")

        # Exclude commented lines.
        ignores = [i for i in ignores if not i.startswith("#")]
        return map(lambda ignore: ignore.strip(" "), ignores)


    def add_ignores(self, entries):
        # Creates the ignore file, if not exist.
        touch(self.ignore_file)

        if os.path.exists(self.ignore_file):
            # Building entries.
            ignore_string = "# Added by GitML\n"
            for entry in entries:
                ignore_string = (ignore_string 
                    + "%s\n" % entry.strip(" "))
            # Adds new ignores.
            with open(self.ignore_file, "a") as ignore_file:
                ignore_file.write("\n%s\n\n" % ignore_string)

