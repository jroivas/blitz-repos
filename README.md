# Blitz-repos

More than a repositories. Blitz-repos is handler for multiple repositories.
It can fetch and unpack multiple different repositories.


## Configuration files

All sources, repositories and actions are defined in JSON based configuration files.
See examples for sample configuration files.

Most minimal configuration only defines source, when those resources are fetched.
However unpack, configuration, build, test and install steps are possible,
so in fact this can be fully blown build system as well.

Main purpose is to be repository handler for bigger projects.
There might be multiple different 3rd party or upstream projects from which your
project depends on. Blitz-repos tries to ease configuration and fetching of those,
in order to enable real build.

This is most minimal configuration file:

    {
        "libgit2": {
            "source": "https://github.com/libgit2/libgit2.git"
        }
    }

It tells we have project "libgit2" and URL to fetch if from.
One can define fetcher method, but by default git is assumed.

You can fetch this project by:

    ./blitz-repos -f output_folder -i examples/libgit2_minimal.json

It will fetch it to output_folder/libgit2

More advanced example of the same:

    {
        "libgit2": {
            "source": "https://github.com/libgit2/libgit2.git",
            "method": "git"
        }
    }

This defines method for fetching. Method can be dictionary or a string.
Most simples method is only "git", which is same as if method is not defined.
Method can be dictionary like:

        "method": {
            "backend": "git",
            "branch": "v0.21.3"
        }

On this case "backend" tells same as "git" on previous defination.
However now we define "branch" as well.
On this case the defined branch will be checked out from the git repository.
In case of git "commit" entry is also valid, and in that case specific commit is checked out.

To define other steps, all these keywords are valid:
"unpack", "configure", "build", "install", "test"

All these entries can be string or list of strings.
Some magic keywords can define other steps as well, such as "cmake".
In case of "build: "cmake", it will define special configure and build steps
to fulfill cmake requirements. Test step is also expanded by default.
