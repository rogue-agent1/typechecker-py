#!/usr/bin/env python3
"""Type checker with inference (Hindley-Milner style)."""
import sys

class Type:
    pass
class TInt(Type):
    def __repr__(self): return "Int"
class TBool(Type):
    def __repr__(self): return "Bool"
class TStr(Type):
    def __repr__(self): return "Str"
class TFun(Type):
    def __init__(self,arg,ret): self.arg=arg; self.ret=ret
    def __repr__(self): return f"({self.arg} -> {self.ret})"
class TVar(Type):
    _counter=0
    def __init__(self): TVar._counter+=1; self.id=TVar._counter; self.instance=None
    def __repr__(self):
        if self.instance: return repr(self.instance)
        return f"t{self.id}"

def unify(t1, t2):
    t1=prune(t1); t2=prune(t2)
    if isinstance(t1,TVar): t1.instance=t2; return
    if isinstance(t2,TVar): t2.instance=t1; return
    if type(t1)==type(t2):
        if isinstance(t1,(TInt,TBool,TStr)): return
        if isinstance(t1,TFun): unify(t1.arg,t2.arg); unify(t1.ret,t2.ret); return
    raise TypeError(f"Cannot unify {t1} with {t2}")

def prune(t):
    if isinstance(t,TVar) and t.instance: t.instance=prune(t.instance); return t.instance
    return t

def infer(expr, env):
    if isinstance(expr,int): return TInt()
    if isinstance(expr,bool): return TBool()
    if isinstance(expr,str):
        if expr in env: return env[expr]
        return TStr()
    if isinstance(expr,list):
        if expr[0]=="lambda":
            arg_type=TVar(); body_env={**env,expr[1]:arg_type}
            ret_type=infer(expr[2],body_env)
            return TFun(arg_type,ret_type)
        if expr[0]=="let":
            val_type=infer(expr[2],env)
            return infer(expr[3],{**env,expr[1]:val_type})
        if expr[0] in ("+","-","*","/"):
            for operand in expr[1:]: unify(infer(operand,env),TInt())
            return TInt()
        if expr[0] in ("==","<",">"):
            return TBool()
        if expr[0]=="if":
            unify(infer(expr[1],env),TBool())
            t=infer(expr[2],env); f=infer(expr[3],env); unify(t,f); return t
        fn_type=infer(expr[0],env); arg_type=infer(expr[1],env)
        ret=TVar(); unify(fn_type,TFun(arg_type,ret)); return prune(ret)
    return TVar()

if __name__ == "__main__":
    env={"add":TFun(TInt(),TFun(TInt(),TInt())),"not":TFun(TBool(),TBool())}
    exprs=[42, True, ["+",1,2], ["lambda","x",["+","x",1]],
           ["let","x",10,["+","x",5]], ["if",True,1,2]]
    for e in exprs: print(f"  {str(e):35s} : {infer(e,env)}")
