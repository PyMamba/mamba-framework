.. _coding_style:

========================
Mamba coding style guide
========================

Like other Python projects, mamba try to follow the |pep8|_ and |sphinx|_ as docstrings conventions. Make sure to read those documents if you intent to contrbute to Mamba.

Naming conventions
------------------

* Package and module names **must** be all lower-case, words may be separated with underscores. No exceptions.
* Class names are `CamelCase` e.g. `ControllerManager`
* The function, variables and class member names **must** be all lower-case, with words separated by underscores. No exceptions.
* Internal (private) methods and members are prefixed with a single underscore e.g. `_templates_search_path`

Style rules
-----------

* **Lines shouldn't exceed 79 characters length.**
* Tabs **must** be replaced by four blank spaces, **never merge** tabs and blank spaces.
* **Never** use multiple statements in the same line, e.g. ``if check is True: a = 0`` with the only one exception for `conditional expressions <http://docs.python.org/3/reference/expressions.html#conditional-expressions>`_
* Comprehensions are preferred to the built-in functions ``filter()`` and ``map()`` when appropiate.
* Only use a ``global`` declaration in a function if that function actually modifies a global variable.
* Use the ``format()`` function to format strings instead of the semi-deprecated old '%s' % (data,) way.
* **Never** use a print statement, we always use a ``print()`` function instead.
* You **never** use ``print`` for logging purposes, for that you use ``twisted.python.log`` methods.

Inconsistences
--------------

Mamba uses |twisted|_ as his main component and Twisted doesn't follow |pep8|_ coding style and is never going to follow it. Because that you are going to be aware of some pretty inconsistences where we use twisted objects and methods.

We want to be clear on that, we **never** use |twisted| coding name conventions in exclusive mamba code, **no exceptions** to this rule.

Principles
----------

#. Never violates `DRY <http://programmer.97things.oreilly.com/wiki/index.php/Don%27t_Repeat_Yourself>`_
#. Any code change **must** pass unit tests and shouldn't break any other test in the system
#. No commit should break the master build
#. No change should break user code silently, deprecations and incompatibilities must be always a known (and a well documented) matter

|
|