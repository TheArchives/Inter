Inter, the inter-server communications system
=============================================

Inter is (or will be) a system for Minecraft servers to communicate with each other, in confined groups or clusters.
However, as plugins provide almost all functionality, this could be used for any project that needs a robust, modular JSON server.
Inter is suitable for anything from client communication, chat servers or data access servers, to simple remote control systems or monitoring solutions.

But do note, the default plugins will be Minecraft-oriented.

Requirements
------------

* Python 2.x (I recommend Python 2.7)
* Twisted (And therefore Zope)
* PyYaml
* yapsy

Running
-------

* Setup: ```python setup.py install``` (Untested but it /should/ work. Should. Maybe.)
* Starting the server: ```python run.py```