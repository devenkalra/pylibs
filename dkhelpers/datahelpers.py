import collections
import inspect
from unittest import TestCase
from copy import deepcopy

class HelperFuncs:
    @classmethod
    def is_int(cls, s):
        if isinstance(s, str):
            try:
                int(s)
                return True
            except ValueError:
                return False

    @classmethod
    def get_deep_lookup(cls, obj, path, default=None):
        try:
            val = eval("obj%s" % path)
            if val is not None:
                return val
        except Exception:
            return default


class DataCompare:

    @classmethod
    def sort_any(cls, a1):
        '''
        Sort keys of all dicts
        :param a1:
        :return:
        '''
        type_a1 = type(a1)
        if a1 is None: return a1

        if (type_a1 in (str, int, float, bool,)):
            return a1

        if (type_a1 in (list, tuple)):
            sorted_list = []
            for item in a1:
                sorted_list.append(DataCompare.sort_any(item))
            hashed_list = {}
            for item in sorted_list:
                if type(item) == collections.OrderedDict:
                    item_hash = hash(tuple(item.keys()))
                else:
                    item_hash = hash(item)
                while item_hash in hashed_list:
                    item_hash = item_hash + 1
                hashed_list[item_hash] = item
            sorted_dict = collections.OrderedDict(sorted(hashed_list.items()))
            sorted_list = []
            for key in sorted_dict:
                sorted_list.append(sorted_dict[key])
            return sorted_list

        if type_a1 == collections.OrderedDict:
            return a1

        if type_a1 is dict:
            sorted_a1 = collections.OrderedDict(sorted(a1.items()))
            for key, item in sorted_a1.items():
                sorted_a1[key] = DataCompare.sort_any(item)
            return sorted_a1

    @classmethod
    def compare_entities(cls, field_map, expected, actual):
        print("matching")
        for field in field_map:
            if field not in expected: continue
            expected_value = expected[field]
            actual_value = actual[field]
            type = field_map[field]["type"]
            if field == "tags":
                tags = expected_value.split(",")
                for tag in tags:
                    tag = tag.strip()
                    found = False
                    for actual_tag in actual_value:
                        if actual_tag["tag"] == tag:
                            found = True
                            break
                    if not found:
                        return False
            elif type in ["input", "checkbox", "detailnote"]:
                if expected_value != actual_value:
                    return False
            elif type == "dropdown":
                matching_key = DataDbFuncs.get_index(field_map[field]["values"], lambda x: x["label"] == expected_value)
                if actual_value != field_map[field]["values"][matching_key]["value"]:
                    return False
            elif type == "date":
                if actual_value != expected_value["value"]:
                    return False

        return True

    @classmethod
    def compare_any(cls, a1, a2, exclude_list=["entity_id", "id", "idpath", "strpath"], include_list=[],
                    ignore_missing_keys=False, where_am_i="", debug_depth=1):
        type_a1 = type(a1)
        type_a2 = type(a2)
        if (type_a1 != type_a2):
            if debug_depth > 0:
                print("Object Mismatch (%s):\n%s (%s != %s)" % (str(type_a1), where_am_i, str(a1), str(a2),))
            return (False, (a1, a2))

        if (a1 is None and a2 is None): return (True,)

        if (type_a1 in (str, int, float, bool,)):
            if a1 == a2:
                return (True, None)
            else:
                if debug_depth > 0:
                    print("Object Mismatch (%s):\n%s (%s != %s)" % (str(type_a1), where_am_i, str(a1), str(a2),))
                return (False, (a1, a2))

        if (type_a1 in (list, tuple)):
            comp = cls.compare_iterable(a1, a2, exclude_list, include_list, ignore_missing_keys, where_am_i, debug_depth = debug_depth-1)
            if not comp[0]:
                if debug_depth > 0:
                    print("Object Mismatch (%s):\n%s (%s != %s)" % (str(type_a1), where_am_i, str(a1), str(a2),))
                return (False, comp[1])
            else:
                return (True, None)

        if (type_a1 is dict or type_a1 == collections.OrderedDict):
            comp = cls.compare_dicts(a1, a2, exclude_list=exclude_list, include_list=include_list,
                                     ignore_missing_keys=ignore_missing_keys, where_am_i=where_am_i, debug_depth = debug_depth-1)

            if not comp[0]:
                if debug_depth > 0:
                    print("Object Mismatch (%s):\n%s (%s != %s)" % (str(type_a1), where_am_i, str(a1), str(a2),))
                return (False, comp[1])
            else:
                return (True, None)

        comp = cls.compare_objects(a1, a2, exclude_list=exclude_list,
                                   include_list=include_list,
                                   ignore_missing_keys=ignore_missing_keys,
                                   where_am_i=where_am_i, debug_depth = debug_depth-1)
        if not comp[0]:
            if debug_depth > 0:
                print("Object Mismatch (%s):\n%s (%s != %s)" % (str(type_a1), where_am_i, str(a1), str(a2),))
            return (False, comp[1])
        else:
            return (True, None)

    @classmethod
    def compare_iterable(cls, i1, i2, exclude_list=[], include_list=[], ignore_missing_keys=False, where_am_i="", debug_depth=1):
        # order independent comparison

        if (len(i1) != len(i2)): return (False, (i1, i2))
        i = 0
        compared_already = []
        for i in range(len(i1)):
            for j in range(len(i1)):
                if (j in compared_already): continue
                comp = cls.compare_any(i1[i], i2[j], exclude_list=exclude_list, include_list=include_list,
                                       ignore_missing_keys=ignore_missing_keys, where_am_i=where_am_i,
                                       debug_depth=debug_depth-1)
                if (comp[0]):
                    compared_already.append(j)
                    break
            # if (not comp[0]):
            #     with Capturing() as output:
            #         print("No match for: %s" % str(i1[i]))
            #         print("Comparisons:")
            #         for s in i2:
            #            print(str(s))
            #    raise Exception(output)
            # if not comp[0]:
            #     return (False, (i1, i2))
        if (len(compared_already) < len(i2)): return (False, (i1, i2))
        return (True, None)

    @classmethod
    def compare_objects(cls, o1, o2, exclude_list=["entity_id", "id", "idpath", "strpath"], include_list=[],
                        ignore_missing_keys=False, where_am_i="", debug_depth=1):
        fields_1 = list(o1.__dict__.keys())
        fields_2 = list(o2.__dict__.keys())

        if (len(include_list) > 0):
            for field in include_list:
                comp = (field in fields_1 and field in fields_2)
                if not comp: continue
                comp = (field in fields_1 and field not in fields_2) or (field not in fields_1 and field in fields_2)
                if comp:
                    print("Missing Key:\n%s (%s)" % (where_am_i, field,))
                    return (False, (o1, o2))
                val1 = getattr(o1, field)
                val2 = getattr(o2, field)
                comp = cls.compare_any(cls, val1, val2, exclude_list, include_list, ignore_missing_keys,
                                       where_am_i="%s:%s" % (where_am_i, field), debug_depth=debug_depth-1)
                if not comp[0]:
                    return (False, comp[1])
            return (True, None)

        for field in fields_1:
            if (not field in fields_2): return (False, (o1, o2))
            comp_value = cls.compare_any(getattr(o1, field), getattr(o2, field), exclude_list, include_list,
                                         ignore_missing_keys, where_am_i="%s:%s" % (where_am_i, field))
            if (not comp_value[0]): return (False, comp_value[1])

        for field in fields_2:
            if (not field in fields_1): return (False, (o1, o2))
            comp_value = cls.compare_any(getattr(o1, field), getattr(o2, field), exclude_list, include_list,
                                         ignore_missing_keys, where_am_i="%s:%s" % (where_am_i, field))
            if (not comp_value[0]): return (False, comp[1])
        return (True, None)

    @classmethod
    def compare_dicts(cls, d1, d2, exclude_list=["entity_id", "id", "idpath", "strpath"],
                      include_list=[],
                      ignore_missing_keys=False, where_am_i="", debug_depth=1):
        ## need to put checks for array and objects

        keys1 = d1.keys()
        keys2 = d2.keys()

        if len(include_list) > 0:

            for key in include_list:
                if (ignore_missing_keys and key not in keys1 and key not in keys2): continue
                if (key in keys1 and key not in keys2) or (key in keys2 and key not in keys1):
                    print("Missing Key:\n%s (%s)" % (where_am_i, key,))
                    return (False, (d1, d2))

                val1 = d1[key]
                val2 = d2[key]
                comp = cls.compare_any(val1, val2, exclude_list=exclude_list, include_list=include_list,
                                       ignore_missing_keys=ignore_missing_keys,
                                       where_am_i="%s:%s" % (where_am_i, key), debug_depth = debug_depth-1)
                if not comp[0]:
                    return (False, comp[1])
            return (True, None)

        for key in keys1:
            if (key in exclude_list): continue;
            if (key not in keys2): return (False, (d1, d2))
            #    raise Exception("Key: %s missing in dict 2\n%s\n\n%s" % (key, d1.__str__(), d2.__str__()))
        for key in keys2:
            if (key in exclude_list): continue;
            if (key in exclude_list): continue;
            if key not in keys1: return (False, (d1, d2))
            #   raise Exception("Key: %s missing in dict 1" % key)

        for key in keys1:
            if (key in exclude_list): continue
            if key not in keys2: raise Exception("Key: %s missing" % key)
            val1 = d1[key]
            val2 = d2[key]
            comp = cls.compare_any(val1, val2, exclude_list=exclude_list, include_list=include_list,
                                   ignore_missing_keys=ignore_missing_keys,
                                   where_am_i="%s:%s" % (where_am_i, key), debug_depth = debug_depth-1)
            if (not comp[0]): return (False, comp[1])

        return (True, None)


class DataDbFuncs:
    '''A set of  DB like functions to process collection of objects'''

    @classmethod
    def sort_dict_keys(cls, d1):
        return collections.OrderedDict(sorted(d1.items()))

    @classmethod
    def delete_fields(cls, iterable_or_dict, fields, filter):
        '''
        Delete fields from dict or list of dicts if it matches filter
        :param iterable_or_dict:
        :param fields: a dictionary that provides the field names as keys and values to be updated in the dict or each
            dict in iterable
        :filter func(x) returns True ro False
        :return:
        '''
        if isinstance(iterable_or_dict, dict):
            if filter(dict):
                dict = iterable_or_dict
                for field in fields:
                    del dict[field]
        else:  # iterable
            for dict in iterable_or_dict:
                if not filter(dict): continue
                for field in fields:
                    del dict[field]

        return iterable_or_dict

    @classmethod
    def get_index(cls, iterable, filter):
        '''
        Return index of matching item. None if there is none or duplicate
        :param iterable:
        :param filter:
        :return:
        '''
        index = -1
        found = None
        found_index = index
        for item in iterable:
            index += 1
            if filter(item):
                if found is not None: return None  # duplicate
                found_index = index
                found = item
        return found_index

    @classmethod
    def get(cls, iterable, filter):
        '''
        Return matching element
        :param iterable:
        :param filter:
        :return:
        '''
        if isinstance(iterable, dict):
            found = None
            for key, item in iterable.items():
                if filter(item):
                    if (found != None): return None  # duplicate
                    found = item
            return found

        found = None
        for item in iterable:
            if filter(item):
                if (found != None): return None  # duplicate
                found = item
        return found

    @classmethod
    def extract_field(cls, iterable, extract_func):
        '''
        extract data from array of records and return as an array
        :param iterable: array of elements
        :param filter: function to extract data
        :return: array of extracted data
        '''
        coll = []
        for item in iterable:
            coll.append(extract_func(item))
        return coll

    @classmethod
    def filtered_value(cls, iterable, field, func=lambda x: True):
        '''
        return matching items from iterable
        :param iterable:
        :param field:
        :param func:
        :return:
        '''
        coll = DataDbFuncs.filter(iterable, func)

        def extract_func(x):
            return x[field]

        return cls.extract_field(coll, extract_func)

    @classmethod
    def sort(cls, iterable, fields):
        '''
        Sort iterable (array of dicts) by fields dict
        :param iterable: Example iterable = [{"first":"Deven", "last":"Kalra"}...]
        :param fields: ["last", "first"]
        :return: No return, sorted iterable
        '''
        for field in fields:
            iterable.sort(key=field)

    @classmethod
    def filter(cls, iterable, func, returnKey=False):
        '''
        extract matching elements if iterable is an array, or matching fields if dict
        :param iterable:
        :param func:
        :return:
        '''
        if isinstance(iterable, dict):
            found = []
            for key, item in iterable.items():
                if func(item):
                    if (item):
                        if returnKey:
                            found.append([key, item])
                        else:
                            found.append(item)

            return found

        found = []
        for item in iterable:
            if func(item):
                if (item): found.append(item)
        return found

    @classmethod
    def update_item(cls, item, value, **key_value):
        for key in value:
            item[key] = value[key]
        return item

    @classmethod
    def update(cls, iterable, value, func=lambda x: True):
        coll = DataDbFuncs.filter(iterable, func)
        for c in coll:
            DataDbFuncs.update_item(c, value)
        return coll

    @classmethod
    def delete(cls, iterable, func, key_field=None):
        coll = DataDbFuncs.filter(iterable, func)
        if isinstance(iterable, dict):
            for c in coll:
                del (iterable[c[key_field]])
            return

        for c in coll:
            iterable.remove(c)

    @classmethod
    def save(cls, iterable, item, key_field=None):
        if isinstance(iterable, dict):
            iterable[key_field] = item
            return item

        iterable.append(item)
        return item

    @classmethod
    def get_value_if_exists(cls, iterable, key, default=None):
        if isinstance(iterable, dict):
            if key in iterable:
                return iterable[key]
        elif key in iterable:
            return key
        return default


class TreeFuncs:
    MULTIPLE_NODES_FOUND = {"code": -1, "message": "Multiple Nodes Found"}
    NO_NODE_FOUND = {"code": -2, "message": "No Nodes Found"}

    def __init__(self, children_name="children", text_name="text", id_name="id", parent_id_name="parent_id"):
        self.children_name = children_name
        self.text_name = text_name
        self.id_name = id_name
        self.parent_id_name = parent_id_name


    @classmethod
    def find_path(cls, nodes, text):
        def _find_path(tree, text, path=""):
            paths = []
            for node in nodes:
                if node[self.text_name] == text:
                    new_path = "%s/%s" % (path, text,)
                    if self.children_name in node:
                        return _find_path(node[self.children_name], text, )
                    paths.append["%s/%s" % (path, text,)]
            return paths

        return _find_path(tree, text, "", path_field)

    def get_leaves(self, root):
        leaves = []

        def find_leaves(nodes, leaves):
            for node in nodes:
                if self.children_name not in node or len(node[self.children_name]) == 0:
                    leaves.append(node)
                else:
                    find_leaves(node[self.children_name], leaves)

        find_leaves(root, leaves)
        return leaves

    def compare_trees(self, t1, t2, exclude_list=[], include_list=[], ignore_missing_keys=False):
        DataCompare.compare_any(t1, t2, exclude_list=exclude_list, include_list=include_list,
                                ignore_missing_keys=ignore_missing_keys)

    @classmethod
    def split_path(cls, path):
        parts = path.split("/")
        if parts[-1] == "":
            parts = parts[1:-1]
        else:
            parts = parts[1:]
        return parts

    def get_by_path(self, tree, path):
        parts = path.split("/")
        if parts[-1] == "":
            parts = parts[1:-1]
        else:
            parts = parts[1:]
        root_nodes = tree
        node = None
        index = 0
        for part in parts:
            node = DataDbFuncs.get(root_nodes, lambda x: x[self.text_name] == part)
            index += 1
            if index == len(parts): return node
            if self.children_name in node and len(node[self.children_name]) > 0:
                root_nodes = node[self.children_name]
            else:
                raise TreeFuncsException(TreeFuncs.NO_NODE_FOUND)

    def filter(self, tree, filter_func):
        coll = []

        def _filter(nodes: iter):
            for node in nodes:
                if filter_func(node):
                    coll.append(node)
                if self.children_name in node and len(node[self.children_name]) > 0:
                    _filter(node[self.children_name])

        _filter(tree)
        return coll

    def filter_with_path(self, tree, filter_func):
        coll = {}

        def _filter(nodes: iter, path=""):
            for node in nodes:
                if filter_func(node):
                    coll["%s/%s"%(path, node[self.text_name],)] = node
                if self.children_name in node and len(node[self.children_name]) > 0:
                    _filter(node[self.children_name], "%s/%s"%(path, node[self.text_name]))

        _filter(tree)
        return coll

    def update(self, tree, update_func, filter_func=lambda x: True):
        coll = self.filter(tree, filter_func)
        for c in coll:
            update_func(c)
        return coll

    def delete_fields(self, tree, fields, filter_func=lambda x: True):
        '''
        Delete fields from matching nodes
        :param tree:
        :param fields:
        :param filter:
        :return:
        '''
        coll = self.filter(tree, filter_func)
        for dict in coll:
            for field in fields:
                try:
                    if field[0] == "[":
                        exec("del dict%s" % field)
                    else:
                        exec("del dict['%s']" % field)
                except Exception as e:
                    pass

    def delete(self, tree, filter_func):
        '''
        delete matching nodes
        :param tree:
        :param filter_func:
        :return:
        '''

        def _delete(nodes):
            count = 0
            to_delete = []
            for node in nodes:
                if filter_func(node):
                    to_delete.append(count)
                count += 1
            for c in to_delete:
                del (nodes[c])
            for node in nodes:
                if self.children_name in node and len(node[self.children_name]) > 0:
                    _delete(node[self.children_name])

        _delete(tree)

    def get(self, tree, filter_func):
        '''
        Search
        :param tree:
        :param filter: function to match a node
        :return: matching nodes
        '''
        found = []

        def _get(root_nodes):
            for node in root_nodes:
                if filter_func(node):
                    found.append(node)
                if self.children_name in node and len(node[self.children_name]) > 0:
                    _get(node["children"])

        _get(tree)
        if len(found) > 1:
            raise (TreeFuncsException(TreeFuncs.MULTIPLE_NODES_FOUND))
        if len(found) == 0:
            raise (TreeFuncsException(TreeFuncs.NO_NODE_FOUND))

        return found[0]

    def create_tree_from_nodes(self, in_nodes, key_field="id", parent_field="parent_id"):
        '''
        Create a tree from an array of nodes. Each node should have a key and a parent field that
        encodes the parent child relationship
        '''
        nodes = [
            {"id": 1, "text": "L1"},
            {"id": 2, "text": "L2"},
            {"id": 3, "text": "L3"},
            {"id": 4, "text": "L11", "parent_id": 1},
            {"id": 5, "text": "L12", "parent_id": 1},
            {"id": 6, "text": "L111", "parent_id": 4},
            {"id": 7, "text": "L21", "parent_id": 2},
        ]

        def add_children(node, nodes):
            child_nodes = DataDbFuncs.filter(nodes, lambda x: x[self.parent_id_name] == node[self.id_name])
            if len(child_nodes):
                node[self.children_name] = deepcopy(child_nodes)
                for child_node in node[self.children_name]:
                    del child_node[self.parent_id_name]
                    add_children(child_node, nodes)

        nodes = deepcopy(in_nodes)
        # top level
        top_nodes = DataDbFuncs.filter(nodes, lambda x: self.parent_id_name not in x or x[self.parent_id_name] == 0)

        tree = deepcopy(top_nodes)
        DataDbFuncs.delete(nodes, lambda x: self.parent_id_name not in x or x[self.parent_id_name] == 0)

        for node in tree:
            if self.parent_id_name in node:
                del node[self.parent_id_name]
            add_children(node, nodes)
        return tree


class TestDataCompare(TestCase):
    def test_sort(self):
        x = 2
        self.assertEqual("a", DataCompare.sort_any("a"))
        x = [3, 2]
        sorted_x = DataCompare.sort_any(x)
        self.assertEqual([2, 3], sorted_x)
        x = {"first": "Deven", "last": "Kalra", "dob": "2002"}
        sorted_x = DataCompare.sort_any(x)
        self.assertEqual(["dob", "first", "last"], list(sorted_x.keys()))

        x = [
            {'id': '-2', 'text': 'Favorite', 'children': []},
            {'id': '-1', 'text': 'All', 'children': [
                {'id': '4940', 'text': 'Location', 'children': [
                    {'id': '4941', 'text': 'US', 'children': [
                        {'id': '4942', 'text': 'California', 'children': []}
                    ]},
                    {'id': '4943', 'text': 'India', 'children': [
                        {'id': '4944', 'text': 'New Delhi', 'children': [
                            {'id': '4945', 'text': 'Hauz Khas', 'children': []}
                        ]},
                        {'id': '4946', 'text': 'Gujarat', 'children': [
                            {'id': '4947', 'text': 'Ahmedabad', 'children': []}]}]}]},
                {'id': '4948', 'text': 'Meetings', 'children': [
                    {'id': '4949', 'text': 'Drs', 'children': [
                        {'id': '4950', 'text': 'Dr Jha', 'children': []}]}]}]}
        ]
        sorted_x = DataCompare.sort_any(x)
        print("Hello")


class TestDBFuncs(TestCase):
    test_scalar_array_data = [
        1, 2, "s1", "s2", True, False
    ]
    test_dict_array_data = [
        {"first": "Jan", "last": "Blake", "gender": "F", "dob": 1962},
        {"first": "Jacob", "last": "Underwood", "gender": "M", "dob": 1958},
        {"first": "Carol", "last": "Rutherford", "gender": "F", "dob": 2001}
    ]
    test_keyed_dict_data = {
        1: {"id": 1, "first": "Jan", "last": "Blake", "gender": "F", "dob": 1962},
        2: {"id": 2, "first": "Jacob", "last": "Underwood", "gender": "M", "dob": 1958},
        3: {"id": 3, "first": "Carol", "last": "Rutherford", "gender": "F", "dob": 2001}
    }

    test_tree_dict_data = {

    }

    def test_keyed_dict(self):
        test_keyed_dict_data = deepcopy(self.test_keyed_dict_data)
        test_dict_array_data = self.test_dict_array_data
        item = DataDbFuncs.get(test_keyed_dict_data, lambda x: x["first"] == "Jan")
        self.assertEqual("Blake", item["last"])
        item = DataDbFuncs.get(test_keyed_dict_data, lambda x: x["gender"] == "X")
        self.assertEqual(None, item)

        self.assertEqual("Jan", DataDbFuncs.get(test_keyed_dict_data, lambda x: x["first"] == "Jan")["first"])
        self.assertEqual("Jacob",
                         DataDbFuncs.get(test_keyed_dict_data, lambda x: x["last"] == "Underwood")["first"])
        items = DataDbFuncs.filter(test_keyed_dict_data, lambda x: x["gender"] == "F")
        self.assertEqual("Jan", items[0]["first"])
        self.assertEqual("Carol", items[1]["first"])
        items = DataDbFuncs.update(test_keyed_dict_data, {"foo": 'blah'}, lambda x: x["gender"] == "F")
        self.assertEqual({"first": 'Jan', "foo": "blah"}, {"first": items[0]["first"], "foo": items[0]["foo"]})
        self.assertEqual({"first": 'Carol', "foo": "blah"}, {"first": items[1]["first"], "foo": items[1]["foo"]})
        DataDbFuncs.delete(test_keyed_dict_data, lambda x: x["first"] == "Jan", "id")
        self.assertEqual(None, DataDbFuncs.get(test_keyed_dict_data, lambda x: x["first"] == "Jan"))
        DataDbFuncs.save(test_dict_array_data, {"first": "Deven", "last": "Kalra", "gender": "M"}, "id")
        self.assertEqual("Deven", DataDbFuncs.get(test_dict_array_data, lambda x: x["first"] == "Deven")["first"])

    def test_scalar(self):
        self.assertEqual(2, DataDbFuncs.get(self.test_scalar_array_data, lambda x: x == 2))
        self.assertEqual("s1", DataDbFuncs.get(self.test_scalar_array_data, lambda x: x == "s1"))
        self.assertEqual(True, DataDbFuncs.get(self.test_scalar_array_data,
                                               lambda x: isinstance(x, type(True)) and x == True))
        self.assertEqual([2], DataDbFuncs.filter(self.test_scalar_array_data, lambda x: x == 2))
        self.assertEqual(["s1"], DataDbFuncs.filter(self.test_scalar_array_data, lambda x: x == "s1"))
        self.assertEqual([True], DataDbFuncs.filter(self.test_scalar_array_data,
                                                    lambda x: isinstance(x, type(True)) and x == True))
        self.assertEqual("s1", DataDbFuncs.get(self.test_scalar_array_data, lambda x: x == "s1"))
        DataDbFuncs.delete(self.test_scalar_array_data, lambda x: x == "s1")
        self.assertEqual(None, DataDbFuncs.get(self.test_scalar_array_data, lambda x: x == "s1"))
        DataDbFuncs.save(self.test_scalar_array_data, "s3")
        self.assertEqual("s3", DataDbFuncs.get(self.test_scalar_array_data, lambda x: x == "s3"))

    def test_dict_array(self):
        item = DataDbFuncs.get(self.test_dict_array_data, lambda x: x["first"] == "Jan")
        self.assertEqual("Blake", item["last"])
        item = DataDbFuncs.get(self.test_dict_array_data, lambda x: x["gender"] == "X")
        self.assertEqual(None, item)

        self.assertEqual("Jan", DataDbFuncs.get(self.test_dict_array_data, lambda x: x["first"] == "Jan")["first"])
        self.assertEqual("Jacob",
                         DataDbFuncs.get(self.test_dict_array_data, lambda x: x["last"] == "Underwood")["first"])
        items = DataDbFuncs.filter(self.test_dict_array_data, lambda x: x["gender"] == "F")
        self.assertEqual("Jan", items[0]["first"])
        self.assertEqual("Carol", items[1]["first"])
        #items = DataDbFuncs.update(self.test_dict_array_data, {"foo": 'blah'}, lambda x: x["gender"] == "F")
        #self.assertEqual({"first": 'Jan', "foo": "blah"}, {"first": items[0]["first"], "foo": items[0]["foo"]})
        #self.assertEqual({"first": 'Carol', "foo": "blah"}, {"first": items[1]["first"], "foo": items[1]["foo"]})
        #DataDbFuncs.delete(self.test_dict_array_data, lambda x: x["first"] == "Jan")
        #self.assertEqual(None, DataDbFuncs.get(self.test_dict_array_data, lambda x: x["first"] == "Jan"))
        #DataDbFuncs.save(self.test_dict_array_data, {"first": "Deven", "last": "Kalra", "gender": "M"})
        #self.assertEqual("Deven", DataDbFuncs.get(self.test_dict_array_data, lambda x: x["first"] == "Deven")["first"])


class TreeFuncsException(Exception):
    def __init__(self, data):
        self.code = data["code"]
        self.message = data["message"]


class TestTreeFuncs(TestCase):
    testData = {
        "default": [
            {"text": "L1", "name": "L1_Name",
             "name": "L1_name",
             "children": [
                 {"text": "L11", "name": "L11_Name"},
                 {"text": "L12", "name": "L12_Name"},
                 {"text": "L13", "name": "L13_Name"}
             ]
             }, {"text": "L2", "name": "L2_Name",
                 "children": [
                     {"text": "L21", "children":
                         [{"text": "L211", "name": "L211_Name"},
                          {"text": "L212", "name": "L212_Name"}]},
                     {"text": "L22", "name": "L22_Name"}
                 ]
                 }, {"text": "L3", "name": "L3_Name"}]
    }

    def test_create(self):
        tf = TreeFuncs()
        nodes = [
            {"id": 1, "text": "L1"},
            {"id": 2, "text": "L2"},
            {"id": 3, "text": "L3"},
            {"id": 4, "text": "L11", "parent_id": 1},
            {"id": 5, "text": "L12", "parent_id": 1},
            {"id": 6, "text": "L111", "parent_id": 4},
            {"id": 7, "text": "L21", "parent_id": 2},
        ]
        test_tree = [
            {"id": 1, "text": "L1",
             "children": [
                 {"id": 4, "text": "L11",
                  "children": [{"id": 6, "text": "L111"}]},
                 {"id": 5, "text": "L12"}
             ]},
            {"id": 2, "text": "L2",
             "children": [{"id": 7, "text": "L21"}]},
            {"id": 3, "text": "L3"}
        ]

        tree = tf.create_tree_from_nodes(nodes)
        self.assertNotEqual(0, len(tree))

        try:
            tf.compare_trees(tree, test_tree, include_list=["id", "text"])
        except Exception as e:
            self.assertTrue(False, str(e))

    def test_delete(self):
        tf = TreeFuncs()

        tree = deepcopy(TestTreeFuncs.testData["default"])
        self.assertEqual(1, len(tf.filter(tree, lambda x: x["text"] == "L2")))
        tf.delete(tree, lambda x: x["text"] == "L2")
        self.assertEqual(0, len(tf.filter(tree, lambda x: x["text"].startswith("L2"))))

        tree = deepcopy(TestTreeFuncs.testData["default"])
        self.assertEqual(5, len(tf.filter(tree, lambda x: x["text"].startswith("L2"))))
        tf.delete(tree, lambda x: x["text"] == "L2")
        self.assertEqual(0, len(tf.filter(tree, lambda x: x["text"].startswith("L2"))))

        tree = deepcopy(TestTreeFuncs.testData["default"])
        self.assertEqual(1, len(tf.filter(tree, lambda x: x["text"].startswith("L3"))))
        tf.delete(tree, lambda x: x["text"] == "L3")
        self.assertEqual(0, len(tf.filter(tree, lambda x: x["text"].startswith("L3"))))

    def test_update(self):
        def update_state(x):
            x["updated"] = "abc"

        tf = TreeFuncs()
        tree = deepcopy(TestTreeFuncs.testData["default"])

        coll = tf.update(tree, update_state, lambda x: x["text"].startswith("L2"))
        self.assertEqual(5, len(coll))

        coll = tf.filter(tree, lambda x:"updated" in x and x["updated"] == "abc")
        self.assertEqual(5, len(coll))

    def test_filter(self):
        tf = TreeFuncs()
        coll = tf.filter(TestTreeFuncs.testData["default"], lambda x: x["text"] == "L2")
        self.assertEqual("L2_Name", coll[0]["name"])

        coll = tf.filter(TestTreeFuncs.testData["default"], lambda x: x["text"].startswith("L2"))
        self.assertEqual(5, len(coll))

        coll = tf.filter(TestTreeFuncs.testData["default"], lambda x: x["text"].startswith("L3"))
        self.assertEqual(1, len(coll))

    def test_filter_with_path(self):
        tf = TreeFuncs()
        coll = tf.filter_with_path(TestTreeFuncs.testData["default"], lambda x: x["text"] == "L2")
        self.assertEqual("L2_Name", list(coll.values())[0]["name"])
        self.assertEqual("/L2", list(coll.keys())[0])

        coll = tf.filter_with_path(TestTreeFuncs.testData["default"], lambda x: x["text"].startswith("L2"))
        self.assertEqual(5, len(coll))
        paths = list(coll.keys())
        for path in paths:
            parts = path.split("/")
            leaf = parts[len(parts)-1]
            self.assertTrue(leaf.startswith("L2"))

        for node in list(coll.values()):
            self.assertTrue(node["text"].startswith("L2"))

    def test_get_by_path(self):
        tf = TreeFuncs()
        self.assertEqual("L11_Name", tf.get_by_path(TestTreeFuncs.testData["default"], "/L1/L11/")["name"])
        self.assertEqual("L3_Name", tf.get_by_path(TestTreeFuncs.testData["default"], "/L3/")["name"])
        self.assertEqual("L212_Name", tf.get_by_path(TestTreeFuncs.testData["default"], "/L2/L21/L212/")["name"])

    def test_get(self):
        tf = TreeFuncs()
        leaves = tf.get_leaves(TestTreeFuncs.testData["default"])
        self.assertEqual(7, len(leaves))

        node = tf.get(TestTreeFuncs.testData["default"],
                      lambda x: x["text"] == "L1")

        self.assertEqual("L1", node["text"])

        node = tf.get(TestTreeFuncs.testData["default"],
                      lambda x: x["text"] == "L21")

        self.assertEqual("L21", node["text"])

        self.assertRaises(TreeFuncsException, tf.get, TestTreeFuncs.testData["default"],
                          lambda x: x["text"] == "LX")
        self.assertRaises(TreeFuncsException, tf.get, TestTreeFuncs.testData["default"],
                          lambda x: x["text"].startswith(""))


#x = TestTreeFuncs()
#x.test_filter_with_path()