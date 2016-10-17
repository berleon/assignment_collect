# assignment_collect

This a collection of scripts to automate assignment collection over git.

Some of its features are tailored towards

# Install

Just run this command:

```
$ pip install git+https://github.com/berleon/assignment_collect
```

# Commands for students


## assignment init

To Enter your name and student id, run this command in your local clone of the
assignment repository

```
$ assignment init
```

You will be ask to enter your information.

## assignment add_student

Similar to `assignment init`. Add students after the repository was initialized.

## assignment check NUMBER

Checks if the assignment with the given number is ready for submission.


# Commands for the instructor

## assignmnt clone_all

Usage: assignment clone_all [OPTIONS] REPOLIST

Clones all repositories in file REPOLIST and performs a sanity check.

Options:
  -o, --output DIRECTORY  clone repositories to this directory
  --help                  Show this message and exit.

## assignment complete_student_data

Augments the repository data with the a csv export from the KVV.

See `assignment complete_student_data --help` for are more detailed
help.

