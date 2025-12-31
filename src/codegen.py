from oosVisitor import oosVisitor

class CodeGenVisitor(oosVisitor):
    def __init__(self, classes):
        super().__init__()
        self.classes = classes  #dict: name -> ClassInfo
        for cname, ci in self.classes.items():
            ci.all_fields = self._collect_all_fields(ci)   #ypologizei ta klironomimena fields
        self.current_class = None
        self.current_method = None
        self.output = []
        self.indent = 0
        self.local_vars = set()
        self.local_types = {}

    def emit(self, line=""):
        self.output.append("   " * self.indent + line) # morfopoihsh kodika

    def get_code(self):
        return "\n".join(self.output)
    
    def _c_type(self, t):
        if t is None:
            return "void"
        if t == "int":
            return "int"
        if t == "-":
            return "void"
        # allios einai klash -> pointer
        return f"{t}*"
    
    def generate(self):
        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")        #skeletos kodika C
        self.emit("")

        for cname in self.classes:
            self.emit(f"typedef struct {cname} {cname};")
        self.emit("")

        # struct definitions
        for cname, ci in self.classes.items():
            self.current_class = ci
            self._emit_struct(ci)
            self.emit("")

        #methods(constructors + aples)
        for cname, ci in self.classes.items():
            self.current_class = ci

            #constructors
            for ctor in ci.constructors:
                self._emit_method(ci, ctor)
                self.emit("")

            #methods
            for mname, overloads in ci.methods.items():
                if mname == "__init__":
                    continue
                for m in overloads:
                    self._emit_method(ci, m)
                    self.emit("")

        if "Main" in self.classes:
            self._emit_main(self.classes["Main"])

        return self.get_code()

    def _emit_struct(self, class_info):
        self.emit(f"struct {class_info.name} " + "{")    #struct gia kathe klasi
        self.indent += 1
        for fname, t in class_info.all_fields.items():
            ctype = self._c_type(t)
            self.emit(f"{ctype} {fname};")
        self.indent -= 1
        self.emit("};")

    def _emit_method(self, class_info, method_info):
        self.current_class = class_info
        self.current_method = method_info
        self.local_vars = set()
        self.local_types = {}

        ret = self._c_type(method_info.return_type)
        cname  = class_info.name
       

        params_sig = self._method_params_signature(method_info, cname)
        cfunc_name = self._c_method_name(cname, method_info)
        self.emit(f"{ret} {cfunc_name}({params_sig}) " + "{")
        self.indent += 1

        
        if method_info.decl_ctx is not None:
            self._emit_local_decls(method_info.decl_ctx)

        for(pname, ptype) in method_info.params:     #prosthetei parametrous stis local vars
            self.local_vars.add(pname)    

        self.visit(method_info.body_ctx)

        if self.current_method.return_type not in ("-", "int", None):   #an epistrefei antikeimeno
            self.emit("return self;")

        self.indent -= 1
        self.emit("}")


    def _method_params_signature(self, method_info, cname):
        parts = []

        #proto self panta pointer stin klash    ftiaxnei th lista parametron gia tin C function
        parts.append(f"{cname}* self")
        for name, t in method_info.params[1:]:
            ctype = self._c_type(t)
            parts.append(f"{ctype} {name}")
        return ", ".join(parts)

    def _emit_main(self, main_class_info):
        overloads = main_class_info.methods.get("main", [])
        if not overloads:
            return
        m = overloads[0]

        cfunc_name = self._c_method_name(main_class_info.name, m)

        self.emit("")
        self.emit("int main(void) {")
        self.indent += 1

        #ftiaxnoume antikeimeo Main kai kaloume Main_main(self)
        self.emit("Main* self = (Main*)malloc(sizeof(Main));")
        self.emit(f"{cfunc_name}(self);")
        self.emit("return 0;")

        self.indent -= 1
        self.emit("}")


    #visitors for bodies
    def visitMethod_body(self, ctx): #katagrafei local vars kai generate kodika gia oles tis entoles tis methodou
        decls = ctx.declarations()
        if decls is not None:
            self._emit_local_decls(decls)
        if ctx.statements() is not None:
            self.visit(ctx.statements())
        return None

    def _emit_local_decls(self, decls_ctx):
        if decls_ctx is None:
            return
        for dl in decls_ctx.decl_line():
            t = dl.types().getText()
            ctype = self._c_type(t)
            names = [idtok.getText() for idtok in dl.ID()]
            self.emit(f"{ctype} " + ", ".join(names) + ";")
            #katagrafoume tis topikes metavlites
            for n in names:
                self.local_vars.add(n)
                self.local_types[n] = t

    def visitStatements(self, ctx):
        for st in ctx.statement():
            self.visit(st)
        return None

    def visitAssignment_stat(self, ctx):

        ids = ctx.ID()
        if ids is None:
            ids_list = []
        elif isinstance(ids, list):
            ids_list = ids
        else:
            ids_list = [ids]

        if ctx.getChild(0).getText() == "self.":
            field_name = ids_list[0].getText()   
            target_code = f"self->{field_name}"

        else:
            target_name = ids_list[0].getText()
            #apli metavliti(local or field)
            if target_name in self.local_vars:
                target_code = target_name
            elif target_name in self.current_class.all_fields:
                target_code = f"self->{target_name}"

            else:
            # fallback
                target_code = target_name

        #check for constructor call
        expr = ctx.expression()
        cons = self._match_constructor_expr(expr)

        if cons is not None:
            class_name, arg_exprs = cons
            arg_count = len(arg_exprs)

        # malloc
            self.emit(f"{target_code} = ({class_name}*)malloc(sizeof({class_name}));")

            ctor_info = self._lookup_constructor(class_name, arg_count)
            if ctor_info is None:
                cfunc_name = f"{class_name}___init__"
            else:
                cfunc_name = self._c_method_name(class_name, ctor_info)

            args = [self._gen_expression(e) for e in arg_exprs]
            if args:
                self.emit(f"{cfunc_name}({target_code}, {', '.join(args)});")
            else:
                self.emit(f"{cfunc_name}({target_code});")

            return None
        expr_code = self._gen_expression(ctx.expression())  #kanoniki anathesi
        self.emit(f"{target_code} = {expr_code};")

    
            

    def visitReturn_stat(self, ctx):
        if ctx.getChildCount() == 2 and ctx.getChild(1).getText() == "self":
            self.emit("return self;")
        elif ctx.getChildCount() == 3 and ctx.getChild(1).getText() == "self.":
            field_name = ctx.ID().getText()
            self.emit(f"return self->{field_name};")
        else:
            expr_code = self._gen_expression(ctx.expression())
            self.emit(f"return {expr_code};")
        return None

    def visitDirect_call_stat(self, ctx):
        fc = ctx.func_call()
        if fc is None:
            return None

        ids = ctx.ID()
        if ids is None:
            ids_list = []
        elif isinstance(ids, list):
            ids_list = ids
        else:
            ids_list = [ids]            

        if ids_list and ctx.getChildCount() >= 2 and ctx.getChild(1).getText() == '.':  #ID '.' func_call
            obj_name = ids_list[0].getText()
        else:
            obj_name = "self"        

        call_code = self._gen_method_call_expr(obj_name, fc)
        self.emit(f"{call_code};")
        return None

    def visitPrint_stat(self, ctx):

        exprs = [ctx.expression(0)]
        n = ctx.getChildCount()

        for i in range(1, len(ctx.expression())):
            exprs.append(ctx.expression(i))

        fmt = " ".join(["%d"] * len(exprs)) + "\\n"

        args = [self._gen_expression(e) for e in exprs]
        self.emit(f'printf("{fmt}", {", ".join(args)});')
        return None

    def visitInput_stat(self, ctx):
        varname = ctx.ID().getText()

        if varname in self.local_vars:
            target = f"&{varname}"
        else:
            target = f"&self->{varname}"

        self.emit(f'scanf("%d", {target});')
        return None

    def visitIf_stat(self, ctx):
        cond_code = self._gen_condition(ctx.condition())

        self.emit(f"if ({cond_code}) " + "{")
        self.indent += 1

        #THEN block
        then_block = ctx.statements()
        if then_block is not None:
            self.visit(then_block)

        self.indent -= 1
        self.emit("}")

        #else block
        else_block = ctx.else_part().statements()
        if else_block is not None:
            self.emit("else {")
            self.indent += 1
            self.visit(ctx.else_part().statements())
            self.indent -= 1
            self.emit("}")
        return None

    def visitWhile_stat(self, ctx):
        cond_code = self._gen_condition(ctx.condition())
        self.emit(f"while ({cond_code}) " + "{")
        self.indent += 1
        if ctx.statements():
            self.visit(ctx.statements())
        self.indent -= 1
        self.emit("}")
        return None

    def _gen_condition(self, ctx):
        code = self._gen_boolterm(ctx.boolterm(0))
        for i in range(1, len(ctx.boolterm())):
            rhs = self._gen_boolterm(ctx.boolterm(i))
            code = f"({code} || {rhs})"
        return code

    def _gen_boolterm(self, ctx):
        code = self._gen_boolfactor(ctx.boolfactor(0))
        for i in range(1, len(ctx.boolfactor())):
            rhs = self._gen_boolfactor(ctx.boolfactor(i))
            code = f"({code} && {rhs})"
        return code

    def _gen_boolfactor(self, ctx):
        if ctx.getChild(0).getText() == "not":
            inner = self._gen_condition(ctx.condition())
            return f"!({inner})"
        if ctx.expression(0) is not None:
            left = self._gen_expression(ctx.expression(0))
            op = ctx.rel_oper().getText()
            right = self._gen_expression(ctx.expression(1))
            return f"({left} {op} {right})"
        
        return f"({self._gen_condition(ctx.condition())})"



    def _gen_expression(self, ctx):
        code = ""
        if ctx.optional_sign() and ctx.optional_sign().getText() == "-":
            code += "-"
        code += self._gen_term(ctx.term(0))
        for i, ao in enumerate(ctx.add_oper()):
            op = ao.getText()
            rhs = self._gen_term(ctx.term(i+1))
            code = f"({code} {op} {rhs})"
        return code

    def _gen_term(self, ctx):
        code = self._gen_factor(ctx.factor(0))
        for i, mo in enumerate(ctx.mul_oper()):
            op = mo.getText()
            rhs = self._gen_factor(ctx.factor(i+1))
            code = f"({code} {op} {rhs})"
        return code

    def _gen_factor(self, ctx):
        if ctx.INTEGER() is not None:           #akeraioi arithmoi
            return ctx.INTEGER().getText()

        if ctx.expression() is not None:            #parenthetikes ekfraseis
            return f"({self._gen_expression(ctx.expression())})"

        ids = ctx.ID()          #read ID tokens
        if ids is None:
            ids_list = []
        elif isinstance(ids, list):
            ids_list = ids
        else:
            ids_list = [ids]

        text = ctx.getText()

        fc = ctx.func_call()  #if factor is fucn call
        if fc is not None:
            child_count = ctx.getChildCount()

        
            if child_count == 4 \
                and ctx.getChild(0).getText() == "self." \
                and ctx.getChild(2).getText() == "." \
                and len(ids_list) == 1:                      #morfi self.obj.method()
                    field_name = ids_list[0].getText()
                    return self._gen_method_call_expr(field_name, fc)

        
            if child_count >= 3 \
            and ctx.getChild(1).getText() == "." \
            and len(ids_list) >= 1:                 # kanoniki morfi object.method()
                obj_name = ids_list[0].getText()
                return self._gen_method_call_expr(obj_name, fc)

        
            if child_count >= 2 and ctx.getChild(0).getText() == "self.": #self.method()
                return self._gen_method_call_expr("self", fc)

        
            return self._gen_method_call_expr("self", fc)  #method() = self.method()

    
        if len(ids_list) == 2 and ctx.getChildCount() >= 3 and ctx.getChild(1).getText() == ".": #obj.x -> obj->x
            obj = ids_list[0].getText()
            field = ids_list[1].getText()
            if obj == "self":
                return f"self->{field}"
            else:
                return f"{obj}->{field}"

   
        if text.startswith("self.") and len(ids_list) == 1:  
            field_name = ids_list[0].getText()
            return f"self->{field_name}"

    
        if len(ids_list) == 1:
            name = ids_list[0].getText()

       
            if name in self.local_vars:
                return name
       
            if name in self.current_class.all_fields:
                return f"self->{name}"

            return name

        return text



    def _gen_constructor_call(self, ctx, target_code):
        class_name = ctx.class_name().getText()
        args = []
        if ctx.arguments().arglist():          #convert arguments into C-expressions
            for a in ctx.arguments().arglist().argitem():
                args.append(self._gen_expression(a.expression()))
        code = []
        code.append(f"{target_code} = ({class_name}*)malloc(sizeof({class_name}));")

        ctor_info = self._looku_constructor(class_name, len(args))  #vriskei ton sosto constructor
        if ctor_info is not None:
            cfunc_name = self._c_method_name(class_name, ctor_info)
        else:
            cfunc_name = f"{class_name}___init__"    
    # init call
        if args:
            code.append(f"{cfunc_name}({target_code}, {', '.join(args)});")
        else:
            code.append(f"{cfunc_name}({target_code});")

        return code
    def _is_class_name(self, name):  #checkare an simvoloseira antistoixi se klasi
        return name in self.classes
    
    #check if expr is constructor call, epistrefei (class_name, [expression1, expression2, ...])
    def _match_constructor_expr(self, expr):
        fc = self._extract_func_call(expr)
        if fc is None:
            return None

        class_name = fc.ID().getText()
        if class_name not in self.classes:
            return None

        args = []
        args_ctx = fc.arguments().arglist()
        if args_ctx:
            for a in args_ctx.argitem():
                args.append(a.expression())

        return (class_name, args)

    
    def _extract_func_call(self, expr):
        if len(expr.add_oper()) > 0:
            return None
        
        term = expr.term(0)
        if len(term.mul_oper()) > 0:
            return None
        
        fac = term.factor(0)
        fc = fac.func_call()
        return fc

    def _resolve_var_type(self, name): #vriskei ton typo mias metavlitis
        if hasattr(self, "local_types") and name in self.local_types:
            return self.local_types[name]
        if name in self.current_class.all_fields:
            return self.current_class.all_fields[name]
        return None
    
    def _gen_method_call_expr(self, obj_name, fc): #metatropi obj.method(a, b) se Class_method__2(obj, a, b)
        mname = fc.ID().getText()

        args_exprs = []
        args_ctx = fc.arguments()
        if args_ctx is not None and args_ctx.arglist() is not None:
            for a in args_ctx.arglist().argitem():
                args_exprs.append((a.expression()))
        arg_count = len(args_exprs)        
        #vriskoume pio object kalei th methodo
        if obj_name is None:
            obj_code = "self"
            recv_class = self.current_class.name
        else:
            if obj_name in self.local_vars:
                obj_code = obj_name
            elif obj_name in self.current_class.all_fields:
                obj_code = f"self->{obj_name}"
            else:
                obj_code = obj_name

            vartype = self._resolve_var_type(obj_name)  #vriskoume ton typo tou object
            if vartype is None or vartype == "int":
                recv_class = self.current_class.name
            else:
                recv_class = vartype

        res = self._lookup_method(recv_class, mname, arg_count) #vriskoumer to sosto overload
        if res is None:
            owner_ci = self.classes[recv_class]
            method_info = None
        else:
            owner_ci, method_info = res

        if method_info is not None:
            cfunc_name = self._c_method_name(owner_ci.name, method_info)
        else:
            cfunc_name = f"{recv_class}_{mname}"

        if owner_ci.name != recv_class:  #metatropi antikeimenou se sosto pointer type
            obj_expr = f"({owner_ci.name}*){obj_code}"
        else:
            obj_expr = obj_code                            


        arg_codes = [self._gen_expression(e) for e in args_exprs]
        if arg_codes:
            call_args = ", ".join([obj_expr] + arg_codes)
        else:
            call_args = obj_expr        
        return f"{cfunc_name}({call_args})"  #p.x c1.add(c2, c3) paragei Circle_add__2(c1, c2, c3)

    def _gen_object_expr(self, obj): #epilogi sostis C anaparastasis antikeimenu
        if obj in self.local_vars:
            return obj
        if obj in self.current_class.fields:
            return f"self->{obj}"
        return obj

    def _collect_all_fields(self, ci):
        #Return ordered dict of all fields + inherited ones
        fields = {}

        for parent_name in ci.parents:
            parents_info = self.classes[parent_name]
            parent_fields = self._collect_all_fields(parents_info)
            fields.update(parent_fields)

        fields.update(ci.fields)

        return fields

    def _lookup_method(self, class_name, method_name, arg_count): #vriskei to sosto overload mias methodou ksekinontas apo tin klasi kai anevainontas stous goneis
        ci = self.classes[class_name]

        if method_name in ci.methods:
            overloads = ci.methods[method_name]
            for m in overloads:
                # params: [("self", None), ("x", "int") ...]
                if len(m.params) - 1 == arg_count:
                    return (ci, m)

        # if not found, search parents
        for parent in ci.parents:
            res = self._lookup_method(parent, method_name, arg_count)
            if res is not None:
                return res

        return None

    def _c_method_name(self, class_name, method_info): #dimiourgei onoma p.x Class.method(x, y) -> Class_method__2
        arity = len(method_info.params) - 1
        return f"{class_name}_{method_info.name}__{arity}"

    def _lookup_constructor(self, class_name, arg_count):
        #Vriskei to katallilo constructor overload me vasei to plithos ton parametron
        ci = self.classes[class_name]
        for ctor in ci.constructors:
            if len(ctor.params) - 1 == arg_count:
                return ctor
        return None                                                      
 
                       

            
