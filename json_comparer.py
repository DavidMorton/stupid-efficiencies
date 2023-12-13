import json, math, copy

def compare_json(obj1, obj2, tolerance=1e-5, path=''):
    assert type(obj1) == type(obj2)
    if type(obj1) == dict:
        keys1 = list(sorted(obj1.keys()))
        keys2 = list(sorted(obj2.keys()))
        assert len(keys1) == len(keys2)
        for k1,k2 in zip(keys1, keys2):
            assert k1 == k2
            compare_json(obj1[k1], obj2[k2], tolerance=tolerance, path=path + f'[{k1}]')
    elif type(obj1) == list:
        assert len(obj1) == len(obj2), f'len({obj1}) != len({obj2}) at {path}'
        for i, (item1, item2) in enumerate(zip(obj1, obj2)):
            compare_json(item1, item2, tolerance=tolerance, path=path + f'[{i}]')
    elif type(obj1) == float:
        assert math.isclose(obj1, obj2, rel_tol=tolerance), f'{obj1} is not close to {obj2} at {path}'
    else:
        assert obj1 == obj2, f'{obj1} != {obj2} at {path}'

def compare_jsons(text1:str, text2:str):
    json1 = json.loads(text1)
    json2 = json.loads(text2)
    compare_json(json1, json2)

obj1 = {"One":1, "Two":[1,2,None,3], "Three":{"A":"a","B":"b"}}
obj2 = copy.deepcopy(obj1)
obj2["Three"]["A"] = 'b'

compare_json(obj1, obj2)