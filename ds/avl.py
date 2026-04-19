# ============================================================
# AVL Tree — Unit 1: Advanced Trees and Applications
# Used for: Student Record Management
# Time Complexity: O(log n) for insert/search/delete
# Self-balancing BST — height stays O(log n) always
# ============================================================

class AVLNode:
    """Each node stores one student record"""
    def __init__(self, roll, name, dept, year):
        self.roll   = roll    # Primary key — roll number
        self.name   = name    # Student name
        self.dept   = dept    # Department
        self.year   = year    # Year of study
        self.left   = None    # Left child pointer
        self.right  = None    # Right child pointer
        self.height = 1       # Height for balancing

class AVLTree:
    """Self-balancing BST for O(log n) student lookups"""

    # --- Utility helpers ---

    def _h(self, node):
        """Return height of node (0 if None)"""
        return node.height if node else 0

    def _bf(self, node):
        """Balance factor = left_height - right_height"""
        return self._h(node.left) - self._h(node.right) if node else 0

    def _update_height(self, node):
        """Recalculate height after rotation"""
        node.height = 1 + max(self._h(node.left), self._h(node.right))

    # --- Rotations (core of AVL balancing) ---

    def _right_rotate(self, y):
        """Right rotation for Left-heavy case"""
        x  = y.left
        T2 = x.right
        x.right = y
        y.left  = T2
        self._update_height(y)
        self._update_height(x)
        return x   # x becomes new root of this subtree

    def _left_rotate(self, x):
        """Left rotation for Right-heavy case"""
        y  = x.right
        T2 = y.left
        y.left  = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y   # y becomes new root of this subtree

    def _balance(self, node, roll):
        """Rebalance after insert if needed (4 cases)"""
        bf = self._bf(node)

        # Left-Left Case
        if bf > 1 and roll < node.left.roll:
            return self._right_rotate(node)

        # Right-Right Case
        if bf < -1 and roll > node.right.roll:
            return self._left_rotate(node)

        # Left-Right Case
        if bf > 1 and roll > node.left.roll:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        # Right-Left Case
        if bf < -1 and roll < node.right.roll:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node   # Already balanced

    # --- Public API ---

    def insert(self, root, roll, name, dept="CE", year=2):
        """Insert student record — O(log n)"""
        # Standard BST insert
        if not root:
            return AVLNode(roll, name, dept, year)
        if roll < root.roll:
            root.left  = self.insert(root.left,  roll, name, dept, year)
        elif roll > root.roll:
            root.right = self.insert(root.right, roll, name, dept, year)
        else:
            return root  # Duplicate roll — skip

        self._update_height(root)
        return self._balance(root, roll)

    def search(self, root, roll):
        """Search by roll number — O(log n)"""
        if root is None:
            return None
        if root.roll == roll:
            return root
        elif roll < root.roll:
            return self.search(root.left, roll)
        else:
            return self.search(root.right, roll)

    def inorder(self, root, result=None):
        """Return all students sorted by roll number — O(n)"""
        if result is None:
            result = []
        if root:
            self.inorder(root.left, result)
            result.append({
                'roll': root.roll,
                'name': root.name,
                'dept': root.dept,
                'year': root.year
            })
            self.inorder(root.right, result)
        return result
