from string import Template
class Macro(): 
    """Macro class"""
    def __init__(self,line):
        """Macro definition line"""
        text = line
        istart = []  
        istart_args = []
        d = []
        dargs = []

        for i, c in enumerate(text):
            if c == '{':
                 istart.append(i)
            if c == '}':
                try:
                    d.append((istart.pop(), i))
                except IndexError:
                    pass
            if c == '[':
                 istart_args.append(i)
            if c == ']':
                try:
                    dargs.append((istart_args.pop(), i))
                except IndexError:
                    pass
        if istart:  
            print('Too many opening parentheses')

        name = line[d[0][0]+1:d[0][1]]
        def_str = line[d[-1][0]+1:d[-1][1]] 
        if dargs == []:  
            nargs = 0
            def_func = lambda args: def_str
        else:
            nargs = int(line[dargs[0][0]+1:dargs[0][1]])
            def_temp = def_str.replace('{','{{')
            def_temp = def_temp.replace('}','}}')
            for i in range(nargs):
                def_temp = def_temp.replace('#{:d}'.format(i+1),'$v{:d}'.format(i+1))
            def_temp = Template(def_temp)
            def_func = lambda args: def_temp.substitute(**{'v{:d}'.format(i):a for i,a in enumerate(args,start=1)})
  
        self.name = name
        self.nargs = nargs
        self.def_str = def_str
        self.def_func = def_func
        self.orig_str = line

    def grab_arg(self,text,delim='{}'):
        """Grab the arguments"""
        ind = text.find(self.name)
        newtext = text[ind:]
        res = []
        ind_f = ind
        for j in range(self.nargs):
            istart = []  
            d = []
            n = 0
            first = True
            for i, c in enumerate(newtext):
                if c == '{':
                    istart.append(i)
                    n +=1 
                    first = False
                if c == '}':
                    try:
                        d.append((istart.pop(), i))
                        n -= 1
                    except IndexError:
                        pass
                if n==0 and not first:
                    break
            istart, iend = d[-1]
            ind_f += iend+1
            res.append(newtext[istart+1:iend])
            newtext = newtext[iend+1:]
        return res,(ind,ind_f)
    def find(self,text):
        """Find instance of macro in the text"""
        ind = text.find(self.name)
        return text[ind+len(self.name):]
    def replace(self,text):
        """Replace all instances of the macro in the text"""
        newtext = text
        if self.nargs == 0:
            while newtext.find(self.name) != -1:
                ind = newtext.find(self.name)
                newtext = newtext.replace(self.name,self.def_str,1)
        else:
            while newtext.find(self.name) != -1:
                args,lims = self.grab_arg(newtext)
                newtext = newtext[:lims[0]] + self.def_func(args) + newtext[lims[1]:]            
        return newtext
    def __str__(self):
        return 'Name: {}\nArgs: {:d}\nDef: {}\n'.format(self.name, self.nargs,self.def_str)
    def __repr__(self):
        return self.__str__()

def get_macros(texfile):
    """Grab the macro definitions"""
    with open(texfile,'r') as f:
        lines = f.readlines()
    lines = [line.strip() for line in lines if 'command' in line and 'renewcommand*' not in line]
    return [Macro(line) for line in lines]
def replace_macros(texfile,macros,save=None):
    """Replace all of the macros in the tex file"""
    with open(texfile,'r') as f:
        text = f.read()
    while sum([text.count(m.name) for m in macros]) > 0:
        for m in macros:
            text = m.replace(text)
    if save is not None:
        with open(save,'w') as f:
            f.write(text)
    return text

def find_input_files(texfile,mydir=''):
    """Search for extra tex files"""
    with open(mydir + texfile,'r') as f:
        lines = f.readlines()

    temp = [re.findall('\{.*?\}',line.strip())[0][1:-1] for line in lines if '\input' in line]
    files = []
    for t in temp:
        if '.tex' not in t:
            files.append(t + '.tex')
        else:
            files.append(t)
    return files

def replace_project(main_file,mydir=''):
    """Replace all of the used tex files in main.tex"""
    macros = get_macros(mydir + main_file)
    for f in find_input_files(main_file,mydir=mydir):
        replace_macros(mydir+f,macros,save=mydir+f)