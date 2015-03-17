# Blitz-repos

More than repositories. Blitz-repos is handler for multiple repositories.
It can fetch and unpack multiple different repositories.

Main purpose is to be repository handler for bigger projects.
There might be multiple different 3rd party or upstream projects from which your
project depends on.
Blitz-repos tries to ease configuration and fetching of those,
in order to enable real build.
One could think this as git submodules with steroids.
Since configuration is plain JSON file,
it is easy to store for example in git, make copies,
and choose between multiple profiles.

## Configuration files

All sources, repositories and actions are defined in JSON based configuration files.
See "examples" folder for sample configuration files.

Most minimal configuration only defines "source" entry.
All defined source entries will then be fetched.
Additional unpack, configuration, build, test and install steps are possible,
so this blitz-repo be fully blown build system as well.

This is most minimal configuration file:

    {
        "libgit2": {
            "source": "https://github.com/libgit2/libgit2.git"
        }
    }

It tells we have project "libgit2" and URL to fetch if from.
One can define fetcher method, but by default git is assumed.

## Advanced examples

You can fetch libgit2_minimal.json project by running:

    ./blitz-repo.py --folder output_folder --init examples/libgit2_minimal.json

It will fetch it to output_folder/libgit2

More advanced example of the same:

    {
        "libgit2": {
            "source": "https://github.com/libgit2/libgit2.git",
            "method": "git"
        }
    }

Previous example defines method for fetching. Method can be dictionary or a string.
The simplest method is only "git", which is also the default.
Method can be more powerful when defined as dictionary like:

        "method": {
            "backend": "git",
            "branch": "v0.21.3"
        }

On this case "backend" entry tells same as "git" on previous definition.
However now we have "branch" entry as well.
The defined branch will be checked out from the git repository
and a local branch is made as well.
In case of git "commit" entry is also valid. In that case specific commit is checked out.

To define other steps, all these keywords are valid:
"unpack", "configure", "build", "install", "test".
All these entries can be string or list of strings.

Some magic values can define other steps as well, such as "cmake".
In case of "build": "cmake", blitz-repo will automatically define proper
configure, build and test steps to in order to be able to build with cmake.

To fetch, build and test specific branch of libgit2, this is minimal setup:

    {
        "libgit2": {
            "source": "https://github.com/libgit2/libgit2.git",
            "method": {
                "backend": "git",
                "branch": "v0.21.3"
            },
            "build": "cmake"
        }
    }

Command to build this is:

    ./blitz-repo.py --folder output_folder --all examples/libgit2.json

## Usage

See up to date usage with:

    ./blitz-repo.py --help


Output:

    blitz-repo.py [-h] [-f FOLDER] [-i] [-b] [-c] [-t] [-a] config

    Blitz repos

    positional arguments:
      config                Config file as JSON

    optional arguments:
      -h, --help            show this help message and exit
      -f FOLDER, --folder FOLDER
                            Output folder
      -i, --init            Initialize only, download sources
      -b, --build           Build sources
      -c, --configure       Build sources
      -t, --test            Run tests
      -a, --all             Perform all actions


## SSH Server

Blitz-repo can serve files over SSH. To enable SSH server first run ./bootstrap-ssh.sh
It will use blitz-repo itself to bootstrap required SSH server libraries.

After that one can start serving files thorough SSH just like:

    ./blitz-repo.py --folder output_folder --init examples/libgit2_minimal.json --serve --serve-port=4444

By default all users and clients are allowed as long as they provide their public SSH key.
To enable list of authorized keys create a file with contents:

    ssh-rsa PUBLIC_KEY user@host

This way "user" will be mapped with PUBLIC_KEY and authorized to access.

SSH provides very simple interface:

    $ ssh -p4444 localhost
    Blitz-repo
    > help
    Commands:
       EXIT          Close connection
       HELP          This help
       LIST [dir]    List directory
       GET file      Get file contents
    > list
    /libgit2
    > list /libgit2
    /libgit2/AUTHORS
    /libgit2/CHANGELOG.md
    /libgit2/CMakeLists.txt
    ...
    > get /libgit2/AUTHORS
    File: /libgit2/AUTHORS
    Size: 1241
    The following people contribute or have contributed
    ...
    > exit
    > Connection to localhost closed.


# Blitz Ninja

Build software with [ninja build](http://martine.github.io/ninja).

Will generate ninja files which can be used to build app.
Example run:

    mkdir buildtest
    cd buildtest
    ../blitz-ninja.py ../ninja_example/ninja_example.json > build.ninja
    ninja
    ./ninja_example

Output of example:

    Got: Hello all: cbQa=fD(


## JSON build file

Blitz utilizes simple JSON build files. They are parsed and transformed into ninja files.
For example traditional Hello World:

    #include <stdio.h>

    int main() {
        printf("Hello world\n");
    }

Minimal JSON build file for it:

    {
        "sources": ["hello.c"],
        "target": [
            {
                "name": "hello"
            }
        ]
    }

Main principle is to solve automatically as much as possible.
However give power to user and allow to override rules, or define custom ones.
