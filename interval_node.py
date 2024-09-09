class IntervalNode:
    """
    Represents a single node in an interval tree, containing an interval [low, high].

    Attributes:
        low (datetime): The starting point of the interval.
        high (datetime): The ending point of the interval.
        max (datetime): The maximum value in the subtree rooted at this node.
        left (IntervalNode): The left child of this node in the interval tree.
        right (IntervalNode): The right child of this node in the interval tree.
    
    Methods:
        __init__(low, high): Initializes an IntervalNode with the specified low and high values.
    """
    def __init__(self, low, high):
        self.low = low
        self.high = high
        self.max = high
        self.left = None
        self.right = None