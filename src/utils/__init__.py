def clean_sh_error(error):
    """Get a clean error returned by a shell command."""
    return error.split(":")[-1].strip()
