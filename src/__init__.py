try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata  # python<=3.7

__meta__ = metadata.metadata("filexplorer")
__version__ = __meta__["version"]
