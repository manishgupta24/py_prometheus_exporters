import gc
import gevent


def has_existing_greenlets():
    for obj in gc.get_objects():
        if isinstance(obj, gevent.Greenlet):
            return True
    return False


def count_greenlets():
    count = 0
    for obj in gc.get_objects():
        if isinstance(obj, gevent.Greenlet):
            count += 1
    return count