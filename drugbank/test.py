def extractDate(new_file_path):

    # filename = psplit(new_file_path)[1].strip().split('.xml.zip')[0].strip()
    # # gunzip file
    # filedir = new_file_path.split('.zip')[0].strip()

    # unzip = 'unzip {} -d {}'.format(new_file_path,drugbank_raw)

    # os.popen(unzip)

    # # raname
    # command = 'mv  {}/"full database.xml"  {}/full_database.xml'.format(drugbank_raw,drugbank_raw)

    # os.popen(command)
    #--------------------------------------------------------------------------------------------------------
    # parser tree
    tree = et.parse(open(pjoin(drugbank_raw,'full_database.xml')))

    root = tree.getroot()

    n = 0

    print len(root.getchildren())

    for child in root.getchildren()[:1]:
        parseDrug(child)



        # f = open(pjoin(drugbank_store,'tree_{}.txt'.format(n)),'w')
        
        # drug_dict = parseNode(child)
        
        # f.write(str(drug_dict))

        # f.close()

        # n += 1
def parseDrug(node):

    tree = dict()

    for child in node.getchildren():

        tag = child.tag.split('{http://www.drugbank.ca}')[1].strip()

        text = child.text

        if tag not in tree:

            tree[tag] = text

        else:
            tag_val = tree[tag]
            if not isinstance(tag_val,list):
                tree[tag] = [tag_val]
            tree[tag].append(text)


    with open('./test.json','w') as wf:
        json.dump(tree,wf,indent=2)
    print len(tree.keys())

def parseNode(node):

    tree = {}

    for child in node.getchildren():

        child_tag = child.tag .split('{http://www.drugbank.ca}')[1].strip()
        child_attr = child.attrib
        child_text = child.text.strip() if child.text is not None else ''  
        child_tree = parseNode(child)

        if not child_tree:
            child_dict = createDict(child_tag,child_text,child_attr)
        else:
            child_dict = createDict(child_tag,child_tree,child_attr)

        if child_tag not in tree:
            tree.update(child_dict)
            continue

        atag = '@' + child_tag
        atree = tree[child_tag]
   
        if not isinstance(atree,list):
            if not isinstance(atree,dict):
                atree = {}
            if atag  in tree:
                atree['#' + child_tag] = tree[atag]
                del tree[atag]

            tree[child_tag] = [atree]

        if child_attr:
            child_tree['#' +child_tag] = child_attr

        tree[child_tag].append(child_tree)

    return tree

def createDict(tag,value,attr=None):

    dic = {tag : value}

    if attr:

        atag = '@' + tag

        aattr = {}

        for key,val in attr.items():

            aattr[key] = val

        dic[atag] = aattr

        del atag
        del aattr

    return dic

def deblank(dic):

    print '1',len(dic)

    for key,val in dic.items():

        if not val:

            dic.pop(key)

        elif isinstance(val,dict) and len(val.keys()) ==1:

            val_key = val.keys()[0]

            val_val = val[val_key]
            dic.pop(key)

            dic.update({val_key:val_val})

        print '2',len(dic)

    return dic


extractDate('/home/user/project/molecular/mymol/dataraw/drugbank/drugbank_5-0-9_171102161331.xml.zip')

    # f = eval(open(os.path.join(drugbank_store,'tree_0.txt')).read())

    # dic = dict()

    # for key,val in f.items():

    #     dic[key] = val

    # with open(os.path.join(drugbank_store,'dic_0.json'),'w') as wf:
    #     json.dump(dic,wf,indent=2)