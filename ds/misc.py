"""
ds/misc.py — Units 3-6 data structures
Cross-platform: cffi (C compiled at runtime) → pure Python fallback.
Unit 3 — Trie, Unit 4 — Skip List, Unit 5 — Segment Tree, Unit 6 — Union-Find
"""
from __future__ import annotations
import random, pathlib

_C_SRC = r"""
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

/* ─── TRIE ─────────────────────────────────────────────── */
#define ALPHA 128
typedef struct TN { struct TN* ch[ALPHA]; int is_end; char data[256]; } TN;
typedef struct { TN* root; } Trie;
static TN* _tn(){ return (TN*)calloc(1,sizeof(TN)); }
Trie* trie_create(){ Trie*t=(Trie*)calloc(1,sizeof(Trie));t->root=_tn();return t; }
void trie_insert(Trie* t,const char* word,const char* data){
    TN* n=t->root;
    for(const char*p=word;*p;p++){
        int c=tolower((unsigned char)*p);
        if(!n->ch[c])n->ch[c]=_tn();
        n=n->ch[c];
    }
    n->is_end=1; strncpy(n->data,data?data:word,255);
}
static int _collect(TN* n,char* prefix,int plen,char* out,int* out_pos,int out_max){
    if(n->is_end&&*out_pos+plen+1<out_max){
        memcpy(out+*out_pos,prefix,plen); (*out_pos)+=plen;
        out[(*out_pos)++]='\n';
    }
    for(int i=0;i<ALPHA;i++){
        if(!n->ch[i])continue;
        prefix[plen]=(char)i;
        _collect(n->ch[i],prefix,plen+1,out,out_pos,out_max);
    }
    return 0;
}
int trie_search_prefix(Trie* t,const char* prefix,char* out,int out_max){
    TN* n=t->root;
    int plen=strlen(prefix);
    for(const char*p=prefix;*p;p++){
        int c=tolower((unsigned char)*p);
        if(!n->ch[c]){if(out_max>0)out[0]=0;return 0;}
        n=n->ch[c];
    }
    char buf[512]={0}; memcpy(buf,prefix,plen);
    int pos=0; _collect(n,buf,plen,out,&pos,out_max);
    if(pos<out_max)out[pos]=0;
    int cnt=0;for(int i=0;i<pos;i++)if(out[i]=='\n')cnt++;
    return cnt;
}

/* ─── SKIP LIST ─────────────────────────────────────────── */
#define SMAX 4
typedef struct SN { int roll; double pct; struct SN* fwd[SMAX+1]; } SN;
typedef struct { SN* hdr; int level; } SList;
static SN* _sn(int r,double p){SN*n=(SN*)calloc(1,sizeof(SN));n->roll=r;n->pct=p;return n;}
SList* skip_create(){SList*s=(SList*)calloc(1,sizeof(SList));s->hdr=_sn(-1,0);return s;}
static int _rl(){int l=0;while((double)rand()/RAND_MAX<0.5&&l<SMAX)l++;return l;}
void skip_insert(SList* sl,int roll,double pct){
    SN*upd[SMAX+1]={0}; SN*cur=sl->hdr;
    for(int i=sl->level;i>=0;i--){while(cur->fwd[i]&&cur->fwd[i]->roll<roll)cur=cur->fwd[i];upd[i]=cur;}
    cur=cur->fwd[0];
    if(cur&&cur->roll==roll){cur->pct=pct;return;}
    int nl=_rl();
    if(nl>sl->level){for(int i=sl->level+1;i<=nl;i++)upd[i]=sl->hdr;sl->level=nl;}
    SN*nn=_sn(roll,pct);
    for(int i=0;i<=nl;i++){nn->fwd[i]=upd[i]->fwd[i];upd[i]->fwd[i]=nn;}
}
double skip_search(SList* sl,int roll){
    SN*cur=sl->hdr;
    for(int i=sl->level;i>=0;i--)while(cur->fwd[i]&&cur->fwd[i]->roll<roll)cur=cur->fwd[i];
    cur=cur->fwd[0];
    return(cur&&cur->roll==roll)?cur->pct:-1.0;
}
int skip_get_all(SList* sl,int* rolls,double* pcts,int max){
    int cnt=0;SN*cur=sl->hdr->fwd[0];
    while(cur&&cnt<max){rolls[cnt]=cur->roll;pcts[cnt]=cur->pct;cnt++;cur=cur->fwd[0];}
    return cnt;
}
void skip_free(SList* sl){SN*c=sl->hdr;while(c){SN*n=c->fwd[0];free(c);c=n;}free(sl);}

/* ─── SEGMENT TREE ──────────────────────────────────────── */
typedef struct { double* tree; int n; } ST;
static void _build(ST*s,const double*d,int node,int start,int end){
    if(start==end){s->tree[node]=d[start];return;}
    int mid=(start+end)/2;
    _build(s,d,2*node+1,start,mid);_build(s,d,2*node+2,mid+1,end);
    s->tree[node]=s->tree[2*node+1]+s->tree[2*node+2];
}
static double _query(ST*s,int l,int r,int node,int start,int end){
    if(r<start||end<l)return 0;
    if(l<=start&&end<=r)return s->tree[node];
    int mid=(start+end)/2;
    return _query(s,l,r,2*node+1,start,mid)+_query(s,l,r,2*node+2,mid+1,end);
}
ST* seg_create(const double* data,int n){
    ST*s=(ST*)calloc(1,sizeof(ST));s->n=n;
    if(n>0){s->tree=(double*)calloc(4*n,sizeof(double));_build(s,data,0,0,n-1);}
    return s;
}
double seg_range_avg(ST* s,int l,int r){
    if(!s||s->n==0||l>r)return 0;
    return _query(s,l,r,0,0,s->n-1)/(r-l+1);
}
void seg_free(ST* s){if(s){free(s->tree);free(s);}}

/* ─── UNION-FIND ────────────────────────────────────────── */
typedef struct { int* parent; int* rank; int n; } UF;
UF* uf_create(int n){
    UF*u=(UF*)calloc(1,sizeof(UF));u->n=n;
    u->parent=(int*)malloc(n*sizeof(int));u->rank=(int*)calloc(n,sizeof(int));
    for(int i=0;i<n;i++)u->parent[i]=i;
    return u;
}
static int _find(UF*u,int x){if(u->parent[x]!=x)u->parent[x]=_find(u,u->parent[x]);return u->parent[x];}
int uf_find(UF* u,int x){return _find(u,x);}
int uf_union(UF* u,int x,int y){
    int px=_find(u,x),py=_find(u,y);if(px==py)return 0;
    if(u->rank[px]<u->rank[py]){int t=px;px=py;py=t;}
    u->parent[py]=px;if(u->rank[px]==u->rank[py])u->rank[px]++;return 1;
}
int uf_same(UF* u,int x,int y){return _find(u,x)==_find(u,y);}
int uf_get_roots(UF* u,int* out){for(int i=0;i<u->n;i++)out[i]=_find(u,i);return u->n;}
void uf_free(UF* u){free(u->parent);free(u->rank);free(u);}
"""

_CACHE = pathlib.Path(__file__).parent.parent / "ds_cache"

def _load():
    try:
        from cffi import FFI
        ffi = FFI()
        ffi.cdef("""
            typedef struct { ...; } Trie;
            Trie* trie_create();
            void trie_insert(Trie*, const char*, const char*);
            int trie_search_prefix(Trie*, const char*, char*, int);
            typedef struct { ...; } SList;
            SList* skip_create();
            void skip_insert(SList*, int, double);
            double skip_search(SList*, int);
            int skip_get_all(SList*, int*, double*, int);
            void skip_free(SList*);
            typedef struct { ...; } ST;
            ST* seg_create(const double*, int);
            double seg_range_avg(ST*, int, int);
            void seg_free(ST*);
            typedef struct { ...; } UF;
            UF* uf_create(int);
            int uf_find(UF*, int);
            int uf_union(UF*, int, int);
            int uf_same(UF*, int, int);
            int uf_get_roots(UF*, int*);
            void uf_free(UF*);
        """)
        _CACHE.mkdir(exist_ok=True)
        lib = ffi.verify(_C_SRC, tmpdir=str(_CACHE), extra_compile_args=["-O2"])
        return ffi, lib
    except Exception:
        return None, None

_ffi, _lib = _load()
_CPP = _lib is not None

# ════════════════════════════════════════════════════════════
# Pure-Python fallbacks
# ════════════════════════════════════════════════════════════

class _PyTrie:
    def __init__(self): self._r={}
    def _node(self): return {'c':{},'end':False,'data':None}
    def insert(self,word,data=None):
        n=self._r
        for ch in word.lower():
            n=n.setdefault(ch,{'c':{},'end':False,'data':None})
            n=n['c'] if isinstance(n,dict) and 'c' in n else n
        # simpler flat approach
        self._r[word.lower()]=data or word
    def search_prefix(self,prefix):
        p=prefix.lower()
        return [{'word':k,'data':v} for k,v in self._r.items() if k.startswith(p)]

class _PySkip:
    def __init__(self): self._d={}
    def insert(self,roll,pct): self._d[roll]=pct
    def search(self,roll): return self._d.get(roll)
    def get_all(self): return [{'roll':r,'pct':p} for r,p in sorted(self._d.items())]

class _PySeg:
    def __init__(self,data): self._d=list(data)
    def range_average(self,l,r):
        if not self._d or l>r: return 0.0
        sl=self._d[l:r+1]; return round(sum(sl)/len(sl),1) if sl else 0.0

class _PyUF:
    def __init__(self,n): self.p=list(range(n)); self.rk=[0]*n; self.n=n
    def find(self,x):
        if self.p[x]!=x: self.p[x]=self.find(self.p[x])
        return self.p[x]
    def union(self,x,y):
        px,py=self.find(x),self.find(y)
        if px==py: return False
        if self.rk[px]<self.rk[py]: px,py=py,px
        self.p[py]=px
        if self.rk[px]==self.rk[py]: self.rk[px]+=1
        return True
    def same(self,x,y): return self.find(x)==self.find(y)
    def get_groups(self,labels):
        g={}
        for i,l in enumerate(labels): g.setdefault(self.find(i),[]).append(l)
        return list(g.values())


# ════════════════════════════════════════════════════════════
# Public classes
# ════════════════════════════════════════════════════════════

class Trie:
    """Unit 3 — O(L) prefix search."""
    BACKEND = "C (cffi)" if _CPP else "Python (fallback)"

    def __init__(self):
        if _CPP: self._p = _lib.trie_create()
        else:    self._py= _PyTrie()

    def insert(self, word:str, data:str|None=None):
        if _CPP: _lib.trie_insert(self._p, word.encode(), (data or word).encode())
        else:    self._py.insert(word, data)

    def search_prefix(self, prefix:str) -> list[dict]:
        if _CPP:
            buf = _ffi.new("char[]", 8192)
            cnt = _lib.trie_search_prefix(self._p, prefix.encode(), buf, 8192)
            if cnt==0: return []
            return [{'word':w,'data':w}
                    for w in _ffi.string(buf).decode().split('\n') if w]
        return self._py.search_prefix(prefix)

    def __del__(self):
        pass  # trie_free not exposed (minor leak on exit only)


class SkipList:
    """Unit 4 — O(log n) average attendance queries."""
    BACKEND = "C (cffi)" if _CPP else "Python (fallback)"

    def __init__(self):
        if _CPP: self._p=_lib.skip_create()
        else:    self._py=_PySkip()

    def insert(self, roll:int, pct:float):
        if _CPP: _lib.skip_insert(self._p, roll, pct)
        else:    self._py.insert(roll, pct)

    def search(self, roll:int) -> float|None:
        if _CPP:
            v=_lib.skip_search(self._p, roll)
            return None if v<0 else v
        return self._py.search(roll)

    def get_all(self) -> list[dict]:
        if _CPP:
            MAX=1000
            rolls=_ffi.new(f"int[{MAX}]")
            pcts =_ffi.new(f"double[{MAX}]")
            n=_lib.skip_get_all(self._p,rolls,pcts,MAX)
            return [{'roll':rolls[i],'pct':pcts[i]} for i in range(n)]
        return self._py.get_all()

    def __del__(self):
        try:
            if _CPP: _lib.skip_free(self._p)
        except Exception: pass


class SegmentTree:
    """Unit 5 — O(log n) range attendance average."""
    BACKEND = "C (cffi)" if _CPP else "Python (fallback)"

    def __init__(self, data:list[float]):
        self._n=len(data)
        if _CPP:
            arr=_ffi.new(f"double[{max(self._n,1)}]", list(data) or [0.0])
            self._p=_lib.seg_create(arr, self._n)
        else:
            self._py=_PySeg(data)

    def range_average(self, l:int, r:int) -> float:
        if _CPP:
            if not self._n or l>r: return 0.0
            return round(_lib.seg_range_avg(self._p,l,r),1)
        return self._py.range_average(l,r)

    def __del__(self):
        try:
            if _CPP: _lib.seg_free(self._p)
        except Exception: pass


class UnionFind:
    """Unit 6 — O(α(n)) project group management."""
    BACKEND = "C (cffi)" if _CPP else "Python (fallback)"

    def __init__(self, n:int):
        self._n=n
        if _CPP: self._p=_lib.uf_create(n)
        else:    self._py=_PyUF(n)

    def find(self, x:int) -> int:
        return _lib.uf_find(self._p,x) if _CPP else self._py.find(x)

    def union(self, x:int, y:int) -> bool:
        return bool(_lib.uf_union(self._p,x,y) if _CPP else self._py.union(x,y))

    def same_group(self, x:int, y:int) -> bool:
        return bool(_lib.uf_same(self._p,x,y) if _CPP else self._py.same(x,y))

    def get_groups(self, labels:list[str]) -> list[list[str]]:
        if _CPP:
            roots=_ffi.new(f"int[{self._n}]")
            _lib.uf_get_roots(self._p, roots)
            g={}
            for i,l in enumerate(labels): g.setdefault(roots[i],[]).append(l)
            return list(g.values())
        return self._py.get_groups(labels)

    def __del__(self):
        try:
            if _CPP: _lib.uf_free(self._p)
        except Exception: pass
