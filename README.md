# Blitz-repos

More than a repositories. Blitz-repos is handler for multiple repositories.
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
