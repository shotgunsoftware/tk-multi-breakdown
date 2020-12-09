## Test Setup
The tests for this app utilizes the test rig and test runners available in the tk-core repository.
The app depends on external frameworks, and these must be present in your setup in order to
execute the tests. You need the `tk-framework-widget` and `tk-framework-shotgunutils` frameworks.

The app and framework repositories need to be located at the same level on disk in order for the
test runner to find them, for example:

```
Users
  \-john.smith
      \-git
          |-tk-multi-breakdown
          |-tk-framework-shotgunutils
          \-tk-framework-widget
```

## Running the tests
Navigate to the `tk-multi-breakdown` folder/repo, and execute pytest.


```
cd /path/to/tk-multi-breakdown
pytest
```
