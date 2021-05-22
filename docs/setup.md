# How to install RASP?

RASP-machine is a simple Python3 module, available on the PyPI
repository. The simplest way to install it, is to use `pip` follows to
install the latest official release.

```shell-session
$ pip install rasp-machine
```

Should you want to contribute, you can retrieve the source code from
Github and install rasp-machine in development mode as follows. Note
that you may want to first create a virtual environment to avoid
polluting your Python installation.

```shell-session
$ git clone https://github.com/fchauvel/rasp-machine.git
$ cd rasp-machine
$ pip install -e . 
```

## Contributing

If you want to modify the source code, make sure to install also the
development dependencies using:

```shell-session
$ pip install -e .[dev]
```

