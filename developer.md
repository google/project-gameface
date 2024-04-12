# Developer getting started guide
Follow these instructions to get started as a developer for this project.

1.  Install Python 3.10 for Windows.

    You can download an installer from here for example.
    [python.org/downloads/release/python-31011/](https://www.python.org/downloads/release/python-31011/)

    There isn't a mediapipe for 3.12 Python, which is the latest at time of
    writing.

2.  Check the Python version is installed, on the path, and so on.

    If you run this command you should get this output.

        > python --version
        Python 3.10.11
    
    If you don't then restart Powershell or VSCode or VSCodium, or the whole
    machine. Or check the PATH environment variable.

3.  Create a Python virtual environment (venv).

    Python venv is now the best practice for programs that require PIP modules.

    Run commands like these to create the venv in a sub-directory also named
    `venv`. The repository is already configured to ignore that sub-directory.

        cd /path/where/you/cloned/FaceCommander
        python -m venv venv

    Going forwards, you will run Python like this.  
    `.\venv\Scripts\python.exe `... other command line options ...

4.  Install the required PIP modules.

    Run commands like these to update PIP and then install the required modules.

        cd /path/where/you/cloned/FaceCommander
        .\venv\Scripts\python.exe -m pip install --upgrade pip
        .\venv\Scripts\python.exe -m pip install -r .\requirements.txt

5.  Run the program.

    Run commands like this.

        cd /path/where/you/cloned/FaceCommander
        .\venv\Scripts\python.exe grimassist.py

The program should start. Its print logging should appear in the terminal or
Powershell session.
