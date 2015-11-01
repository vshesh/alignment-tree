#!/usr/bin/env python

import sys
from numpy import array
import itertools
from getopt import getopt
import fileinput

# data pertaining to the various kinds of operations. It's a double dictionary -
# each order has a dictionary of a tuple containing and order and 
operations = {
    2: {(0,1): 'N', (1,0): 'R'},
    4: {(1,3,0,2): '4one', (2,0,3,1): '4two'}, 
    5: {(1,3,0,4,2): '5one', 
        (1,4,2,0,3): '5two', 
        (2,0,4,1,3): '5three', 
        (2,4,0,3,1): '5four', 
        (3,0,2,4,1): '5five', 
        (3,1,4,0,2): '5six'
    },
    6: {(1, 3, 0, 5, 2, 4): '6n1', 
        (1, 3, 5, 0, 2, 4): '6n2', 
        (1, 3, 5, 0, 4, 2): '6n3', 
        (1, 3, 5, 2, 0, 4): '6n4', 
        (1, 4, 0, 2, 5, 3): '6n5', 
        (1, 4, 0, 3, 5, 2): '6n6', 
        (1, 4, 2, 0, 5, 3): '6n7', 
        (1, 4, 2, 5, 0, 3): '6n8', 
        (1, 5, 2, 4, 0, 3): '6n9', 
        (1, 5, 3, 0, 2, 4): '6n10', 
        (1, 5, 3, 0, 4, 2): '6n11', 
        (2, 0, 3, 5, 1, 4): '6n12', 
        (2, 0, 4, 1, 5, 3): '6n13', 
        (2, 0, 5, 3, 1, 4): '6n14', 
        (2, 4, 0, 3, 5, 1): '6n15', 
        (2, 4, 0, 5, 1, 3): '6n16', 
        (2, 4, 0, 5, 3, 1): '6n17', 
        (2, 4, 1, 5, 0, 3): '6n18', 
        (2, 5, 0, 3, 1, 4): '6n19', 
        (2, 5, 0, 4, 1, 3): '6n20', 
        (2, 5, 1, 3, 0, 4): '6n21', 
        (2, 5, 1, 4, 0, 3): '6n22', 
        (2, 5, 3, 0, 4, 1): '6n23', 
        (3, 0, 2, 5, 1, 4): '6n24', 
        (3, 0, 4, 1, 5, 2): '6n25', 
        (3, 0, 4, 2, 5, 1): '6n26', 
        (3, 0, 5, 1, 4, 2): '6n27', 
        (3, 0, 5, 2, 4, 1): '6n28', 
        (3, 1, 4, 0, 5, 2): '6n29', 
        (3, 1, 5, 0, 2, 4): '6n30', 
        (3, 1, 5, 0, 4, 2): '6n31', 
        (3, 1, 5, 2, 0, 4): '6n32', 
        (3, 5, 0, 2, 4, 1): '6n33', 
        (3, 5, 1, 4, 0, 2): '6n34', 
        (3, 5, 2, 0, 4, 1): '6n35', 
        (4, 0, 2, 5, 1, 3): '6n36', 
        (4, 0, 2, 5, 3, 1): '6n37', 
        (4, 0, 3, 1, 5, 2): '6n38', 
        (4, 1, 3, 0, 5, 2): '6n39', 
        (4, 1, 3, 5, 0, 2): '6n40', 
        (4, 1, 5, 2, 0, 3): '6n41', 
        (4, 1, 5, 3, 0, 2): '6n42', 
        (4, 2, 0, 3, 5, 1): '6n43', 
        (4, 2, 0, 5, 1, 3): '6n44', 
        (4, 2, 0, 5, 3, 1): '6n45',
        (4, 2, 5, 0, 3, 1): '6n46' 
    }
}

class Node:
    def __init__(self, start = 0, end = 0, order = "", children=[]):
        self.children = children
        self.order = order
        self.start = start
        self.end = end
    
    def __repr__(self):
        if (self.order == 'T'): return "T("+str(self.start)+")"
        else: return self.order+"("+str(self.start)+", "+str(self.end)+")"
    
    def __str__(self):
        if (self.order == 'T'): return str(self.start)
        else: return self.order+"("+str(self.start)+", "+str(self.end)+")"

def sanitize(alignments):
    prev1 = 0
    prev2 = 0
    order = []
    words = []
    
    #deal with vanishing words by copying the mapping of the last word, 
    # e.g. [0-0 2-1] becomes [0-0 1-0 2-1]
    for x in alignments:
        split = x.split("-")
        first = int(split[0])
        second = int(split[1])
        
        i = prev1+1
        while i < first: #vanishing words
            order.append(Node(prev2, prev2, "T"))
            words.append(prev2)
            i = i+1
        
        order.append(Node(second, second, "T"))
        words.append(second)
        prev1 = first
        prev2 = second
    
    #deal with materializing words by removing missing indices and repacking, 
    # and also deal with many-to-one mappings by duplicating the word
    # E.g. [0-0 1-2 2-3 3-3] => [0-0 1-1 2-2 3-2] => [0-0 1-1 2-2 3-3]
    
    #remove duplicates and sort
    words.sort()
    
    wmap = {}
    for i in range(0,len(words)):
        if i == 0 or words[i] != words[i-1]:
            wmap[words[i]] = i
    
    order2 = []
    for x in order:
        index = x.start
        order2.append(Node(wmap[index], wmap[index], "T"))
        wmap[index] = wmap[index]+1
    
    return order2

def mapfromarray(array):
    d = {}
    for i in array:
        if d.has_key(i[0]):
            d[i[0]].add(i[1])
        else:
            d[i[0]] = set([i[1]])

    d.update((k, frozenset(v)) for k, v in d.iteritems())
    return d

def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def sanitize2(alignments):
    # source to translation map
    forwardmap = mapfromarray(array([map(int, x.split('-')) for x in alignments]))
    #remove duplicate maps that are greater than length 1.     
    reducedmap = dict(unique_everseen(forwardmap.items(), lambda key: key[1]))
    keymap = dict(zip(reducedmap.keys(), range(len(reducedmap.keys())) ) )
    repackedmap = { keymap[key] : value for key, value in reducedmap.items() }
    newalignments = list(itertools.chain(
                         *map(lambda x: [str(x[0])+'-'+str(v) for v in x[1]], 
                              repackedmap.items())))
    return newalignments   


def binaryparse(order):
    #alignments = order.reverse()
    alignments = order[:]
    alignments.reverse()
    stack = []
    while(len(alignments) > 0):
        node = alignments.pop()
        if(len(stack) == 0):
            stack.append(node)
        else:
            top = stack.pop()
            if(top.end == node.start or top.end+1 == node.start):
                alignments.append(Node(top.start, node.end, "N", [top, node]))
            elif(top.start == node.end or top.start == node.end+1):
                alignments.append(Node(node.start, top.end, "R", [top, node]))
            else:
                stack.append(top)
                stack.append(node)
    return stack

def checkcontiguous(nodes):
    ''' takes a list of nodes (in any order) and makes sure
        that some permutation of the nodes is contiguous (ie, there
        are no breaks in the chain of numbers that they cover.) '''
    
    s = sorted(nodes, key=lambda node: node.start)
    for i in range(len(s)-1):
        if (s[i].end +1 != s[i+1].start):
            return False
    return True

def sortedorder(l, keyfunc=lambda x: x):
    s = sorted(l, key=keyfunc)
    d = dict([(s[i], i) for i in range(len(s))])
    return tuple([d[x] for x in l])

def parseOrderK(stack, order):
    global operations
    i = 0
    while i <= len(stack) - order:
        operands = stack[i:i+order]
        if (checkcontiguous(operands)):
            align = sortedorder(operands, lambda node: node.start)
            if align in operations[order]:
                stack = stack[:i] + \
                        [Node(operands[align.index(0)].start, 
                              operands[align.index(order-1)].end, 
                              operations[order][align], operands)] + \
                        stack[i+order:]
                i -= 1
        i += 1

    return stack

def preorder(tree):
    if(tree == None): return
    sys.stdout.write("{"+str(tree)+" ")
    for t in tree.children: preorder(t)
    sys.stdout.write("}")

def printtree(stack):
    if(len(stack) == 1):
        sys.stdout.write("V:")
        preorder(stack.pop())
    else:
        sys.stdout.write("N:")
        for tree in stack:
            preorder(tree)
            sys.stdout.write('| ')
    print ''

def lisppreorder(tree):
    if (tree == None): return
    if tree.order == 'T': return str(tree.start)
    return '(:'+tree.order + '^' + str(tree.start) + '-' + str(tree.end) + ' ' + ' '.join(lisppreorder(child) for child in tree.children) + ')'

def lisptree(stack):
    s = ''
    if len(stack) == 1:
        s += lisppreorder(stack.pop())
    else:
        s += '['
        for tree in stack:
            s += lisppreorder(tree) + ' '
        s += ']'
    return s

def jsonPreorder(tree):
    if (tree == None): return
    s = '{ "name":"' + str(tree)+'"'
    if len(tree.children) > 0: 
        s += ', "children": ['
        for t in tree.children: s += jsonPreorder(t) + ','
        s = s[:-1]+ ']'
    return s + '}'

def jsonTree(stack, alignment, linenum):
    json = '{ "line_number":'+str(linenum)+', "original_alignment":"'+ alignment + '", '
    if (len(stack) == 1):
        json += '"success": "yes", '
        json += '"parse_tree":' + jsonPreorder(stack[0]) + ' '
    else:
        json += '"success": "no", '
        json += '"parse_tree": [' 
        for t in stack: json += jsonPreorder(stack[0]) + ', ' 
        json = json[:-2]+']'
    json += '}'
    return json

if __name__ == '__main__':

    opts, args = getopt(sys.argv[1:], 'jl', ['--json', '--lisp'])
    outformat = 'lisp'
    for o,a in opts:
        if o == '-j' or o == '--json':
            outformat = 'json'
        elif o == '-l' or l == '--lisp':
            outformat = 'lisp'


    if outformat is 'json': print '['
    count= 1
    for line in fileinput.input(args):
        if(line.strip() == ""):
            break
        order = sanitize(sanitize2(line.split()))
        
        prevresult = []
        result = binaryparse(order)

        while len(result) > 1 and prevresult != result:
            prevresult = result[:]
            result = binaryparse(parseOrderK(parseOrderK(
                                 parseOrderK(result, 4),5),6))

        if outformat == 'json':
            print jsonTree(result, line.strip(), count) + ','
        elif outformat == 'lisp':
            print lisptree(result)
        else:
            printtree(result)
        count +=1 

    if outformat is 'json': print ']'
    





