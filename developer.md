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

# Tips for Git on Windows
Git for Windows can be installed with winget as described here.  
[git-scm.com/download/win](https://git-scm.com/download/win)

You can activate OpenSSH in Windows 10 as described here.  
[stackoverflow.com/a/40720527/7657675](https://stackoverflow.com/a/40720527/7657675)

You can then set up a private key for GitHub authentication and configure SSH in
the usual way, by creating a `.ssh` sub-directory under your `users` directory,
for example `C:\Users\Jim\.ssh`. For example, you could create a `config` file
there with these settings.

    Host github.com
        IdentityFile ~/.ssh/<file you created with ssh-keygen here>
        User <Your GitHub username here>

    Host *
        AddKeysToAgent yes

That will cause the SSH identity you use for GitHub to be loaded in the agent so
you don't have to retype the private key passcode every time.

You can discover the OpenSSH executable path by running a Powershell command
like this.

    gcm ssh

The output could be like this (spaces have been compressed).

    CommandType     Name         Version    Source
    -----------     ----         -------    ------
    Application     ssh-add.exe  8.1.0.1    C:\Windows\System32\OpenSSH\ssh.exe

You can configure Git to use OpenSSH in the current Powershell session by
setting an environment variable, like this.

    $env:GIT_SSH = "C:\Windows\System32\OpenSSH\ssh.exe"

You can configure Git to use OpenSSH in all your future Powershell sessions by
configuring a permanent environment variable, like this.

    [Environment]::SetEnvironmentVariable(
        "GIT_SSH", "C:\Windows\System32\OpenSSH\ssh.exe", "User")

TOTH [stackoverflow.com/a/55389713/7657675](https://stackoverflow.com/a/55389713/7657675)  
Looks like you have to exit the Powershell session in which you ran that
command for it to take effect.

You can check the value has been set by printing all environment variables. To
do that run a command like this.

    get-childitem env:
