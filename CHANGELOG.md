Python
======

### 2.0.0

This version introduces a NumPy version dependency, and has only been tested in
Python 2.7 and 3.4+.  If these compatibility requirements pose a problem, the
previous version (1.0.3) should continue to work for the foreseeable future.

* Add changelog
* Remove functions that were not part of the intended public interface
* Remove the long-deprecated "rounded" parameter
* Add more robust input checking for unpack64(), and the option to disable it
* Significantly improve performance
* General cleanups
