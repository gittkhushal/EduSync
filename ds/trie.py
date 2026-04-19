# ============================================================
# Trie + Compressed Trie — Unit 3: Data Structures for Strings
# Used for: Fast Material / Subject Search (autocomplete)
# Time Complexity: O(L) per insert/search where L = word length
# Compressed Trie (Radix Trie) reduces space usage
# ============================================================

class TrieNode:
    """Node in the Trie — stores one character per level"""
    def __init__(self):
        self.children = {}   # Dict: char -> TrieNode
        self.is_end   = False     # True if this node ends a word
        self.data     = None      # Extra metadata stored at end nodes

class Trie:
    """Standard Trie for O(L) prefix search — Unit 3"""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, data=None):
        """Insert word letter by letter — O(L)"""
        node = self.root
        for ch in word.lower():
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
        node.data   = data or word   # Store original casing

    def _collect(self, node, prefix, result):
        """DFS to collect all words from a given node"""
        if node.is_end:
            result.append({'word': prefix, 'data': node.data})
        for ch, child in node.children.items():
            self._collect(child, prefix + ch, result)

    def search_prefix(self, prefix):
        """Return all words matching a given prefix — O(L + results)"""
        node = self.root
        for ch in prefix.lower():
            if ch not in node.children:
                return []          # Prefix not found
            node = node.children[ch]
        result = []
        self._collect(node, prefix.lower(), result)
        return result

    def search_exact(self, word):
        """Exact word lookup — O(L)"""
        node = self.root
        for ch in word.lower():
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end


# ============================================================
# Skip List — Unit 4: Randomized Data Structures
# Used for: Attendance record storage with O(log n) average ops
# Probability-based layered linked list
# ============================================================

import random

class SkipNode:
    """Node in skip list — stores attendance record"""
    def __init__(self, roll, attendance_pct, level):
        self.roll           = roll
        self.attendance_pct = attendance_pct
        self.forward        = [None] * (level + 1)  # Pointers per level

class SkipList:
    """Skip List for O(log n) average attendance queries — Unit 4"""

    MAX_LEVEL = 4      # Maximum levels in skip list
    P         = 0.5    # Probability for promoting to next level

    def __init__(self):
        self.header = SkipNode(-1, 0, self.MAX_LEVEL)  # Sentinel head
        self.level  = 0

    def _random_level(self):
        """Coin-flip based level generation"""
        lvl = 0
        while random.random() < self.P and lvl < self.MAX_LEVEL:
            lvl += 1
        return lvl

    def insert(self, roll, attendance_pct):
        """Insert attendance record — O(log n) average"""
        update = [None] * (self.MAX_LEVEL + 1)
        cur    = self.header

        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].roll < roll:
                cur = cur.forward[i]
            update[i] = cur

        cur = cur.forward[0]

        if cur is None or cur.roll != roll:
            new_level = self._random_level()
            if new_level > self.level:
                for i in range(self.level + 1, new_level + 1):
                    update[i] = self.header
                self.level = new_level

            new_node = SkipNode(roll, attendance_pct, new_level)
            for i in range(new_level + 1):
                new_node.forward[i] = update[i].forward[i]
                update[i].forward[i] = new_node
        else:
            cur.attendance_pct = attendance_pct   # Update existing

    def search(self, roll):
        """Search attendance by roll — O(log n) average"""
        cur = self.header
        for i in range(self.level, -1, -1):
            while cur.forward[i] and cur.forward[i].roll < roll:
                cur = cur.forward[i]
        cur = cur.forward[0]
        if cur and cur.roll == roll:
            return cur.attendance_pct
        return None

    def get_all(self):
        """Return all records in sorted order"""
        result = []
        cur = self.header.forward[0]
        while cur:
            result.append({'roll': cur.roll, 'pct': cur.attendance_pct})
            cur = cur.forward[0]
        return result


# ============================================================
# Segment Tree — Unit 5: Multidimensional Spatial Data Structures
# Used for: Attendance range queries (e.g., avg attendance Jan–Mar)
# Time Complexity: O(log n) query and update
# ============================================================

class SegmentTree:
    """Segment Tree for range attendance queries — Unit 5"""

    def __init__(self, data):
        """Build tree from list of attendance percentages"""
        self.n    = len(data)
        self.tree = [0] * (4 * self.n)
        if self.n > 0:
            self._build(data, 0, 0, self.n - 1)

    def _build(self, data, node, start, end):
        if start == end:
            self.tree[node] = data[start]
        else:
            mid = (start + end) // 2
            self._build(data, 2*node+1, start,   mid)
            self._build(data, 2*node+2, mid+1,   end)
            # Store sum for range average queries
            self.tree[node] = self.tree[2*node+1] + self.tree[2*node+2]

    def query(self, l, r, node=0, start=0, end=None):
        """Range sum query [l, r] — O(log n)"""
        if end is None:
            end = self.n - 1
        if r < start or end < l:
            return 0   # Out of range
        if l <= start and end <= r:
            return self.tree[node]   # Fully inside range
        mid = (start + end) // 2
        left  = self.query(l, r, 2*node+1, start, mid)
        right = self.query(l, r, 2*node+2, mid+1, end)
        return left + right

    def range_average(self, l, r):
        """Get average attendance for range [l, r]"""
        if self.n == 0 or l > r:
            return 0
        total = self.query(l, r)
        count = r - l + 1
        return round(total / count, 1)


# ============================================================
# Disjoint Set Union-Find — Unit 6: Miscellaneous Data Structures
# Used for: Grouping students into project teams
# Time Complexity: O(α(n)) — nearly O(1) with path compression
# ============================================================

class UnionFind:
    """Union-Find for student project grouping — Unit 6"""

    def __init__(self, n):
        self.parent = list(range(n))   # Each student is own parent
        self.rank   = [0] * n          # Rank for union by rank

    def find(self, x):
        """Find root with path compression — O(α(n))"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compress
        return self.parent[x]

    def union(self, x, y):
        """Merge two groups — O(α(n))"""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False   # Already in same group
        # Union by rank — attach smaller tree under larger
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

    def same_group(self, x, y):
        """Check if two students are in same team"""
        return self.find(x) == self.find(y)

    def get_groups(self, labels):
        """Return all groups as dict of root -> [members]"""
        groups = {}
        for i, label in enumerate(labels):
            root = self.find(i)
            if root not in groups:
                groups[root] = []
            groups[root].append(label)
        return list(groups.values())
