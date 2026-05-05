
#include <Python.h>
#include <stddef.h>

/* this block of #ifs should be kept exactly identical between
   c/_cffi_backend.c, cffi/vengine_cpy.py, cffi/vengine_gen.py
   and cffi/_cffi_include.h */
#if defined(_MSC_VER)
# include <malloc.h>   /* for alloca() */
# if _MSC_VER < 1600   /* MSVC < 2010 */
   typedef __int8 int8_t;
   typedef __int16 int16_t;
   typedef __int32 int32_t;
   typedef __int64 int64_t;
   typedef unsigned __int8 uint8_t;
   typedef unsigned __int16 uint16_t;
   typedef unsigned __int32 uint32_t;
   typedef unsigned __int64 uint64_t;
   typedef __int8 int_least8_t;
   typedef __int16 int_least16_t;
   typedef __int32 int_least32_t;
   typedef __int64 int_least64_t;
   typedef unsigned __int8 uint_least8_t;
   typedef unsigned __int16 uint_least16_t;
   typedef unsigned __int32 uint_least32_t;
   typedef unsigned __int64 uint_least64_t;
   typedef __int8 int_fast8_t;
   typedef __int16 int_fast16_t;
   typedef __int32 int_fast32_t;
   typedef __int64 int_fast64_t;
   typedef unsigned __int8 uint_fast8_t;
   typedef unsigned __int16 uint_fast16_t;
   typedef unsigned __int32 uint_fast32_t;
   typedef unsigned __int64 uint_fast64_t;
   typedef __int64 intmax_t;
   typedef unsigned __int64 uintmax_t;
# else
#  include <stdint.h>
# endif
# if _MSC_VER < 1800   /* MSVC < 2013 */
#  ifndef __cplusplus
    typedef unsigned char _Bool;
#  endif
# endif
# define _cffi_float_complex_t   _Fcomplex    /* include <complex.h> for it */
# define _cffi_double_complex_t  _Dcomplex    /* include <complex.h> for it */
#else
# include <stdint.h>
# if (defined (__SVR4) && defined (__sun)) || defined(_AIX) || defined(__hpux)
#  include <alloca.h>
# endif
# define _cffi_float_complex_t   float _Complex
# define _cffi_double_complex_t  double _Complex
#endif

#if PY_MAJOR_VERSION < 3
# undef PyCapsule_CheckExact
# undef PyCapsule_GetPointer
# define PyCapsule_CheckExact(capsule) (PyCObject_Check(capsule))
# define PyCapsule_GetPointer(capsule, name) \
    (PyCObject_AsVoidPtr(capsule))
#endif

#if PY_MAJOR_VERSION >= 3
# define PyInt_FromLong PyLong_FromLong
#endif

#define _cffi_from_c_double PyFloat_FromDouble
#define _cffi_from_c_float PyFloat_FromDouble
#define _cffi_from_c_long PyInt_FromLong
#define _cffi_from_c_ulong PyLong_FromUnsignedLong
#define _cffi_from_c_longlong PyLong_FromLongLong
#define _cffi_from_c_ulonglong PyLong_FromUnsignedLongLong
#define _cffi_from_c__Bool PyBool_FromLong

#define _cffi_to_c_double PyFloat_AsDouble
#define _cffi_to_c_float PyFloat_AsDouble

#define _cffi_from_c_int_const(x)                                        \
    (((x) > 0) ?                                                         \
        ((unsigned long long)(x) <= (unsigned long long)LONG_MAX) ?      \
            PyInt_FromLong((long)(x)) :                                  \
            PyLong_FromUnsignedLongLong((unsigned long long)(x)) :       \
        ((long long)(x) >= (long long)LONG_MIN) ?                        \
            PyInt_FromLong((long)(x)) :                                  \
            PyLong_FromLongLong((long long)(x)))

#define _cffi_from_c_int(x, type)                                        \
    (((type)-1) > 0 ? /* unsigned */                                     \
        (sizeof(type) < sizeof(long) ?                                   \
            PyInt_FromLong((long)x) :                                    \
         sizeof(type) == sizeof(long) ?                                  \
            PyLong_FromUnsignedLong((unsigned long)x) :                  \
            PyLong_FromUnsignedLongLong((unsigned long long)x)) :        \
        (sizeof(type) <= sizeof(long) ?                                  \
            PyInt_FromLong((long)x) :                                    \
            PyLong_FromLongLong((long long)x)))

#define _cffi_to_c_int(o, type)                                          \
    ((type)(                                                             \
     sizeof(type) == 1 ? (((type)-1) > 0 ? (type)_cffi_to_c_u8(o)        \
                                         : (type)_cffi_to_c_i8(o)) :     \
     sizeof(type) == 2 ? (((type)-1) > 0 ? (type)_cffi_to_c_u16(o)       \
                                         : (type)_cffi_to_c_i16(o)) :    \
     sizeof(type) == 4 ? (((type)-1) > 0 ? (type)_cffi_to_c_u32(o)       \
                                         : (type)_cffi_to_c_i32(o)) :    \
     sizeof(type) == 8 ? (((type)-1) > 0 ? (type)_cffi_to_c_u64(o)       \
                                         : (type)_cffi_to_c_i64(o)) :    \
     (Py_FatalError("unsupported size for type " #type), (type)0)))

#define _cffi_to_c_i8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[1])
#define _cffi_to_c_u8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[2])
#define _cffi_to_c_i16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[3])
#define _cffi_to_c_u16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[4])
#define _cffi_to_c_i32                                                   \
                 ((int(*)(PyObject *))_cffi_exports[5])
#define _cffi_to_c_u32                                                   \
                 ((unsigned int(*)(PyObject *))_cffi_exports[6])
#define _cffi_to_c_i64                                                   \
                 ((long long(*)(PyObject *))_cffi_exports[7])
#define _cffi_to_c_u64                                                   \
                 ((unsigned long long(*)(PyObject *))_cffi_exports[8])
#define _cffi_to_c_char                                                  \
                 ((int(*)(PyObject *))_cffi_exports[9])
#define _cffi_from_c_pointer                                             \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[10])
#define _cffi_to_c_pointer                                               \
    ((char *(*)(PyObject *, CTypeDescrObject *))_cffi_exports[11])
#define _cffi_get_struct_layout                                          \
    ((PyObject *(*)(Py_ssize_t[]))_cffi_exports[12])
#define _cffi_restore_errno                                              \
    ((void(*)(void))_cffi_exports[13])
#define _cffi_save_errno                                                 \
    ((void(*)(void))_cffi_exports[14])
#define _cffi_from_c_char                                                \
    ((PyObject *(*)(char))_cffi_exports[15])
#define _cffi_from_c_deref                                               \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[16])
#define _cffi_to_c                                                       \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[17])
#define _cffi_from_c_struct                                              \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[18])
#define _cffi_to_c_wchar_t                                               \
    ((wchar_t(*)(PyObject *))_cffi_exports[19])
#define _cffi_from_c_wchar_t                                             \
    ((PyObject *(*)(wchar_t))_cffi_exports[20])
#define _cffi_to_c_long_double                                           \
    ((long double(*)(PyObject *))_cffi_exports[21])
#define _cffi_to_c__Bool                                                 \
    ((_Bool(*)(PyObject *))_cffi_exports[22])
#define _cffi_prepare_pointer_call_argument                              \
    ((Py_ssize_t(*)(CTypeDescrObject *, PyObject *, char **))_cffi_exports[23])
#define _cffi_convert_array_from_object                                  \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[24])
#define _CFFI_NUM_EXPORTS 25

typedef struct _ctypedescr CTypeDescrObject;

static void *_cffi_exports[_CFFI_NUM_EXPORTS];
static PyObject *_cffi_types, *_cffi_VerificationError;

static int _cffi_setup_custom(PyObject *lib);   /* forward */

static PyObject *_cffi_setup(PyObject *self, PyObject *args)
{
    PyObject *library;
    int was_alive = (_cffi_types != NULL);
    (void)self; /* unused */
    if (!PyArg_ParseTuple(args, "OOO", &_cffi_types, &_cffi_VerificationError,
                                       &library))
        return NULL;
    Py_INCREF(_cffi_types);
    Py_INCREF(_cffi_VerificationError);
    if (_cffi_setup_custom(library) < 0)
        return NULL;
    return PyBool_FromLong(was_alive);
}

union _cffi_union_alignment_u {
    unsigned char m_char;
    unsigned short m_short;
    unsigned int m_int;
    unsigned long m_long;
    unsigned long long m_longlong;
    float m_float;
    double m_double;
    long double m_longdouble;
};

struct _cffi_freeme_s {
    struct _cffi_freeme_s *next;
    union _cffi_union_alignment_u alignment;
};

#ifdef __GNUC__
  __attribute__((unused))
#endif
static int _cffi_convert_array_argument(CTypeDescrObject *ctptr, PyObject *arg,
                                        char **output_data, Py_ssize_t datasize,
                                        struct _cffi_freeme_s **freeme)
{
    char *p;
    if (datasize < 0)
        return -1;

    p = *output_data;
    if (p == NULL) {
        struct _cffi_freeme_s *fp = (struct _cffi_freeme_s *)PyObject_Malloc(
            offsetof(struct _cffi_freeme_s, alignment) + (size_t)datasize);
        if (fp == NULL)
            return -1;
        fp->next = *freeme;
        *freeme = fp;
        p = *output_data = (char *)&fp->alignment;
    }
    memset((void *)p, 0, (size_t)datasize);
    return _cffi_convert_array_from_object(p, ctptr, arg);
}

#ifdef __GNUC__
  __attribute__((unused))
#endif
static void _cffi_free_array_arguments(struct _cffi_freeme_s *freeme)
{
    do {
        void *p = (void *)freeme;
        freeme = freeme->next;
        PyObject_Free(p);
    } while (freeme != NULL);
}

static int _cffi_init(void)
{
    PyObject *module, *c_api_object = NULL;

    module = PyImport_ImportModule("_cffi_backend");
    if (module == NULL)
        goto failure;

    c_api_object = PyObject_GetAttrString(module, "_C_API");
    if (c_api_object == NULL)
        goto failure;
    if (!PyCapsule_CheckExact(c_api_object)) {
        PyErr_SetNone(PyExc_ImportError);
        goto failure;
    }
    memcpy(_cffi_exports, PyCapsule_GetPointer(c_api_object, "cffi"),
           _CFFI_NUM_EXPORTS * sizeof(void *));

    Py_DECREF(module);
    Py_DECREF(c_api_object);
    return 0;

  failure:
    Py_XDECREF(module);
    Py_XDECREF(c_api_object);
    return -1;
}

#define _cffi_type(num) ((CTypeDescrObject *)PyList_GET_ITEM(_cffi_types, num))

/**********/



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


static PyObject *
_cffi_f_fib_create(PyObject *self, PyObject *noarg)
{
  FH * result;
  PyObject *pyresult;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fib_create(); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  (void)noarg; /* unused */
  pyresult = _cffi_from_c_pointer((char *)result, _cffi_type(0));
  return pyresult;
}

static PyObject *
_cffi_f_fib_extract_min(PyObject *self, PyObject *arg0)
{
  FH * x0;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;
  FN * result;
  PyObject *pyresult;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(0), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fib_extract_min(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  pyresult = _cffi_from_c_pointer((char *)result, _cffi_type(1));
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  return pyresult;
}

static PyObject *
_cffi_f_fib_free(PyObject *self, PyObject *arg0)
{
  FH * x0;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(0), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { fib_free(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_fib_free_node(PyObject *self, PyObject *arg0)
{
  FN * x0;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(1), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { fib_free_node(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
_cffi_f_fib_insert(PyObject *self, PyObject *args)
{
  FH * x0;
  int x1;
  char const * x2;
  char const * x3;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;
  FN * result;
  PyObject *pyresult;
  PyObject *arg0;
  PyObject *arg1;
  PyObject *arg2;
  PyObject *arg3;

  if (!PyArg_ParseTuple(args, "OOOO:fib_insert", &arg0, &arg1, &arg2, &arg3))
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(0), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg2, (char **)&x2);
  if (datasize != 0) {
    x2 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(3), arg2, (char **)&x2,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(3), arg3, (char **)&x3);
  if (datasize != 0) {
    x3 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(3), arg3, (char **)&x3,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fib_insert(x0, x1, x2, x3); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  pyresult = _cffi_from_c_pointer((char *)result, _cffi_type(1));
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  return pyresult;
}

static PyObject *
_cffi_f_fib_node_code(PyObject *self, PyObject *arg0)
{
  FN * x0;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;
  char const * result;
  PyObject *pyresult;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(1), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fib_node_code(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  pyresult = _cffi_from_c_pointer((char *)result, _cffi_type(3));
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  return pyresult;
}

static PyObject *
_cffi_f_fib_node_days(PyObject *self, PyObject *arg0)
{
  FN * x0;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;
  int result;
  PyObject *pyresult;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(1), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fib_node_days(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  pyresult = _cffi_from_c_int(result, int);
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  return pyresult;
}

static PyObject *
_cffi_f_fib_node_subject(PyObject *self, PyObject *arg0)
{
  FN * x0;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;
  char const * result;
  PyObject *pyresult;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(1), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(1), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fib_node_subject(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  pyresult = _cffi_from_c_pointer((char *)result, _cffi_type(3));
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  return pyresult;
}

static PyObject *
_cffi_f_fib_size(PyObject *self, PyObject *arg0)
{
  FH * x0;
  Py_ssize_t datasize;
  struct _cffi_freeme_s *large_args_free = NULL;
  int result;
  PyObject *pyresult;

  datasize = _cffi_prepare_pointer_call_argument(
      _cffi_type(0), arg0, (char **)&x0);
  if (datasize != 0) {
    x0 = ((size_t)datasize) <= 640 ? alloca((size_t)datasize) : NULL;
    if (_cffi_convert_array_argument(_cffi_type(0), arg0, (char **)&x0,
            datasize, &large_args_free) < 0)
      return NULL;
  }

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = fib_size(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  (void)self; /* unused */
  pyresult = _cffi_from_c_int(result, int);
  if (large_args_free != NULL) _cffi_free_array_arguments(large_args_free);
  return pyresult;
}

static int _cffi_setup_custom(PyObject *lib)
{
  return ((void)lib,0);
}

static PyMethodDef _cffi_methods[] = {
  {"fib_create", _cffi_f_fib_create, METH_NOARGS, NULL},
  {"fib_extract_min", _cffi_f_fib_extract_min, METH_O, NULL},
  {"fib_free", _cffi_f_fib_free, METH_O, NULL},
  {"fib_free_node", _cffi_f_fib_free_node, METH_O, NULL},
  {"fib_insert", _cffi_f_fib_insert, METH_VARARGS, NULL},
  {"fib_node_code", _cffi_f_fib_node_code, METH_O, NULL},
  {"fib_node_days", _cffi_f_fib_node_days, METH_O, NULL},
  {"fib_node_subject", _cffi_f_fib_node_subject, METH_O, NULL},
  {"fib_size", _cffi_f_fib_size, METH_O, NULL},
  {"_cffi_setup", _cffi_setup, METH_VARARGS, NULL},
  {NULL, NULL, 0, NULL}    /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef _cffi_module_def = {
  PyModuleDef_HEAD_INIT,
  "_cffi__xef1fba66xc1d211ed",
  NULL,
  -1,
  _cffi_methods,
  NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__cffi__xef1fba66xc1d211ed(void)
{
  PyObject *lib;
  lib = PyModule_Create(&_cffi_module_def);
  if (lib == NULL)
    return NULL;
  if (((void)lib,0) < 0 || _cffi_init() < 0) {
    Py_DECREF(lib);
    return NULL;
  }
#if Py_GIL_DISABLED
  PyUnstable_Module_SetGIL(lib, Py_MOD_GIL_NOT_USED);
#endif
  return lib;
}

#else

PyMODINIT_FUNC
init_cffi__xef1fba66xc1d211ed(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__xef1fba66xc1d211ed", _cffi_methods);
  if (lib == NULL)
    return;
  if (((void)lib,0) < 0 || _cffi_init() < 0)
    return;
  return;
}

#endif
