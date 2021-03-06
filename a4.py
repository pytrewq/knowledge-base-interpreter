class KB(object):
    def __init__(self, rules={}, atoms=[]):
        self.rules = rules
        self.update_num_rules()
        self.atoms = atoms

    def __str__(self):
        output = "\nRules:\n"
        for head in self.rules:
            output += self.parse_rule(head, self.rules[head]) + "\n"
        output += "\nAtoms:\n"
        for atom in self.atoms:
            output += atom + "\n"
        return output

    def update_num_rules(self):
        self.num_rules = len(self.rules)

    def load_kb(self, rules):
        self.rules = rules
        self.update_num_rules()
        self.print_rules()
        print ("\n" + str(self.num_rules) + " added to the knowledge base")

    def add_atom(self, atom):
        # Do not add atoms that are already in the knowledge base
        if atom in self.atoms:
            print ("Atom '" + atom + "' is already in the knowledge base")
            return
        self.atoms.append(atom)
        print ("Added '" + atom + "' to the knowledge base")

    def clear_all(self):
        self.rules = {}
        self.update_num_rules()
        self.atoms = []
        print ("Cleared all rules and atoms from the knowledge base")

    def clear_atoms(self):
        self.atoms = []
        print ("Cleared all atoms from the knowledge base")

    def print_rules(self):
        rules = self.rules
        for head in rules:
            conditions = rules[head]
            print(self.parse_rule(head, conditions))

    def parse_rule(self, head, conditions):
        conditions_string = " & ".join(conditions)
        arr = [head, conditions_string]
        return " <-- ".join(arr)

    def print_atoms(self):
        for atom in self.atoms:
            print (atom)

# Prints an error. Identical to print(). For debugging purposes
def printError(string):
    print(string)

# returns True if, and only if, string s is a valid variable name
def is_atom(s):
    def is_letter(s):
        return len(s) == 1 and s.lower() in "_abcdefghijklmnopqrstuvwxyz"
    if not isinstance(s, str):
        return False
    if s == "":
        return False
    return is_letter(s[0]) and all(is_letter(c) or c.isdigit() for c in s[1:])

def interpret_file(kbString):
    kb_dict = {}
    kb = kbString.split("\n")
    
    # Interpret each line of the file
    for line in kb:
        # Do nothing if line is a blank line
        if line.strip():
            head = ""
            conditions = []     #b_1 ... b_n
            
            # Check if the line has "<--"
            tokens = line.split("<--")

            # Line should only have 1 "<--", which splits the line into 2
            if len(tokens) < 2:
                printError("Error: \"<--\" symbol not found in line: '" + line + "'")
                return 
            if len(tokens) > 2:
                printError("Error: too many \"<--\" symbols found in line: '" + line + "'")
                return
            
            # retrieve the head
            head = tokens[0].strip()

            # Check the variable name for head
            if not is_atom(head):
                printError("Error: the head does not have an appropriate variable name in line: '" + line + "'")
                return
            
            # Retrieve b1 ... bn
            conditions = tokens[1].split("&")

            # Make sure there is at least 1 condition
            if not conditions:
                printError("Error: not enough conditionals in line: '" + line + "'")
                return

            # Remove whitespaces from atoms and check each variable name
            for i in range(len(conditions)):
                atom = conditions[i]
                atom = atom.strip()
                if not is_atom(atom):
                    printError("Error: this atom does not have an appropriate variable name: '"
                    + atom + "' in line: '" + line + "'")
                    return
                conditions[i] = atom

            kb_dict[head] = conditions   

    # Check if the file was empty
    if not kb_dict:
        printError("Error: Knowledge base file is empty")
        return
    return kb_dict

def load(filename):
    try:
        kbFile = open(filename)
    except:
        printError ("Error: file '" + filename + "' not found")
        return

    kb_dict = interpret_file(kbFile.read())
    kbFile.close()

    return kb_dict
    
def tell(tokens_line):
    tokens = tokens_line.strip()
    tokens = tokens.split(" ")

    if len(tokens) == 1 and not tokens[0]:
        printError("Error: no atoms detected")
        return
    
    for token in tokens:
        token = token.strip()
        if not is_atom(token):
            printError("Error: '" + token + "' is not an appropriate variable name")
            return
        
    return tokens

def infer_all(kb):
    # Checks if all conditions of a rule is satisfied
    def is_rule_satisfied(atoms, conditions):
        for condition in conditions:
            if condition not in atoms:
                return False
        
        return True
    
    # Find all the satisfied heads from a set of rules
    def satisfied_heads(rules, atoms, new_atoms):
        all_atoms = atoms + new_atoms
        satisfied = []
        for head in rules:
            if head in all_atoms:
                continue
            if is_rule_satisfied(all_atoms, rules[head]):
                satisfied.append(head)

        return satisfied
    
    rules = kb.rules
    atoms = kb.atoms

    if not kb.rules:
        printError("Error: knowledge base must have at least one rule")
        return

    if not kb.atoms:
        printError("Error: knowledge base must have at least one atom")
        return
    
    new_atoms = []

    while (True):
        heads = satisfied_heads(rules, atoms, new_atoms)

        if not heads:
            break

        new_atoms += heads

    return new_atoms
             

def main():
    kb = KB()
    while True:

        # Quit interpreter command
        print()
        text = input("kb> ")
        text = text.strip()
        print()
        if text in [":q", ":Q", "quit", "end"]:
            break

        # Load command
        if text[:4] == "load":
            new_kb = load(text[5:])                  # Accounts for "load" + " "

            if new_kb:
                kb.load_kb(new_kb)

        # Tell command
        elif text[:4] == "tell":
            atoms = tell(text[4:])
            if atoms:
                for atom in atoms:
                    kb.add_atom(atom)

        # Print kb
        elif text[:5] == "print":
            print(kb)

        # Clear all data from kb
        elif text[:9] == "clear_all":
            kb.clear_all()

        # Clear all data from kb
        elif text[:11] == "clear_atoms":
            kb.clear_atoms()
        
        # Infer All command
        elif text[:9] == "infer_all":
            inferred_atoms = infer_all(kb)

            if inferred_atoms:
                print ("Newly inferred atoms:")
                print ("     " + str(inferred_atoms))
                print ("Atoms already known to be true:")
                print ("     " + str(kb.atoms))
                print()

                for atom in inferred_atoms:
                    kb.add_atom(atom)
            else:
                print ("No atoms inferred")

        else:
            printError("Error: unknown command \"" + text + "\"")

if __name__ == '__main__':
    main()