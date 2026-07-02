TOOLS = {}

def register(name, func):
    TOOLS[name] = func

def get(name):
    return TOOLS.get(name)
