// ============================================================
// AVL Tree — Unit 1: Advanced Trees and Applications
// Used for: Student Record Management
// Time Complexity: O(log n) insert / search / delete
// Self-balancing BST — height guaranteed O(log n)
// Compiles to shared library called by Python via ctypes
// ============================================================

#include <cstdlib>
#include <cstring>
#include <cstdio>

// ── Data types ───────────────────────────────────────────────
struct AVLNode {
    int  roll;
    char name[64];
    char dept[64];
    int  year;
    int  height;
    AVLNode* left;
    AVLNode* right;
};

// ── Helpers ─────────────────────────────────────────────────
static int height(AVLNode* n) { return n ? n->height : 0; }

static int bf(AVLNode* n) {
    return n ? height(n->left) - height(n->right) : 0;
}

static void update_height(AVLNode* n) {
    if (!n) return;
    int lh = height(n->left), rh = height(n->right);
    n->height = 1 + (lh > rh ? lh : rh);
}

// ── Rotations ───────────────────────────────────────────────
static AVLNode* right_rotate(AVLNode* y) {
    AVLNode* x  = y->left;
    AVLNode* T2 = x->right;
    x->right = y;
    y->left  = T2;
    update_height(y);
    update_height(x);
    return x;
}

static AVLNode* left_rotate(AVLNode* x) {
    AVLNode* y  = x->right;
    AVLNode* T2 = y->left;
    y->left  = x;
    x->right = T2;
    update_height(x);
    update_height(y);
    return y;
}

static AVLNode* rebalance(AVLNode* node, int roll) {
    int b = bf(node);

    if (b > 1 && roll < node->left->roll)
        return right_rotate(node);

    if (b < -1 && roll > node->right->roll)
        return left_rotate(node);

    if (b > 1 && roll > node->left->roll) {
        node->left = left_rotate(node->left);
        return right_rotate(node);
    }

    if (b < -1 && roll < node->right->roll) {
        node->right = right_rotate(node->right);
        return left_rotate(node);
    }

    return node;
}

// ── Public API (extern "C" for ctypes) ──────────────────────
extern "C" {

AVLNode* avl_insert(AVLNode* root, int roll,
                    const char* name, const char* dept, int year)
{
    if (!root) {
        AVLNode* n  = new AVLNode();
        n->roll     = roll;
        n->height   = 1;
        n->left = n->right = nullptr;
        strncpy(n->name, name, 63); n->name[63] = '\0';
        strncpy(n->dept, dept, 63); n->dept[63] = '\0';
        n->year     = year;
        return n;
    }
    if (roll < root->roll)
        root->left  = avl_insert(root->left,  roll, name, dept, year);
    else if (roll > root->roll)
        root->right = avl_insert(root->right, roll, name, dept, year);
    else
        return root;   // duplicate

    update_height(root);
    return rebalance(root, roll);
}

// Returns pointer to found node or nullptr
AVLNode* avl_search(AVLNode* root, int roll) {
    if (!root)           return nullptr;
    if (root->roll == roll) return root;
    if (roll < root->roll)  return avl_search(root->left,  roll);
    return avl_search(root->right, roll);
}

// In-order: callback(roll, name, dept, year)
void avl_inorder(AVLNode* root,
                 void (*cb)(int, const char*, const char*, int))
{
    if (!root) return;
    avl_inorder(root->left, cb);
    cb(root->roll, root->name, root->dept, root->year);
    avl_inorder(root->right, cb);
}

// Free entire tree
void avl_free(AVLNode* root) {
    if (!root) return;
    avl_free(root->left);
    avl_free(root->right);
    delete root;
}

// Accessor helpers (so Python doesn't touch raw memory)
int         avl_roll(AVLNode* n) { return n ? n->roll : -1; }
const char* avl_name(AVLNode* n) { return n ? n->name : ""; }
const char* avl_dept(AVLNode* n) { return n ? n->dept : ""; }
int         avl_year(AVLNode* n) { return n ? n->year :  0; }

} // extern "C"
