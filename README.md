# PyVMEC-2

This will be the next version of PyVMEC, rebuilt from the ground up, with much more functionality in mind.

# Environment

This is built with PsychoPy 2021.2.3 which does not run on newer version of Python (3.10 / 3.11) without issues. So here are instructions to set up an environment with Python 3.8.10:

First you need to install `pyenv`. Instructions for Mac and Windows are on their GitHub page: https://github.com/pyenv/pyenv

For Linux, I got them from this page: https://www.dwarmstrong.org/pyenv/

First download:

```
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```

Then add this to the end of your profile (`~/.profile` or `~/.bash_profile`):

```
if [ -d "$HOME/.pyenv" ] ; then
    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
fi
```

And reload your profile (e.g. `$ . ~/.profile`). You now have pyenv installed, so there should be two new folders at the start of your `$PATH`:

```
$ echo $PATH
```
One for shims and one bin folder.

Since `pyenv` compiles Python, you need tools to do that. On Debian-based systems:

```
sudo apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
On Fedora-based systems:
```
sudo dnf install make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel
```

Now you can install (many!) older versions of Python. For PyVMEC you want Python 3.8.10:

```
pyenv install -v 3.8.10
```

And then you can set your environment (current bash shell) to use that with:

```
pyenv local 3.8.10
```
Or even:
```
pyenv global 3.8.10
```

# PsychoPy

You can then install everything necessary to run PyVMEC2, still from commandline:

```
pip3 install psychopy==2021.2.3 wxwidgets ipython
```

(Seems that wxwidgets is version 1.0.5, and ipython is 8.9.0 if that helps.)


# Numpy

The newest versions of numpy use built-in float and int types, but PsychoPy doesn;t, so we need an old numpy:

```
pip3 install numpy=1.22
```

# Screeninfo

For reading out information about monitors, we use the `screeninfo` module (version 0.8.1 currently):

```
pip3 install screeninfo
```

