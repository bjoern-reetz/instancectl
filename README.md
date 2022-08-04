# instancectl
A command line tool to start and stop cloud compute instances.

# Resources
* https://github.com/c4urself/bump2version
  * Why not use Poetry's own version command? Because I think `__version__` should indeed be hard-coded into the module.
    Also, bump2version has more features like automatic creation of tags. (Compare [foo](https://github.com/python-poetry/poetry/issues/144#issuecomment-652765652))
* Why src dir? Because then you have control of where you import your module from. (cwd in python-path, see https://blog.ionelmc.ro/2014/05/25/python-packaging/)
* https://click.palletsprojects.com/en/8.1.x/
