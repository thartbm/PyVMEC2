# PyVMEC2

This will be the next version of PyVMEC, rebuilt from the ground up, with much more functionality in mind.

# Environment

This is built with PsychoPy 2021.2.3 which does not run on newer version of Python (3.10 / 3.11) without issues. So here are instructions to set up an environment with Python 3.8.10:

First you need to install `pyenv`. Instructions for Mac and Windows are on their GitHub page: https://github.com/pyenv/pyenv

For Linux, I got them from this page: https://www.dwarmstrong.org/pyenv/

First download:

```
$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
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
$ sudo apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
On Fedora-based systems:
```
$ sudo dnf install make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel
```

Now you can install (many!) older versions of Python. For PyVMEC you want Python 3.8.10:

```
$ pyenv install -v 3.8.10
```

And then you can set your environment (current bash shell) to use that with:

```
$ pyenv local 3.8.10
```
Or even:
```
$ pyenv global 3.8.10
```

## PsychoPy

PsychoPy relies on wxWidgets which uses the GTK+ libraries, so these should also be installed on the system. Depending on your version of linux, this could look like:

```
$ sudo apt-get install build-essential libgtk-3-dev
```

You can then install everything necessary to run PyVMEC2, still from commandline:

```
$ pip3 install psychopy==2021.2.3 wxwidgets==1.0.5 ipython==8.9.0 numpy==1.22
```

Seems that wxwidgets is version 1.0.5, and ipython is 8.9.0 if that helps. 


## Screeninfo, Scipy

For reading out information about monitors, we use the `screeninfo` module (version 0.8.1 currently):

```
$ pip3 install screeninfo==0.8.1 scipy==1.3.3
```

For some advanced options, we use `scipy.optimize`.

# Installing PyVMEC2

Once the required environment and dependencies are set up, you should create a folder for everything to live in, for example: `VisuomotorAdaptation`. Then within this folder, you should _clone_ this repository:

```
$ cd VisuomotorAdaptation
$ git clone https://github.com/thartbm/PyVMEC2.git
```

That's it for the installing part... unless you want it available system-wide, then you should put it somewhere on the system path. But as long as you're in the parent folder, you can now import PyVMEC2 as a module:

```
$ ipython3
Python 3.8.10 ...
In [1]: from PyVMEC2 import *
pygame 2.1.2  ...
In [2]: runExperiment(experiment='diagnostic_triplets', participant='marius')
```
