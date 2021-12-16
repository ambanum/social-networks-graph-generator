from graphgenerator.version import __version__

# load only once modules are installed, to avoid error during installation of the package
try:
    from graphgenerator.custom_classes.GraphBuilder import GraphBuilder
except ModuleNotFoundError:
    pass
