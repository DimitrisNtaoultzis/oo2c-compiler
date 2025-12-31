from oosVisitor import oosVisitor
from symbols import ClassInfo, MethodInfo

class SymbolCollector(oosVisitor):
    def __init__(self):
        super().__init__()
        self.classes = {}     #name -> ClassInfo
        self.current_class = None

    def visitStartRule(self, ctx):
        return self.visit(ctx.classes())

    def visitClasses(self, ctx):
        #kanonikes klaseis
        for c in ctx.class_def():
            self.visit(c)

        #main class
        if ctx.class_main_def() is not None:
            self.visit(ctx.class_main_def())
        return self.classes        

    def visitClass_def(self, ctx):
        name = ctx.class_name(0).getText()

        parents = []
        if len(ctx.class_name()) > 1:
            for cn in ctx.class_name()[1:]:
                parents.append(cn.getText())

        ci = ClassInfo(name, parents)
        self.classes[name] = ci
        self.current_class = ci

        #pedia
        self.visit(ctx.declarations())

        #constructors & methods
        self.visit(ctx.class_body())

        self.current_class = None
        return None

    #main
    def visitClass_main_def(self, ctx):
        name  = "Main"
        ci = ClassInfo(name, [])
        self.classes[name] = ci
        self.current_class = ci

        self.visit(ctx.declarations())

        #main method
        mm = ctx.main_body().method_main_def()
        self._handle_main_method(mm)

        self.current_class = None
        return None

    def visitDecl_line(self, ctx):
        t = ctx.types().getText()

        for idtok in ctx.ID():
            name  = idtok.getText()
            self.current_class.fields[name] = t             #πχ fields["a"] = int
        return None

    def visitConstructor_def(self, ctx):
        params = self._parse_params(ctx.parameters())
        rettype = ctx.class_name().getText()
        body_ctx = ctx.method_body()
        decl_ctx = ctx.declarations()

        mi = MethodInfo("__init__", rettype, params, body_ctx, decl_ctx)

        self.current_class.constructors.append(mi)
        self.current_class.add_method(mi)

        return None

    def visitMethod_def(self, ctx):
        name = ctx.ID().getText()
        rettype = ctx.getChild(4).getText()
        params = self._parse_params(ctx.parameters())
        body_ctx = ctx.method_body()
        decl_ctx = ctx.declarations()


        mi = MethodInfo(name, rettype, params, body_ctx, decl_ctx)
        self.current_class.add_method(mi)

        return None

    def _handle_main_method(self, ctx):
        name = "main"
        rettype = "-"
        params = [("self", None)]
        body_ctx = ctx.method_body()
        decl_ctx = ctx.declarations()

        mi = MethodInfo(name, rettype, params, body_ctx, decl_ctx)
        self.current_class.add_method(mi)

    def _parse_params(self, params_ctx):
        if params_ctx is None:
            return []

        pl = params_ctx.parlist()
        params = []

        #first param always self
        params.append(("self", None))

        for t, name in zip(pl.types(), pl.ID()):
            params.append((name.getText(), t.getText()))       #πχ ("self", None), ("x", int), ("c", Circle)

        return params    


