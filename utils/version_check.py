# coding=utf-8
# Author: Nic Wolfe <nic@wolfeden.ca>
# Modified by: echel0n

import os
import platform
import re
# import shutil
# import stat
import subprocess
# import tarfile
# import traceback

# from six.moves.urllib.request import urlretrieve

from utils.logger import Logger
from utils.config import get_config

# import cleanup
# import core
# from core import github_api as github, logger


APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log = Logger().get_log(__name__)
config = get_config()

class Update(object):
    """Update this script"""

    def __init__(self):
        self._git = None
        self._current_hash = None
        self._new_hash = None
        self._behind = None
        self._ahead = None


    def run(self):
        # check if we even want to do this
        if config['updates']['auto_update'] and not config['updates']['auto_update'].lower() == 'true':
            log.info('Auto updating is disabled. Not checking for the latest version')
            return

        # check if this is a git clone install
        if not os.path.isdir(os.path.join(APP_ROOT, '.git')):
            log.warning('Unable to auto update. This was not installed with git')
            return

        # check if we can use git
        self._git = self._find_git()
        if not self._git:
            log.warning('Can not make calls to git. Exiting updater')
            return

        # get versions
        if self._get_installed_version() and self._get_new_version():
            log.debug('Current Commit = {}'.format(self._current_hash))
            log.debug('Newest Commit = {}'.format(self._new_hash))
            log.debug('Commits behind = {}'.format(self._behind))
            log.debug('Commits ahead = {}'.format(self._ahead))
        else:
            return

        # download new version
        if self._behind > 0:
            log.debug('Starting update.')
            # self._update()

        # restart script once done
        return None

    def _get_new_version(self):
        self._new_hash = None

        # get all new info from github
        output, err, exit_status = self._run_git_cmd(self._git, 'fetch origin')

        if not exit_status == 0:
            # logger.log(u'Unable to contact github, can\'t check for update', logger.ERROR)
            log.debug('Unable to contact github, can\'t check for updates')
            return

        # get latest commit_hash from remote
        output, err, exit_status = self._run_git_cmd(self._git, 'rev-parse --verify --quiet {}'.format(config['updates']['git_branch']))

        if exit_status == 0 and output:
            cur_commit_hash = output.strip()

            if not re.match('^[a-z0-9]+$', cur_commit_hash):
                # logger.log(u'Output doesn\'t look like a hash, not using it', logger.DEBUG)
                log.debug('Output doesn\'t look like a has, not using it')
                return

            else:
                self._new_hash = cur_commit_hash
        else:
            # logger.log(u'git didn\'t return newest commit hash', logger.DEBUG)
            log.debug('git didn\'t return newest commit hash')
            return

        # get number of commits behind and ahead (option --count not supported git < 1.7.2)
        output, err, exit_status = self._run_git_cmd(self._git, 'rev-list --left-right {}...HEAD'.format(config['updates']['git_branch']))

        if exit_status == 0 and output:

            try:
                self._behind = int(output.count('<'))
                self._ahead = int(output.count('>'))

            except Exception:
                # logger.log(u'git didn\'t return numbers for behind and ahead, not using it', logger.DEBUG)
                log.debug('git didn\'t return numbers for behind and ahead, not using it')
                return

        # logger.log(u'cur_commit = {current} % (newest_commit)= {new}, '
        #            u'num_commits_behind = {x}, num_commits_ahead = {y}'.format
        #            (current=self._cur_commit_hash, new=self._newest_commit_hash,
        #             x=self._num_commits_behind, y=self._num_commits_ahead), logger.DEBUG)

    def _get_installed_version(self):
        output, err, exit_status = self._run_git_cmd(self._git, 'rev-parse HEAD')  # @UnusedVariable

        if exit_status == 0 and output:
            cur_commit_hash = output.strip()
            if not re.match('^[a-z0-9]+$', cur_commit_hash):
                log.debug('Output doesn\'t look like a hash, not using it')
                return False
            self._current_hash = cur_commit_hash
            return True
        else:
            return False

    def _find_git(self):
        cmd = 'version'

        # Set configured or default git path
        if config['updates']['git_path'] and not config['updates']['git_path'] == '':
            main_git = '"{}"'.format(config['updates']['git_path'])
        else:
            main_git = 'git'


        log.info('Checking if we can use git commands: {} {}'.format(main_git, cmd))
        output, err, exit_status = self._run_git_cmd(main_git, cmd)

        if exit_status == 0:
            log.debug('Using: {}'.format(main_git))
            return main_git
        else:
            log.debug('Not using: {}'.format(main_git))

        # trying alternatives

        alternative_git = []

        # osx people who start SB from launchd have a broken path, so try a hail-mary attempt for them
        if platform.system().lower() == 'darwin':
            alternative_git.append('/usr/local/git/bin/git')

        if platform.system().lower() == 'windows':
            if main_git != main_git.lower():
                alternative_git.append(main_git.lower())

        if alternative_git:
            # logger.log(u'Trying known alternative git locations', logger.DEBUG)
            log.info('Trying known alternative git locations')

            for cur_git in alternative_git:
                # logger.log(u'Checking if we can use git commands: {git} {cmd}'.format
                #            (git=cur_git, cmd=test_cmd), logger.DEBUG)
                log.debug('Checking if we can use git commands: {} {}'.format(cur_git, cmd))
                output, err, exit_status = self._run_git_cmd(cur_git, cmd)

                if exit_status == 0:
                    # logger.log(u'Using: {git}'.format(git=cur_git), logger.DEBUG)
                    log.info('Using: {}'.format(cur_git))
                    return cur_git
                else:
                    # logger.log(u'Not using: {git}'.format(git=cur_git), logger.DEBUG)
                    log.info('Not using: {}'.format(cur_git))

        # Still haven't found a working git
        # logger.debug('Unable to find your git executable - '
        #              'Set git_path in your autoProcessMedia.cfg OR '
        #              'delete your .git folder and run from source to enable updates.')
        log.warning('Unable to find your git executable, set git_path in your settings.ini file')

        return None

    def _run_git_cmd(self, git, cmd):
        output = None
        err = None

        if not git:
            log.info('No git specified, can\'t use git commands')
            exit_status = 1
            return output, err, exit_status

        git_cmd = '{} {}'.format(git, cmd)

        try:
            log.info('Executing {} with your shell in {}'.format(cmd, APP_ROOT))
            p = subprocess.Popen(git_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 shell=True, cwd=APP_ROOT)
            output, err = p.communicate()
            exit_status = p.returncode

            output = output.decode('utf-8')

            if output:
                output = output.strip()
                log.debug('git output: {}'.format(output))

        except OSError:
            # logger.log(u'Command {cmd} didn\'t work'.format(cmd=cmd))
            log.info('Command {} didn\'t work'.format(cmd))
            exit_status = 1

        exit_status = 128 if ('fatal:' in output) or err else exit_status
        if exit_status == 0:
            # logger.log(u'{cmd} : returned successful'.format(cmd=cmd), logger.DEBUG)
            log.info('{} : returned successful'.format(cmd))
            exit_status = 0
        else:
            log.debug('{} returned : {}'.format(cmd, output))
            exit_status = 1

        return output, err, exit_status

    def _update(self):
        output, err, exit_status = self._run_git_cmd(self._git, 'pull origin {}'.format(config['updates']['git_branch']))  # @UnusedVariable

        if exit_status == 0:
            return True

        return False