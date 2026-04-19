# ============================================================
# Fibonacci Heap — Unit 2: Priority Queues and Heaps
# Used for: Assignment deadline priority queue
# Time Complexity: O(1) amortized insert, O(log n) extract-min
# More efficient than binary heap for decrease-key operations
# ============================================================

import math

class FibNode:
    """Node in Fibonacci Heap"""
    def __init__(self, days, subject, subject_code=""):
        self.days         = days          # Priority key (days remaining)
        self.subject      = subject       # Assignment name
        self.subject_code = subject_code  # e.g. "DSA301"
        self.degree       = 0             # Number of children
        self.marked       = False         # For decrease-key cascade
        self.parent       = None
        self.child        = None
        self.left         = self          # Circular doubly linked
        self.right        = self

class FibonacciHeap:
    """
    Fibonacci Heap for assignment scheduling — Unit 2
    Supports O(1) amortized insert, O(log n) extract-min
    Better than binary heap when many decrease-key ops needed
    """

    def __init__(self):
        self.min_node  = None   # Pointer to minimum
        self.num_nodes = 0

    def _link(self, child, parent):
        """Make child a child of parent (used during consolidation)"""
        # Remove child from root list
        child.left.right  = child.right
        child.right.left  = child.left

        child.parent = parent

        if parent.child is None:
            parent.child = child
            child.left   = child
            child.right  = child
        else:
            child.left        = parent.child
            child.right       = parent.child.right
            parent.child.right.left = child
            parent.child.right      = child

        parent.degree += 1
        child.marked   = False

    def insert(self, days, subject, subject_code=""):
        """Insert assignment — O(1) amortized"""
        node = FibNode(days, subject, subject_code)

        if self.min_node is None:
            self.min_node = node
        else:
            # Insert into root list
            node.right              = self.min_node
            node.left               = self.min_node.left
            self.min_node.left.right = node
            self.min_node.left       = node

            if node.days < self.min_node.days:
                self.min_node = node

        self.num_nodes += 1
        return node

    def extract_min(self):
        """Remove and return assignment with nearest deadline — O(log n) amortized"""
        z = self.min_node
        if z is None:
            return None

        # Add children of z to root list
        if z.child:
            children = []
            cur = z.child
            while True:
                children.append(cur)
                cur = cur.right
                if cur == z.child:
                    break

            for child in children:
                child.left.right  = child.right
                child.right.left  = child.left

                child.right              = self.min_node
                child.left               = self.min_node.left
                self.min_node.left.right = child
                self.min_node.left       = child

                child.parent = None

        # Remove z from root list
        z.left.right = z.right
        z.right.left = z.left

        if z == z.right:
            self.min_node = None
        else:
            self.min_node = z.right
            self._consolidate()

        self.num_nodes -= 1
        return z

    def _consolidate(self):
        """Consolidate trees of same degree — O(log n)"""
        max_degree = int(math.log2(self.num_nodes + 1)) + 2
        A = [None] * (max_degree + 1)

        roots = []
        cur = self.min_node
        if cur:
            while True:
                roots.append(cur)
                cur = cur.right
                if cur == self.min_node:
                    break

        for w in roots:
            x = w
            d = x.degree

            while d < len(A) and A[d] is not None:
                y = A[d]
                if x.days > y.days:
                    x, y = y, x
                self._link(y, x)
                A[d] = None
                d += 1

            if d < len(A):
                A[d] = x

        self.min_node = None
        for node in A:
            if node:
                if self.min_node is None:
                    self.min_node = node
                    node.left  = node
                    node.right = node
                else:
                    node.right              = self.min_node
                    node.left               = self.min_node.left
                    self.min_node.left.right = node
                    self.min_node.left       = node

                    if node.days < self.min_node.days:
                        self.min_node = node

    def get_all_sorted(self):
        """
        Extract all assignments sorted by urgency.
        Uses a temp heap so original is not destroyed.
        Returns list of dicts.
        """
        result = []
        temp   = FibonacciHeap()

        # Copy all root + child nodes
        def collect(node):
            if node is None:
                return
            cur = node
            while True:
                temp.insert(cur.days, cur.subject, cur.subject_code)
                collect(cur.child)
                cur = cur.right
                if cur == node:
                    break

        collect(self.min_node)
        temp.num_nodes = self.num_nodes

        while temp.num_nodes > 0:
            node = temp.extract_min()
            if node:
                result.append({
                    'days':         node.days,
                    'subject':      node.subject,
                    'subject_code': node.subject_code
                })

        return result


# ============================================================
# Simple Priority Queue wrapper (also exposes binary heap API)
# Used as fallback for demonstration
# ============================================================

import heapq

class AssignmentHeap:
    """Min-heap priority queue wrapper — also Unit 2"""

    def __init__(self):
        self.heap = []

    def add_assignment(self, days, subject, subject_code=""):
        heapq.heappush(self.heap, (days, subject, subject_code))

    def get_assignments(self):
        return [
            {'days': d, 'subject': s, 'subject_code': c}
            for d, s, c in sorted(self.heap)
        ]
