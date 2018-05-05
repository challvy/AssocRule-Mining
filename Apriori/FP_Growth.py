import csv
import time


def load_dataset(csv_file_name):
    csv_file = open(csv_file_name, "r", encoding="utf8")
    reader = csv.reader(csv_file)
    dataset = []
    for line in reader:
        if reader.line_num == 1:
            continue
        transaction = line[1].lstrip("{").rstrip("}").split(",")
        dataset.append(transaction)
    csv_file.close()
    return dataset


def load_UNIX_dataset(csv_file_name):
    csv_file = open(csv_file_name, "r", encoding="utf8")
    reader = csv.reader(csv_file)
    dataset = []
    flag = True
    for line in reader:
        if len(line) == 0:
            continue
        elif len(line) == 1 and line[0] == '\n':
            continue
        elif line[0] == '**SOF**' or line[0] == '' or line[0][0] == '<':
            continue
        elif line[0] == '**EOF**':
            flag = True
            continue

        if flag == False:
            dataset[-1] += line
        else:
            dataset.append(line)
            flag = False
    csv_file.close()
    tran_num = float(len(dataset))
    data_list = {}
    for elem in dataset:
        if frozenset(elem) in data_list:
            data_list[frozenset(elem)] += 1
        else:
            data_list[frozenset(elem)] = 1
    return data_list, tran_num


class TreeNode:
    def __init__(self, name, count, parent):
        self.name = name
        self.count = count
        self.parent = parent
        self.children = {}
        self.next = None

    def inc(self, inc):
        self.count += inc


def update_head_tab(head_node, targetNode):
    while(head_node.next is not None):
        head_node = head_node.next
    head_node.next = targetNode
    return


def update_FPTree(FPTree, ordered_freq_items, head_tab, count):
    if ordered_freq_items[0] in FPTree.children:
        FPTree.children[ordered_freq_items[0]].inc(count)
    else:
        FPTree.children[ordered_freq_items[0]] = TreeNode(ordered_freq_items[0], count, FPTree)
        if head_tab[ordered_freq_items[0]][1] is None:
            head_tab[ordered_freq_items[0]][1] = FPTree.children[ordered_freq_items[0]]
        else:
            update_head_tab(head_tab[ordered_freq_items[0]][1], FPTree.children[ordered_freq_items[0]])
    if(len(ordered_freq_items) > 1):
        update_FPTree(FPTree.children[ordered_freq_items[0]], ordered_freq_items[1::], head_tab, count)
    return


def gen_FPTree(dataset, min_sup, tran_num):
    head_tab = {}
    for items in dataset:
        for item in items:
            head_tab[item] = head_tab.get(item, 0) + dataset[items]
    head_tab = {k:v for k,v in head_tab.items() if v/tran_num >= min_sup}
    freq_items = set(head_tab.keys())
    if freq_items is None:
        return None, None
    for head_tab_item in head_tab:
        head_tab[head_tab_item] = [head_tab[head_tab_item], None]
    FPTree = TreeNode("null", 1, None)
    for items, count in dataset.items():
        freq_items_rec = {}
        for item in items:
            if item in freq_items:
                freq_items_rec[item] = head_tab[item][0]
        if len(freq_items_rec) > 0:
            ordered_freq_items = [v[0] for v in sorted(freq_items_rec.items(), key=lambda v:v[1], reverse = True)]
            update_FPTree(FPTree, ordered_freq_items, head_tab, count)
    return FPTree, head_tab


def ascend_tree(treeNode):
    prefixs = []
    while((treeNode.parent != None) and (treeNode.parent.name != 'null')):
        treeNode = treeNode.parent
        prefixs.append(treeNode.name)
    return prefixs


def get_prefix_path(head_tab, head_item):
    prefix_path = {}
    begin_node = head_tab[head_item][1]
    prefixs = ascend_tree(begin_node)
    if prefixs != []:
        prefix_path[frozenset(prefixs)] = begin_node.count
    while(begin_node.next != None):
        begin_node = begin_node.next
        prefixs = ascend_tree(begin_node)
        if (prefixs != []):
            prefix_path[frozenset(prefixs)] = begin_node.count
    return prefix_path


def mine_FPTree(head_tab, prefix, freq_pats, min_sup, len_dat):
    head_tab_items = [v[0] for v in sorted(head_tab.items(), key=lambda v:v[1][0])]
    if head_tab_items is None:
        return
    for head_tab_item in head_tab_items:
        tmp_prefix = prefix.copy()
        tmp_prefix.add(head_tab_item)
        freq_pats[frozenset(tmp_prefix)] = head_tab[head_tab_item][0]
        prefix_path = get_prefix_path(head_tab, head_tab_item)
        if prefix_path != {}:
            cond_FPTree, cond_head_tab = gen_FPTree(prefix_path, min_sup, len_dat)
            if cond_head_tab is not None:
                mine_FPTree(cond_head_tab, tmp_prefix, freq_pats, min_sup, len_dat)
    return


def removeStr(set, str):
    tempSet = []
    for elem in set:
        if(elem != str):
            tempSet.append(elem)
    tempFrozenSet = frozenset(tempSet)
    return tempFrozenSet


def get_rules(frequentset, currentset, rules, frequentPatterns, minConf):
    for frequentElem in currentset:
        subSet = removeStr(currentset, frequentElem)
        confidence = frequentPatterns[frequentset] / frequentPatterns[subSet]
        if (confidence >= minConf):
            flag = False
            for rule in rules:
                if(rule[0] == subSet and rule[1] == frequentset - subSet):
                    flag = True
            if(flag == False):
                rules.append((subSet, frequentset - subSet, confidence))
            if(len(subSet) >= 2):
                get_rules(frequentset, subSet, rules, frequentPatterns, minConf)
    return


def gen_assoc_rules(freq_pat, min_conf, rules):
    for frequentset in freq_pat:
        if(len(frequentset) > 1):
            get_rules(frequentset, frequentset, rules, freq_pat, min_conf)
    return


def itemsets_to_string(set):
    aim = "{"
    for i in set:
        aim += i + ","
    aim = aim[:-1] + "}"
    return aim


if __name__=='__main__':
    min_sup = 0.150
    min_conf = 0.950
    #dataset, tran_num = load_dataset('Groceries.csv')
    dataset, tran_num = load_UNIX_dataset('UNIX_usage/USER0/sanitized_all.981115184025')
    freq_pats = {}
    prefix = set([])
    timelist = []
    start = time.clock()
    FPTree, head_tab = gen_FPTree(dataset, min_sup, tran_num)
    mine_FPTree(head_tab, prefix, freq_pats, min_sup, tran_num)
    elapsed = (time.clock() - start)
    timelist.append(float(elapsed))
    rules = []
    gen_assoc_rules(freq_pats, min_conf, rules)
    print("#"*100 + "\n" + "Frequent patterns".center(70) + "Num\n")
    for item in freq_pats:
        if(len(item)>2):
            print(itemsets_to_string(item).center(70) + str(freq_pats[item]))

    print("\n" + "#"*100 + "\n" + "Association rules".center(70) + " Confidence value" + "\n")
    for item in rules:
        print((itemsets_to_string(item[0]) + "  =>  " + itemsets_to_string(item[1])).center(70) + str(item[2]))
    print("\n" + "#"*100)

