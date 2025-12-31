class ClassInfo:
    def __init__(self, name, parents=None):
        self.name = name
        self.parents = parents or []
        self.fields = {}
        self.constructors = []
        self.methods = {}
                                                   #krataei plirofories gia oles tis klaseis
    def add_method(self, method_info):
        if method_info.name not in self.methods:
            self.methods[method_info.name] = []
        self.methods[method_info.name].append(method_info)   #prosthetei thn overload methodo

class MethodInfo:
    def __init__(self, name, return_type, params, body_ctx, decl_ctx=None):
        self.name = name
        self.return_type = return_type
        self.params = params
        self.body_ctx = body_ctx                                            #krataei plirofories gia tis methodous
        self.decl_ctx = decl_ctx
