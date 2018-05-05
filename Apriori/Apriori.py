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
        if len(line)==0:
            continue
        elif len(line)==1 and line[0]=='\n':
            continue
        elif line[0] == '**SOF**' or line[0]=='' or line[0][0]=='<':
            continue
        elif line[0] =='**EOF**':
            flag = True
            continue

        if flag==False:
            dataset[-1] += line
        else:
            dataset.append(line)
            flag = False
    csv_file.close()
    return dataset


def is_freq(Ck_itemsets, Lksub1):
    for item in Ck_itemsets:
        Cksub1 = Ck_itemsets - frozenset([item])
        if Cksub1 not in Lksub1:
            return False
    return True


def gen_C1_itemsets(dataset):
    C1_itemsets = set()
    for dataset_item in dataset:
        for item in dataset_item:
            C1_item = frozenset([item])
            C1_itemsets.add(C1_item)
    return C1_itemsets


def gen_Ck_itemsets(Lksub1, k):
    Ck_itemsets = set()
    list_Lksub1 = list(Lksub1)
    len_Lksub1 = len(Lksub1)
    for i in range(len_Lksub1):
        for j in range(len_Lksub1):
            l1 = list(list_Lksub1[i])
            l1.sort()
            l2 = list(list_Lksub1[j])
            l2.sort()
            if l1[0:k-1] == l2[0:k-1]:
                Ck_item = list_Lksub1[i] | list_Lksub1[j]
                if is_freq(Ck_item, Lksub1):
                    Ck_itemsets.add(Ck_item)
    return Ck_itemsets


def gen_Lk(dataset, Ck, min_sup, sup_dict):
    Lk = set()
    count = {}
    for item in dataset:
        for Ck_item in Ck:
            if Ck_item.issubset(item):
                if Ck_item not in count:
                    count[Ck_item] = 1
                else:
                    count[Ck_item] += 1
    num_item = float(len(dataset))
    for count_item in count:
        if count[count_item]/num_item >= min_sup:
            Lk.add(count_item)
            sup_dict[count_item] = count[count_item]/num_item
    return Lk


def gen_all_freq_itemsets(dataset, k, min_sup):
    L = []
    sup_dict = {}
    C1_itemsets = gen_C1_itemsets(dataset)
    L1 = gen_Lk(dataset, C1_itemsets, min_sup, sup_dict)
    Lksub1 = L1.copy()
    L.append(Lksub1)
    for k_idx in range(1, k):
        Ci_itemsets = gen_Ck_itemsets(Lksub1, k_idx)
        Li = gen_Lk(dataset, Ci_itemsets, min_sup, sup_dict)
        Lksub1 = Li.copy()
        L.append(Lksub1)
    return L, sup_dict


def gen_assoc_rules(L, sup_dict, min_conf):
    assoc_rules = []
    list_sub_itemsets = []
    for i in range(len(L)):
        for freq_itemsets in L[i]:
            for sub_itemset in list_sub_itemsets:
                if sub_itemset.issubset(freq_itemsets):
                    conf = sup_dict[freq_itemsets] / sup_dict[freq_itemsets - sub_itemset]
                    assoc_rule = (freq_itemsets - sub_itemset, sub_itemset, conf)
                    if conf >= min_conf and assoc_rule not in assoc_rules:
                        assoc_rules.append(assoc_rule)
            list_sub_itemsets.append(freq_itemsets)
    return assoc_rules


def itemsets_to_string(set):
    aim = "{"
    for i in set:
        aim += i + ","
    aim = aim[:-1] + "}"
    return aim


def print_result(L,sup_dict,assoc_rules, k):
    for k_idx in range(k):
        print("#"*100 + "\n" + ("Frequent " + str(k_idx+1) + "-itemset").center(70) + "   Support value" + "\n")
        for freq_set in L[k_idx]:
            print(itemsets_to_string(freq_set).center(70) + str(sup_dict[freq_set]))
        print()
    print("#"*100 + "\n" + "Association rules".center(70) + " Confidence value" + "\n")
    for item in assoc_rules:
        print((itemsets_to_string(item[0]) + " => " + itemsets_to_string(item[1])).center(70) + str(item[2]))
    print("\n" + "#"*100)
    return


if __name__ == "__main__":
    k = 3
    min_sup = 0.150
    min_conf = 0.900
    #dataset = load_dataset('Groceries.csv')
    dataset = load_dataset('UNIX_usage/USER8/sanitized_all.981115184025')
    start = time.clock()
    L, sup_dict = gen_all_freq_itemsets(dataset, k, min_sup)
    elapsed = (time.clock() - start)
    print("Time used:", elapsed)
    assoc_rules = gen_assoc_rules(L, sup_dict, min_conf)
    print_result(L, sup_dict, assoc_rules, k)

