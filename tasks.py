from invoke import task


@task
def run(c):
    c.run("python server.py")


@task
def test(c):
    c.run("python -m pytest")
