
def is_empty(value):
    if value is None:
        return True
    elif len(value) <= 0:
        return True
    else:
        return False

def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
