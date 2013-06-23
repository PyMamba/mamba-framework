.. _mamba_12_steps:

=========================
Mamba's 12 steps workflow
=========================

This is the general process for commiting code into the master branch of mamba project. There are exceptions to this general workflow for example for security or critical bug fixes, minor changes to documentation and typo fixes or fix a broken build.

All the development workflow is performed in the `Mamba's GitHub <https://github.com/DamnWidget/mamba>`_ project site.

#. When you are going to start to work in a fix or a feature you have to make sure of
    #. Make sure there is already an open issue about the code you are going to submit. If not, create it yourself.
    #. The issue has been discussed and approved by the mamba's development team
    #. If the fix or feature affects the mamba core, make sure a mamba core developer is working (or is going to) with you in the integration of the code into mamba
#. You should perform your work in your own `fork <https://help.github.com/articles/fork-a-repo>`_
#. You have to do it into a new `branch <http://git-scm.com/book/en/Git-Branching-What-a-Branch-Is>`_
#. Make sure your fork is `synced <https://help.github.com/articles/syncing-a-fork>`_ with the last in-development version and your branch is `rebased <http://git-scm.com/book/en/Git-Branching-Rebasing>`_ if needed.
#. Make sure you add an entry about the new fix/feature that you introduced on mamba into the `relnotes index <https://github.com/DamnWidget/mamba/blob/master/docs/relnotes/index.rst>`_ file
#. Make sure you add whatever documentation that is needed following the ocumentation for the project, thank you very much, we really appreciate it. Mamba uses the `Sphinx <sphinx-doc.org>`_  documentation syntax.
#. Make sure you reference the issue or issues that your changes affects in your `commit message <https://help.github.com/articles/closing-issues-via-commit-messages>`_ so we can just track the code fro the issues panel.
#. When your work is complete you should send a `Pull Request <https://help.github.com/articles/using-pull-requests>`_ on GitHub
#. Your pull request will be then reviewed by mamba developers and other contributors.
#. If there are issues with your code in the review, you should fix them and pushing your changes for new review (make sure you add a new comment in the pull request issue thread as GitHub doesn't alert anyone about new commits added into a pull request).
#. When the review finish, a core developer will merge your contribution into the master branch
#. Goto step 1

|
|