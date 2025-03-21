# Nautilus
Federated Learning Platform

### Supported Operating Systems

* Linux

### Python Version

Nautilus requires Python 3.8+.

### Install Nautilus in a virtual environment

```
$ sudo apt update
$ sudo apt-get install python3-venv
$ python3 -m venv nautilus-env
$ cd nautilus-env
$ source bin/activate
```

### Cloning the Nautilus Repository

```
(nautilus-env) $ sudo apt install git
(nautilus-env) $ git clone https://github.com/KETICoTLab/Nautilus.git
(nautilus-env) $ chmod +x ./Nautilus/setup.sh
(nautilus-env) $ sudo ./Nautilus/setup.sh
```

### Start nautilus\_server

```
(nautilus-env) $ cd Nautilus/nautilus/nautilus_server/
(nautilus-env) $ uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```