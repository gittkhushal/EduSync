// ============================================================
// Fibonacci Heap — Unit 2: Priority Queues and Heaps
// Used for: Assignment deadline priority queue
// O(1) amortised insert, O(log n) extract-min
// ============================================================

#include <cmath>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#include <cstdio>

struct FibNode {
    int  days;
    char subject[128];
    char subject_code[16];
    int  degree;
    bool marked;
    FibNode* parent;
    FibNode* child;
    FibNode* left;
    FibNode* right;
};

struct FibHeap {
    FibNode* min_node;
    int      num_nodes;
};

extern "C" {

// ── Lifecycle ────────────────────────────────────────────────
FibHeap* fib_create() {
    FibHeap* h  = new FibHeap();
    h->min_node = nullptr;
    h->num_nodes = 0;
    return h;
}

void fib_destroy_node(FibNode* n) {
    if (!n) return;
    // Iterative child destruction (avoid deep recursion)
    // We'll do it from Python side since heap is rebuilt each request
    delete n;
}

// ── Internal helpers ─────────────────────────────────────────
static FibNode* make_node(int days, const char* subject, const char* code) {
    FibNode* n    = new FibNode();
    n->days       = days;
    n->degree     = 0;
    n->marked     = false;
    n->parent = n->child = nullptr;
    n->left = n->right   = n;
    strncpy(n->subject,      subject, 127); n->subject[127]     = '\0';
    strncpy(n->subject_code, code,    15);  n->subject_code[15] = '\0';
    return n;
}

static void link(FibNode* child, FibNode* parent) {
    child->left->right = child->right;
    child->right->left = child->left;

    child->parent = parent;
    if (!parent->child) {
        parent->child = child;
        child->left = child->right = child;
    } else {
        child->left          = parent->child;
        child->right         = parent->child->right;
        parent->child->right->left = child;
        parent->child->right       = child;
    }
    parent->degree++;
    child->marked = false;
}

static void consolidate(FibHeap* h) {
    int max_deg = (int)(std::log2(h->num_nodes + 1)) + 2;
    std::vector<FibNode*> A(max_deg + 1, nullptr);

    std::vector<FibNode*> roots;
    FibNode* cur = h->min_node;
    do { roots.push_back(cur); cur = cur->right; } while (cur != h->min_node);

    for (FibNode* w : roots) {
        FibNode* x = w;
        int d = x->degree;
        while (d < (int)A.size() && A[d]) {
            FibNode* y = A[d];
            if (x->days > y->days) std::swap(x, y);
            link(y, x);
            A[d] = nullptr;
            d++;
        }
        if (d < (int)A.size()) A[d] = x;
    }

    h->min_node = nullptr;
    for (FibNode* node : A) {
        if (!node) continue;
        if (!h->min_node) {
            h->min_node = node;
            node->left = node->right = node;
        } else {
            node->right              = h->min_node;
            node->left               = h->min_node->left;
            h->min_node->left->right = node;
            h->min_node->left        = node;
            if (node->days < h->min_node->days)
                h->min_node = node;
        }
    }
}

// ── Public API ───────────────────────────────────────────────
FibNode* fib_insert(FibHeap* h, int days,
                    const char* subject, const char* code)
{
    FibNode* n = make_node(days, subject, code);
    if (!h->min_node) {
        h->min_node = n;
    } else {
        n->right              = h->min_node;
        n->left               = h->min_node->left;
        h->min_node->left->right = n;
        h->min_node->left        = n;
        if (n->days < h->min_node->days)
            h->min_node = n;
    }
    h->num_nodes++;
    return n;
}

// Returns extracted min node (caller must free after reading)
FibNode* fib_extract_min(FibHeap* h) {
    FibNode* z = h->min_node;
    if (!z) return nullptr;

    if (z->child) {
        std::vector<FibNode*> children;
        FibNode* c = z->child;
        do { children.push_back(c); c = c->right; } while (c != z->child);

        for (FibNode* ch : children) {
            ch->left->right          = ch->right;
            ch->right->left          = ch->left;
            ch->right                = h->min_node;
            ch->left                 = h->min_node->left;
            h->min_node->left->right = ch;
            h->min_node->left        = ch;
            ch->parent               = nullptr;
        }
    }

    z->left->right = z->right;
    z->right->left = z->left;

    if (z == z->right) {
        h->min_node = nullptr;
    } else {
        h->min_node = z->right;
        consolidate(h);
    }
    h->num_nodes--;
    return z;
}

int         fib_size(FibHeap* h)      { return h ? h->num_nodes : 0; }
int         fib_node_days(FibNode* n) { return n ? n->days : -1; }
const char* fib_node_subject(FibNode* n) { return n ? n->subject : ""; }
const char* fib_node_code(FibNode* n)    { return n ? n->subject_code : ""; }
void        fib_free_node(FibNode* n)    { delete n; }
void        fib_free(FibHeap* h)         { delete h; }

} // extern "C"
