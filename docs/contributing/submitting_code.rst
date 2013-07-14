.. _submitting_code:

=================
Howto submit code
=================

Code submition in mamba is done through `GitHub pull requests system <https://help.github.com/articles/using-pull-requests>`_ so you should be familiarized with it before trying to contribute your code with mamba.


Contributing with a bug fix
---------------------------

You found a bug and you want to fix it and share the fix with the rest of the community?. First of all, thank you very much, contributions like that make mamba better and maintains it alive.

Before start working in your fix, you have to go to the `mamba issues <https://github.com/DamnWidget/mamba/issues>`_ and look for the bug that you've found because maybe some other person is working on fix it already.

If you don't find any open issue related to the bug that you found, make sure that the bug is not already fixed in a more up-to-date version of mamba. You can do that just checking the code in the last commit of the GitHub repo or just looking for a closed issue related with the bug.

Another useful place were to find information related with the bug is the |relnotes|_ where the developers add information about bug fixes and other changes for the incomming new release version.

Of course your bugfix **must** follow the :doc:`coding_style` and :doc:`unit_tests` guidelines.


My bug is listed as a closed issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

That means that the bug that you found is already fixed by another developer and is added already to a more up-to-date version of mamba or is fixed in the in-development version and it's waiting for the release of the new version of the framework.

What I can do then?
...................

You can pull the in-development version of the framework (that is always the last commit in the master branch) and test if your bug is gone. If is not, just re-open the issue and explain what the problem is and why the fix doesn't work. You may also want to work with the person that wrote the first fix.


My bug is listed as an open issue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then this is a known issue, just read the issue discussion thread to discover if someone else is already working on a fix for that, if someone is already working to fix this problem, you can just contact with him (or her) to work together in solving the issue.

If no other person is working in fix the issue, just write a new comment to the issue discussion thread informing that you are going to work on solve the issue actively and ask other developers about guidance or ideas.


My bug is not listed anywhere
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Then you found an unknown mamba issue, create a new issue  in the GitHub repo and tag it as **bug**, explain that you are starting to work on fix it and ask for any help or guidance if needed.

Depending on the importance of the bug that you found, a mamba core developer may like to assist you or even solve himself the issue as fast as possible with your help.


Contributing with a new feature
-------------------------------

You added a *killer* feature to your own mamba fork and you decided to share it with the community? That's really great, thank you.

New features **may or may not** been always welcome, that depends of the nature of the new feature and the impact in the framework and how developers use it. If you are planning to develop and share a new feature for mamba, or you already developed it and what you want is just include it as part of the project, create a new issue in the GitHub project and tag it as **enhancement** or just send a **pull request** explaining about yor new feature and why it should be added into the framework.

.. note::
    Remember that all the code that you submit to the project **must** include unit tests.

Licenseing the code
-------------------

All the code that get into the mamba framework **must** be licensed under the **GPLv3** (or a later version on your choice) license.

|
|