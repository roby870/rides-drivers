from interval_node import IntervalNode


class IntervalTree:
    """
    A data structure that supports efficient storage and querying of intervals, 
    allowing for quick lookup of intervals that overlap with a given interval.

    Attributes:
        root (IntervalNode): The root node of the interval tree.
    
    Methods:
        insert_interval(low, high): Inserts a new interval [low, high] into the interval tree.
        modify_intervals(low, high): Modifies intervals in the tree by removing any overlapping interval
                                     and reinserting the non-overlapping parts.
        is_available(low, high):
            Checks if the interval [low, high] is fully contained within any existing interval in the tree.
    """
    def __init__(self):
        self.root = None

    def _insert(self, root, low, high):
        """
        Inserts a new interval [low, high] into the interval tree.
        This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root node of the subtree where the interval will be inserted.
            low (datetime): The starting point of the interval.
            high (datetime): The ending point of the interval.

        Returns:
            IntervalNode: The new root of the subtree after insertion.
        """
        if root is None:
            return IntervalNode(low, high)
        if low < root.low: 
            root.left = self._insert(root.left, low, high)
        else:
            root.right = self._insert(root.right, low, high)
        root.max = max(root.max, high)
        return root

    def insert_interval(self, low, high):
        """
        Inserts a new interval [low, high] into the interval tree.

        Args:
            low (datetime): The starting point of the interval.
            high (datetime): The ending point of the interval.
        """
        if self.root is None:
            self.root = IntervalNode(low, high)
        else:
            self.root = self._insert(self.root, low, high)

    def _do_overlap(self, interval1, interval2):
        """
        Checks if two intervals overlap.
        This is an internal method and should not be called directly.

        Args:
            interval1 (IntervalNode): The first interval node.
            interval2 (IntervalNode): The second interval node.

        Returns:
            bool: True if the intervals overlap, False otherwise.
        """
        return interval1.low <= interval2.high and interval2.low <= interval1.high 

    def _search_overlap(self, root, low, high):
        """
        Searches for all intervals that overlap with the given interval [low, high] in the subtree rooted at root.
        This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root node of the subtree to search.
            low (datetime): The starting point of the interval to check for overlaps.
            high (datetime): The ending point of the interval to check for overlaps.

        Returns:
            list of tuples: A list of tuples where each tuple represents an overlapping interval [low, high].
        """
        if root is None:
            return []
        interval = IntervalNode(low, high)
        result = []
        if self._do_overlap(root, interval):
            result.append((root.low, root.high))
        if root.left is not None and root.left.max >= low:
            result.extend(self._search_overlap(root.left, low, high))
        result.extend(self._search_overlap(root.right, low, high))
        return result

    def _find_overlaps(self, low, high):
        """
        Returns a list of all intervals in the tree that overlap with the interval [low, high].
        This is an internal method and should not be called directly.

        Args:
            low (datetime): The starting point of the interval to check for overlaps.
            high (datetime): The ending point of the interval to check for overlaps.

        Returns:
            list of tuples: A list of tuples where each tuple represents an overlapping interval [low, high].
        """
        return self._search_overlap(self.root, low, high)

    def _find_min(self, root):
        """
        Finds the node with the minimum low value in the subtree rooted at root.
        This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root of the subtree to search.

        Returns:
            IntervalNode: The node with the minimum low value.
        """
        while root.left is not None:
            root = root.left
        return root
    
    def _delete_interval(self, root, low, high):
        """
        Recursively deletes an interval [low, high] from the interval tree.
        This method is used internally to handle the deletion of an interval
        from a subtree rooted at the given node. This is an internal method and should not be called directly.

        Args:
            root (IntervalNode): The root of the subtree from which the interval should be deleted.
            low (datetime): The starting point of the interval to delete.
            high (datetime): The ending point of the interval to delete.

        Returns:
            IntervalNode: The root of the subtree after the deletion, with the interval [low, high] removed.
        """
        if root is None:
            return None
        if low < root.low:
            root.left = self._delete_interval(root.left, low, high)
        elif low > root.low:
            root.right = self._delete_interval(root.right, low, high)
        elif root.low == low and root.high == high: #we found the interval 
            if root.left is None:
                return root.right
            if root.right is None:
                return root.left
            temp = self._find_min(root.right) #if the node has two children, we search the lowest value from the right part of the subtree
            root.low, root.high = temp.low, temp.high #we replace the interval with the lowest value from the right branch 
            root.right = self._delete_interval(root.right, temp.low, temp.high)
        #after deleting the interval, we refresh the max value on the top's nodes
        if root.left is None and root.right is None: 
            root.max = root.high
        elif root.left is None:
            root.max = max(root.high, root.right.max)
        elif root.right is None:
            root.max = max(root.high, root.left.max)
        else:
            root.max = max(root.high, root.left.max, root.right.max)
        return root

    def _delete(self, low, high):
        """
        Deletes an interval [low, high] from the interval tree. This is an internal method and should not be called directly.

        This method is a wrapper around the _delete_interval method and is used
        to initiate the deletion process from the root of the tree.

        Args:
            low (datetime): The starting point of the interval to delete.
            high (datetime): The ending point of the interval to delete.
        """
        self.root = self._delete_interval(self.root, low, high)

    def modify_intervals(self, low, high):
        """
        Modifies the interval tree by removing any intervals that overlap with the given interval [low, high]
        and then reinserting the non-overlapping portions back into the tree.

        Args:
            low (datetime): The starting point of the interval to modify.
            high (datetime): The ending point of the interval to modify.

        Notes:
            - For any interval [a, b] that overlaps with [low, high]:
                - If a < low, the interval [a, low] is reinserted.
                - If high < b, the interval [high, b] is reinserted.
        """
        overlapping_intervals = self._find_overlaps(low, high)
        for interval in overlapping_intervals:
            self._delete(interval[0], interval[1])
            if interval[0] < low:
                self.insert_interval(interval[0], low)
            if high < interval[1]:
                self.insert_interval(high, interval[1])


    def _is_available(self, node, low, high):
        """
        Recursively checks if an interval [low, high] is fully contained within any interval 
        in the subtree rooted at the given node.

        Args:
            node (IntervalNode): The root of the current subtree being checked.
            low (datetime): The starting point of the interval to check.
            high (datetime): The ending point of the interval to check.

        Returns:
            bool: True if the interval [low, high] is fully contained within an interval in this subtree, 
            False otherwise.
        """
        if not node:
            return False
        if low >= node.low and high <= node.high:
            return True
        if node.left and node.left.max >= low:
            if self._is_available(node.left, low, high):
                return True
        return self._is_available(node.right, low, high)
    

    def is_available(self, low, high):
        """
        Checks if an interval [low, high] is fully contained within any existing interval in the tree.

        Args:
            low (datetime): The starting point of the interval to check.
            high (datetime): The ending point of the interval to check.

        Returns:
            bool: True if the interval [low, high] is fully contained within an existing interval, False otherwise.
        """
        return self._is_available(self.root, low, high)