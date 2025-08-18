import ctypes

def make_array(n):
    return (n * ctypes.py_object)()

class ArrayStack:
    INITIAL_CAPACITY = 8

    def __init__(self):
        self.data = make_array(ArrayStack.INITIAL_CAPACITY)
        self.n = 0
        self.capacity = 1

    def __len__(self):
        return self.n

    def isEmpty(self):
        return len(self) == 0
    
    def resize(self, newSize):
        newArray = make_array(newSize)
        for i in range(self.n):
            newArray[i] = self.data[i]
        self.data = newArray
        self.capacity = newSize
    
    def push(self, elem):
        if self.n == self.capacity:
            self.resize(self.capacity * 2)
        self.data[self.n] = elem
        self.n += 1
    
    def pop(self):
        if self.isEmpty():
            raise IndexError('Stack is empty')
        
        self.n -= 1
        if self.n < self.capacity // 4 and self.n > ArrayStack.INITIAL_CAPACITY:
            self.resize(self.capacity // 2)
        
        return self.data[self.n]
    
    def top(self):
        if self.isEmpty():
            raise IndexError('Stack is empty')
        
        return self.data[self.n - 1]
