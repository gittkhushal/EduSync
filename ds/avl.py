"""
ds/avl.py — AVL Tree, Unit 1
Cross-platform: tries cffi (compiles C at runtime) → pure Python fallback.
No manual build steps needed on Windows.
"""
from __future__ import annotations
import pathlib

_C_SOURCE = r"""
#include <stdlib.h>
#include <string.h>
typedef struct AVLNode {
    int roll,height,year; char name[64],dept[64];
    struct AVLNode *left,*right;
} AVLNode;
static int _h(AVLNode* n){return n?n->height:0;}
static int _bf(AVLNode* n){return n?_h(n->left)-_h(n->right):0;}
static void _uh(AVLNode* n){if(!n)return;int l=_h(n->left),r=_h(n->right);n->height=1+(l>r?l:r);}
static AVLNode* _rr(AVLNode* y){AVLNode*x=y->left,*T2=x->right;x->right=y;y->left=T2;_uh(y);_uh(x);return x;}
static AVLNode* _lr(AVLNode* x){AVLNode*y=x->right,*T2=y->left;y->left=x;x->right=T2;_uh(x);_uh(y);return y;}
static AVLNode* _bal(AVLNode* n,int roll){
    int b=_bf(n);
    if(b>1&&roll<n->left->roll)return _rr(n);
    if(b<-1&&roll>n->right->roll)return _lr(n);
    if(b>1&&roll>n->left->roll){n->left=_lr(n->left);return _rr(n);}
    if(b<-1&&roll<n->right->roll){n->right=_rr(n->right);return _lr(n);}
    return n;
}
AVLNode* avl_insert(AVLNode* root,int roll,const char* name,const char* dept,int year){
    if(!root){AVLNode* n=(AVLNode*)calloc(1,sizeof(AVLNode));n->roll=roll;n->height=1;n->year=year;
    strncpy(n->name,name,63);strncpy(n->dept,dept,63);return n;}
    if(roll<root->roll)root->left=avl_insert(root->left,roll,name,dept,year);
    else if(roll>root->roll)root->right=avl_insert(root->right,roll,name,dept,year);
    else return root;
    _uh(root);return _bal(root,roll);
}
AVLNode* avl_search(AVLNode* root,int roll){
    if(!root)return NULL;if(root->roll==roll)return root;
    if(roll<root->roll)return avl_search(root->left,roll);
    return avl_search(root->right,roll);
}
void avl_inorder(AVLNode* root,void(*cb)(int,const char*,const char*,int)){
    if(!root)return;avl_inorder(root->left,cb);cb(root->roll,root->name,root->dept,root->year);avl_inorder(root->right,cb);
}
void avl_free(AVLNode* root){if(!root)return;avl_free(root->left);avl_free(root->right);free(root);}
int avl_roll(AVLNode* n){return n?n->roll:-1;}
const char* avl_name(AVLNode* n){return n?n->name:"";}
const char* avl_dept(AVLNode* n){return n?n->dept:"";}
int avl_year(AVLNode* n){return n?n->year:0;}
"""

_CACHE = pathlib.Path(__file__).parent.parent / "ds_cache"

def _load():
    try:
        from cffi import FFI
        ffi = FFI()
        ffi.cdef("""
            typedef struct AVLNode AVLNode;
            AVLNode* avl_insert(AVLNode*, int, const char*, const char*, int);
            AVLNode* avl_search(AVLNode*, int);
            void avl_inorder(AVLNode*, void(*)(int,const char*,const char*,int));
            void avl_free(AVLNode*);
            int avl_roll(AVLNode*); const char* avl_name(AVLNode*);
            const char* avl_dept(AVLNode*); int avl_year(AVLNode*);
        """)
        _CACHE.mkdir(exist_ok=True)
        lib = ffi.verify(_C_SOURCE, tmpdir=str(_CACHE), extra_compile_args=["-O2"])
        return ffi, lib
    except Exception:
        return None, None

_ffi, _lib = _load()
_CPP = _lib is not None

# ── Pure Python fallback ──────────────────────────────────────
class _N:
    __slots__=('roll','name','dept','year','height','left','right')
    def __init__(self,r,n,d,y): self.roll=r;self.name=n;self.dept=d;self.year=y;self.height=1;self.left=self.right=None
def _ph(n): return n.height if n else 0
def _puf(n):
    if n: n.height=1+max(_ph(n.left),_ph(n.right))
def _prr(y): x=y.left;T=x.right;x.right=y;y.left=T;_puf(y);_puf(x);return x
def _plr(x): y=x.right;T=y.left;y.left=x;x.right=T;_puf(x);_puf(y);return y
def _pbal(n,roll):
    b=(_ph(n.left)-_ph(n.right))
    if b>1 and roll<n.left.roll: return _prr(n)
    if b<-1 and roll>n.right.roll: return _plr(n)
    if b>1 and roll>n.left.roll: n.left=_plr(n.left);return _prr(n)
    if b<-1 and roll<n.right.roll: n.right=_prr(n.right);return _plr(n)
    return n
def _pins(root,roll,name,dept,year):
    if not root: return _N(roll,name,dept,year)
    if roll<root.roll: root.left=_pins(root.left,roll,name,dept,year)
    elif roll>root.roll: root.right=_pins(root.right,roll,name,dept,year)
    else: return root
    _puf(root); return _pbal(root,roll)
def _psearch(root,roll):
    if not root: return None
    if root.roll==roll: return root
    return _psearch(root.left,roll) if roll<root.roll else _psearch(root.right,roll)
def _pio(root,acc):
    if not root: return
    _pio(root.left,acc)
    acc.append({'roll':root.roll,'name':root.name,'dept':root.dept,'year':root.year})
    _pio(root.right,acc)

class AVLTree:
    """Unit 1 — Self-balancing BST. Uses C via cffi when compiler available."""
    BACKEND = "C (cffi)" if _CPP else "Python (fallback)"

    def insert(self, root, roll, name, dept="CE", year=2):
        if _CPP:
            return _lib.avl_insert(root or _ffi.NULL, roll, name.encode(), dept.encode(), year)
        return _pins(root, roll, name, dept, year)

    def search(self, root, roll) -> dict|None:
        if _CPP:
            ptr = _lib.avl_search(root or _ffi.NULL, roll)
            if ptr==_ffi.NULL: return None
            return {'roll':_lib.avl_roll(ptr), 'name':_ffi.string(_lib.avl_name(ptr)).decode(),
                    'dept':_ffi.string(_lib.avl_dept(ptr)).decode(), 'year':_lib.avl_year(ptr)}
        n=_psearch(root,roll)
        return {'roll':n.roll,'name':n.name,'dept':n.dept,'year':n.year} if n else None

    def inorder(self, root) -> list[dict]:
        if _CPP:
            result=[]
            @_ffi.callback("void(int,const char*,const char*,int)")
            def cb(roll,name,dept,year):
                result.append({'roll':roll,'name':_ffi.string(name).decode(),
                               'dept':_ffi.string(dept).decode(),'year':year})
            _lib.avl_inorder(root or _ffi.NULL, cb); return result
        acc=[]; _pio(root,acc); return acc

    def free(self, root):
        if _CPP and root: _lib.avl_free(root)
