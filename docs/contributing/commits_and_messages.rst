.. _commits_and_messages:

==================
Commits guidelines
==================

Before to send your pull request you have to follow the following general rules.

#. Generally you are not going to do a single big commit with all your changes while you are working in your code. Normally you are going to have safe points commits, merges/rebases and other information that is useful for your development process but doesn't add any useful information to the project if you send your pull request all those commits on it. First you have to squash the commits into a single commit with a really good commit message. The general rule to follow is that every commit should be able to be used as an isolated cherry pick.
#. You message has to be descriptive and useful. First line should be a descriptive sentence about what the commit is doing. It has to be clear and fully understable what the full commit is going to do just reading that single line.
#. You have to include the issue number prefixed with # at the end of the first line
#. The next line should be a blank line followed by an enumerated list with the commit details.
#. Add the right keywords for the commit as described in `Closing issues via commit messages <https://help.github.com/articles/closing-issues-via-commit-messages>`_ in the GitHub documentation.

Finally you have to get a commit message like this one::

    Adds <feature description> fo mamba web. Resolves #1936 and Fixes #456

        * Addition 1
        * Fix 1
        * Change 1
        * Deprecates 1
        * Deprecates 2
        ...

For a detailed information refer to the `Git Workflow <https://sandofsky.com/blog/git-workflow.html>`_ guidelines that mamba project follow since version 0.3.6

|
|