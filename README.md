# Behave tests


## Setup

To setup python 3 environment for project first install direnv and pyenv on your machine:

brew install pyenv
brew install direnv
brew install pyenv-virtualenv
Copy this .direnvrc to your home directory.

Now when loading a project run direnv allow and a virtual python environment should be setup for the project.

This works with pyenv-virtualenv wrapper: https://github.com/direnv/direnv/wiki/Python#pyenv-virtualenv

We manage our python versions using pyenv: https://github.com/pyenv/pyenv