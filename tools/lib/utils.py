def find(li, ele):
    try:
        return li.index(ele)
    except ValueError:
        return False
