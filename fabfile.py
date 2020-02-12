from __future__ import with_statement
from fabric.api import *



def production():
    projectname = 'pumpwerk'
    basepath = '/srv/pumpwerk.org/%s'
    env.hosts = ['pumpwerk@pumpwerk.org']
    env.path = basepath % projectname
    env.virtualenv_path = basepath % (projectname + 'env')
    env.push_branch = 'master'
    env.push_remote = 'origin'
    env.reload_cmd = 'supervisorctl restart {0}'.format(projectname)
    env.after_deploy_url = 'http://pumpwerk.org'


def reload_webserver():
    run("%(reload_cmd)s" % env)


def migrate():
    with prefix("source %(virtualenv_path)s/bin/activate" % env):
        run("%(path)s/manage.py migrate --settings=config.settings.production" % env)


def ping():
    run("echo %(after_deploy_url)s returned:  \>\>\>  $(curl --write-out %%{http_code} --silent --output /dev/null %(after_deploy_url)s)" % env)


def deploy():
    with cd(env.path):
        run("git pull %(push_remote)s %(push_branch)s" % env)
        with prefix("source %(virtualenv_path)s/bin/activate" % env):
            run("./manage.py collectstatic --noinput --settings=config.settings.production")

    migrate()
    reload_webserver()
    ping()


def pip():
    with cd(env.path):
        run("git pull %(push_remote)s %(push_branch)s" % env)
        with prefix("source %(virtualenv_path)s/bin/activate" % env):
            run("pip install -Ur requirements/production.txt")

    reload_webserver()


def soft_deploy():
    with cd(env.path):
        run("git pull %(push_remote)s %(push_branch)s" % env)

    reload_webserver()
    ping()