"""
ds/heap.py — Fibonacci Heap, Unit 2
Cross-platform: tries cffi → pure Python fallback.
"""
from __future__ import annotations
import math, pathlib

_C_SOURCE = r"""
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef struct FN {
    int days,degree; int marked;
    char subject[128],subject_code[16];
    struct FN *parent,*child,*left,*right;
} FN;
typedef struct FH { FN* min_node; int num_nodes; } FH;

static FN* _mkn(int days,const char* s,const char* c){
    FN* n=(FN*)calloc(1,sizeof(FN));
    n->days=days; n->left=n->right=n;
    strncpy(n->subject,s,127); strncpy(n->subject_code,c,15);
    return n;
}
static void _link(FN* child,FN* parent){
    child->left->right=child->right; child->right->left=child->left;
    child->parent=parent;
    if(!parent->child){parent->child=child;child->left=child->right=child;}
    else{child->left=parent->child;child->right=parent->child->right;
         parent->child->right->left=child;parent->child->right=child;}
    parent->degree++; child->marked=0;
}
static void _consolidate(FH* h){
    int max_deg=(int)(log2(h->num_nodes+1))+2;
    FN** A=(FN**)calloc(max_deg+2,sizeof(FN*));
    /* collect roots */
    int cnt=0; FN* cur=h->min_node;
    do{cnt++;cur=cur->right;}while(cur!=h->min_node);
    FN** roots=(FN**)malloc(cnt*sizeof(FN*));
    cur=h->min_node; for(int i=0;i<cnt;i++){roots[i]=cur;cur=cur->right;}
    for(int i=0;i<cnt;i++){
        FN* x=roots[i]; int d=x->degree;
        while(d<=max_deg&&A[d]){
            FN* y=A[d];
            if(x->days>y->days){FN*tmp=x;x=y;y=tmp;}
            _link(y,x); A[d]=NULL; d++;
        }
        if(d<=max_deg) A[d]=x;
    }
    h->min_node=NULL;
    for(int i=0;i<=max_deg;i++){
        if(!A[i])continue;
        if(!h->min_node){h->min_node=A[i];A[i]->left=A[i]->right=A[i];}
        else{A[i]->right=h->min_node;A[i]->left=h->min_node->left;
             h->min_node->left->right=A[i];h->min_node->left=A[i];
             if(A[i]->days<h->min_node->days)h->min_node=A[i];}
    }
    free(A); free(roots);
}
FH* fib_create(){FH* h=(FH*)calloc(1,sizeof(FH));return h;}
FN* fib_insert(FH* h,int days,const char* s,const char* c){
    FN* n=_mkn(days,s,c);
    if(!h->min_node)h->min_node=n;
    else{n->right=h->min_node;n->left=h->min_node->left;
         h->min_node->left->right=n;h->min_node->left=n;
         if(n->days<h->min_node->days)h->min_node=n;}
    h->num_nodes++; return n;
}
FN* fib_extract_min(FH* h){
    FN* z=h->min_node; if(!z)return NULL;
    if(z->child){
        int cnt=0;FN*c=z->child;do{cnt++;c=c->right;}while(c!=z->child);
        FN**ch=(FN**)malloc(cnt*sizeof(FN*));
        c=z->child;for(int i=0;i<cnt;i++){ch[i]=c;c=c->right;}
        for(int i=0;i<cnt;i++){
            ch[i]->left->right=ch[i]->right;ch[i]->right->left=ch[i]->left;
            ch[i]->right=h->min_node;ch[i]->left=h->min_node->left;
            h->min_node->left->right=ch[i];h->min_node->left=ch[i];
            ch[i]->parent=NULL;
        }
        free(ch);
    }
    z->left->right=z->right;z->right->left=z->left;
    if(z==z->right)h->min_node=NULL;
    else{h->min_node=z->right;_consolidate(h);}
    h->num_nodes--; return z;
}
int fib_size(FH* h){return h?h->num_nodes:0;}
int fib_node_days(FN* n){return n?n->days:-1;}
const char* fib_node_subject(FN* n){return n?n->subject:"";}
const char* fib_node_code(FN* n){return n?n->subject_code:"";}
void fib_free_node(FN* n){free(n);}
void fib_free(FH* h){free(h);}
"""

_CACHE = pathlib.Path(__file__).parent.parent / "ds_cache"

def _load():
    try:
        from cffi import FFI
        ffi = FFI()
        ffi.cdef("""
            typedef struct FN FN; typedef struct FH FH;
            FH* fib_create(); FN* fib_insert(FH*,int,const char*,const char*);
            FN* fib_extract_min(FH*); int fib_size(FH*);
            int fib_node_days(FN*); const char* fib_node_subject(FN*);
            const char* fib_node_code(FN*); void fib_free_node(FN*); void fib_free(FH*);
        """)
        _CACHE.mkdir(exist_ok=True)
        lib = ffi.verify(_C_SOURCE, tmpdir=str(_CACHE),
                         libraries=["m"], extra_compile_args=["-O2"])
        return ffi, lib
    except Exception:
        return None, None

_ffi, _lib = _load()
_CPP = _lib is not None

# ── Pure Python fallback ──────────────────────────────────────
import heapq as _hq

class _PyHeap:
    def __init__(self): self._h=[]
    def insert(self,days,sub,code): _hq.heappush(self._h,(days,sub,code))
    def extract_min(self):
        if not self._h: return None
        d,s,c=_hq.heappop(self._h); return {'days':d,'subject':s,'subject_code':c}
    def size(self): return len(self._h)
    def get_all_sorted(self):
        tmp=sorted(self._h); return [{'days':d,'subject':s,'subject_code':c} for d,s,c in tmp]

class FibonacciHeap:
    """Unit 2 — Fibonacci Heap priority queue. C via cffi or pure-Python fallback."""
    BACKEND = "C (cffi)" if _CPP else "Python (heapq fallback)"

    def __init__(self):
        if _CPP: self._h = _lib.fib_create()
        else:    self._py = _PyHeap()

    def insert(self, days:int, subject:str, subject_code:str=""):
        if _CPP: _lib.fib_insert(self._h, days, subject.encode(), subject_code.encode())
        else:    self._py.insert(days, subject, subject_code)

    def extract_min(self) -> dict|None:
        if _CPP:
            ptr = _lib.fib_extract_min(self._h)
            if not ptr or ptr==_ffi.NULL: return None
            r={'days':_lib.fib_node_days(ptr),
               'subject':_ffi.string(_lib.fib_node_subject(ptr)).decode(),
               'subject_code':_ffi.string(_lib.fib_node_code(ptr)).decode()}
            _lib.fib_free_node(ptr); return r
        return self._py.extract_min()

    def get_all_sorted(self) -> list[dict]:
        if _CPP:
            extracted=[]
            while _lib.fib_size(self._h)>0:
                ptr=_lib.fib_extract_min(self._h)
                if not ptr or ptr==_ffi.NULL: break
                extracted.append({'days':_lib.fib_node_days(ptr),
                    'subject':_ffi.string(_lib.fib_node_subject(ptr)).decode(),
                    'subject_code':_ffi.string(_lib.fib_node_code(ptr)).decode()})
                _lib.fib_free_node(ptr)
            for item in extracted:
                _lib.fib_insert(self._h,item['days'],
                                item['subject'].encode(),item['subject_code'].encode())
            return extracted
        return self._py.get_all_sorted()

    def size(self) -> int:
        return _lib.fib_size(self._h) if _CPP else self._py.size()

    def __del__(self):
        try:
            if _CPP: _lib.fib_free(self._h)
        except Exception: pass
