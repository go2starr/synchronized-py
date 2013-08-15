import functools
import types

from multiprocessing import RLock

class ObjectLock(object):
    """
    This class provides re-entrant locking over object instances via
    "with" context.
    """
    # Synchronize access to objects within this class
    _lock = RLock()

    # Attribute name for instance locks
    __LOCK_NAME = '__ObjectLock__'

    def __init__(self, obj):
        self.lock = ObjectLock._get_lock(obj)

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.lock.release()

    @classmethod
    def _get_lock(cls, obj):
        with cls._lock:
            lock_name = cls.__LOCK_NAME
            if not hasattr(obj, lock_name):
                setattr(obj, lock_name, RLock())
            return getattr(obj, lock_name)

def synchronized_object(obj):
    """
    Synchronized access to objects:
    
    >>> f = Foo()
    >>> with synchronized(f):
    >>>    # Exclusive access to f
    """
    return ObjectLock(obj)

def synchronized_method(func):
    """
    Synchronized access to instances from methods:
    
    >>> class MyClass:
    >>>     @synchronized
    >>>     def my_method(self):
    >>>         # Exclusive access to self
    """
    @functools.wraps(func)
    def with_synchronization(self, *args, **kwargs):
        with ObjectLock(self):
            return func(self, *args, **kwargs)
    return with_synchronization

def synchronized_func(func):
    """
    Synchronized access to functions:

    >>> @synchronized
    >>> def foo():
    >>>     # Exclusive access to foo
    """
    @functools.wraps(func)
    def with_synchronization(*args, **kwargs):
        with ObjectLock(func):
            return func(*args, **kwargs)
    return with_synchronization

def synchronized(obj):
    if type(obj) is types.FunctionType:
        return synchronized_func(obj)

    if type(obj) is types.MethodType:
        return synchronized_method(obj)

    if type(obj) is types.InstanceType:
        return synchronized_object(obj)
    
if __name__ == '__main__':
    import threading
    import time
    
    class Foo:
        @synchronized
        def foo(self):
            print('Enter!')
            time.sleep(0.25)
            print('Exit!')

        @synchronized
        def bar(self):
            print('bar')

    f = Foo()
    def test_object_lock():
        with ObjectLock(f):
            print('Acquired')
            time.sleep(0.25)
            print('Released')

    threads = [threading.Thread(target=test_object_lock) for _ in xrange(5)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    def test_synchronized():
        f.foo()
        time.sleep(0.25)

    threads = [threading.Thread(target=test_synchronized) for _ in xrange(5)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    @synchronized
    def foo():
        print('Enter!')
        time.sleep(0.25)
        print('Exit!')
    def test_synchronized_func():
        foo()

    threads = [threading.Thread(target=test_synchronized_func) for _ in xrange(5)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()        
    

    f = Foo()
    def test_synchronized_object():
        with synchronized(f):
            print('Enter!')
            time.sleep(0.25)
            print('Exit!')

    threads = [threading.Thread(target=test_synchronized_object) for _ in xrange(5)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()                    
