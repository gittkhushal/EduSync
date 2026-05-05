// ============================================================
// ds_misc.cpp — Units 3-6 data structures
//
// Unit 3 — Trie       : Material / subject prefix search
// Unit 4 — Skip List  : Attendance storage, O(log n) avg
// Unit 5 — Segment Tree: Attendance range queries
// Unit 6 — Union-Find : Student project group management
// ============================================================

#include <cstdlib>
#include <cstring>
#include <cstdio>
#include <cmath>
#include <ctime>
#include <vector>
#include <unordered_map>
#include <string>
#include <functional>

// ════════════════════════════════════════════════════════════
// UNIT 3 — TRIE
// ════════════════════════════════════════════════════════════

struct TrieNode {
    std::unordered_map<char, TrieNode*> children;
    bool        is_end;
    char        data[256];   // original-casing metadata
    TrieNode() : is_end(false) { data[0] = '\0'; }
};

struct Trie {
    TrieNode* root;
    Trie() { root = new TrieNode(); }
};

// ── Helpers ─────────────────────────────────────────────────
static std::string to_lower(const char* s) {
    std::string r(s);
    for (char& c : r) if (c >= 'A' && c <= 'Z') c += 32;
    return r;
}

static void collect(TrieNode* node, const std::string& prefix,
                    std::vector<std::string>& result)
{
    if (node->is_end) result.push_back(prefix);
    for (auto& [ch, child] : node->children)
        collect(child, prefix + ch, result);
}

extern "C" {

Trie* trie_create() { return new Trie(); }

void trie_insert(Trie* t, const char* word, const char* data) {
    TrieNode* node = t->root;
    std::string lower = to_lower(word);
    for (char ch : lower) {
        if (!node->children.count(ch))
            node->children[ch] = new TrieNode();
        node = node->children[ch];
    }
    node->is_end = true;
    strncpy(node->data, data ? data : word, 255);
    node->data[255] = '\0';
}

// Writes comma-separated matches into out_buf (max out_size)
// Returns number of matches found
int trie_search_prefix(Trie* t, const char* prefix,
                       char* out_buf, int out_size)
{
    TrieNode* node = t->root;
    std::string lower = to_lower(prefix);
    for (char ch : lower) {
        if (!node->children.count(ch)) {
            if (out_size > 0) out_buf[0] = '\0';
            return 0;
        }
        node = node->children[ch];
    }
    std::vector<std::string> result;
    collect(node, lower, result);

    // Serialise as newline-separated
    int written = 0;
    for (size_t i = 0; i < result.size() && written < out_size - 2; ++i) {
        int rem = out_size - written - 1;
        int n   = snprintf(out_buf + written, rem, "%s\n", result[i].c_str());
        if (n < 0 || n >= rem) break;
        written += n;
    }
    out_buf[written] = '\0';
    return (int)result.size();
}

bool trie_search_exact(Trie* t, const char* word) {
    TrieNode* node = t->root;
    for (char ch : to_lower(word)) {
        if (!node->children.count(ch)) return false;
        node = node->children[ch];
    }
    return node->is_end;
}

void trie_free(Trie* t) {
    // BFS free
    std::vector<TrieNode*> stack = {t->root};
    while (!stack.empty()) {
        TrieNode* n = stack.back(); stack.pop_back();
        for (auto& [_, child] : n->children) stack.push_back(child);
        delete n;
    }
    delete t;
}

} // extern "C" (trie section)


// ════════════════════════════════════════════════════════════
// UNIT 4 — SKIP LIST
// ════════════════════════════════════════════════════════════

static const int SKIP_MAX_LEVEL = 4;
static const double SKIP_P      = 0.5;

struct SkipNode {
    int    roll;
    double attendance_pct;
    SkipNode* forward[SKIP_MAX_LEVEL + 1];
    SkipNode(int r, double p) : roll(r), attendance_pct(p) {
        memset(forward, 0, sizeof(forward));
    }
};

struct SkipList {
    SkipNode* header;
    int       level;
    SkipList() {
        header = new SkipNode(-1, 0.0);
        level  = 0;
        srand((unsigned)time(nullptr));
    }
};

static int skip_random_level() {
    int lvl = 0;
    while ((double)rand() / RAND_MAX < SKIP_P && lvl < SKIP_MAX_LEVEL)
        lvl++;
    return lvl;
}

extern "C" {

SkipList* skip_create() { return new SkipList(); }

void skip_insert(SkipList* sl, int roll, double pct) {
    SkipNode* update[SKIP_MAX_LEVEL + 1] = {};
    SkipNode* cur = sl->header;

    for (int i = sl->level; i >= 0; --i) {
        while (cur->forward[i] && cur->forward[i]->roll < roll)
            cur = cur->forward[i];
        update[i] = cur;
    }
    cur = cur->forward[0];

    if (cur && cur->roll == roll) {
        cur->attendance_pct = pct;   // update
        return;
    }

    int new_level = skip_random_level();
    if (new_level > sl->level) {
        for (int i = sl->level + 1; i <= new_level; ++i)
            update[i] = sl->header;
        sl->level = new_level;
    }

    SkipNode* nn = new SkipNode(roll, pct);
    for (int i = 0; i <= new_level; ++i) {
        nn->forward[i]       = update[i]->forward[i];
        update[i]->forward[i] = nn;
    }
}

// Returns -1.0 if not found
double skip_search(SkipList* sl, int roll) {
    SkipNode* cur = sl->header;
    for (int i = sl->level; i >= 0; --i)
        while (cur->forward[i] && cur->forward[i]->roll < roll)
            cur = cur->forward[i];
    cur = cur->forward[0];
    return (cur && cur->roll == roll) ? cur->attendance_pct : -1.0;
}

// Write all records into parallel arrays; returns count
int skip_get_all(SkipList* sl, int* rolls, double* pcts, int max_out) {
    int count = 0;
    SkipNode* cur = sl->header->forward[0];
    while (cur && count < max_out) {
        rolls[count] = cur->roll;
        pcts[count]  = cur->attendance_pct;
        count++;
        cur = cur->forward[0];
    }
    return count;
}

void skip_free(SkipList* sl) {
    SkipNode* cur = sl->header;
    while (cur) {
        SkipNode* next = cur->forward[0];
        delete cur;
        cur = next;
    }
    delete sl;
}

} // extern "C" (skip list)


// ════════════════════════════════════════════════════════════
// UNIT 5 — SEGMENT TREE
// ════════════════════════════════════════════════════════════

struct SegTree {
    std::vector<double> tree;
    int n;

    void build(const double* data, int node, int start, int end) {
        if (start == end) { tree[node] = data[start]; return; }
        int mid = (start + end) / 2;
        build(data, 2*node+1, start,   mid);
        build(data, 2*node+2, mid+1,   end);
        tree[node] = tree[2*node+1] + tree[2*node+2];
    }

    double query(int l, int r, int node, int start, int end) {
        if (r < start || end < l) return 0;
        if (l <= start && end <= r) return tree[node];
        int mid = (start + end) / 2;
        return query(l, r, 2*node+1, start, mid)
             + query(l, r, 2*node+2, mid+1, end);
    }
};

extern "C" {

SegTree* seg_create(const double* data, int n) {
    SegTree* st = new SegTree();
    st->n = n;
    if (n > 0) {
        st->tree.resize(4 * n, 0.0);
        st->build(data, 0, 0, n - 1);
    }
    return st;
}

double seg_range_sum(SegTree* st, int l, int r) {
    if (!st || st->n == 0 || l > r) return 0.0;
    return st->query(l, r, 0, 0, st->n - 1);
}

double seg_range_avg(SegTree* st, int l, int r) {
    if (!st || st->n == 0 || l > r) return 0.0;
    double total = seg_range_sum(st, l, r);
    return total / (r - l + 1);
}

void seg_free(SegTree* st) { delete st; }

} // extern "C" (segment tree)


// ════════════════════════════════════════════════════════════
// UNIT 6 — UNION-FIND (Disjoint Set)
// ════════════════════════════════════════════════════════════

struct UnionFind {
    std::vector<int> parent;
    std::vector<int> rank_;
    int n;

    explicit UnionFind(int n) : n(n), parent(n), rank_(n, 0) {
        for (int i = 0; i < n; ++i) parent[i] = i;
    }
};

extern "C" {

UnionFind* uf_create(int n) { return new UnionFind(n); }

int uf_find(UnionFind* uf, int x) {
    if (uf->parent[x] != x)
        uf->parent[x] = uf_find(uf, uf->parent[x]);
    return uf->parent[x];
}

bool uf_union(UnionFind* uf, int x, int y) {
    int px = uf_find(uf, x), py = uf_find(uf, y);
    if (px == py) return false;
    if (uf->rank_[px] < uf->rank_[py]) std::swap(px, py);
    uf->parent[py] = px;
    if (uf->rank_[px] == uf->rank_[py]) uf->rank_[px]++;
    return true;
}

bool uf_same_group(UnionFind* uf, int x, int y) {
    return uf_find(uf, x) == uf_find(uf, y);
}

// Write root of each element into roots array; returns n
int uf_get_roots(UnionFind* uf, int* roots) {
    for (int i = 0; i < uf->n; ++i)
        roots[i] = uf_find(uf, i);
    return uf->n;
}

void uf_free(UnionFind* uf) { delete uf; }

} // extern "C" (union-find)
