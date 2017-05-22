def openFile(filepath, Mode="r"):
    """"
    (str, str) -> file object
    Interface for the open() built-in function with try/exception structure.
    Returns None if an IOError exception is raised.
    """
    try:
        fileObj = open(filepath, mode=Mode)
    except IOError:
        print("Warning: IOError while trying to open %s!" %filepath)
        return None
    return fileObj
