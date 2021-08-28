import dict_deep
import mergedeep

def deep_build(source, dict_map, sep='.'):
    target = dict()

    for ka, kb in dict_map.items():
        value = dict_deep.deep_get(source, kb or ka, sep=sep)
        dict_deep.deep_set(target, ka, value, sep=sep) if value else None

    return target

def deep_set(*pargs, **kwargs):
    return dict_deep.deep_set(*pargs, **kwargs)

def deep_get(*pargs, **kwargs):
    return dict_deep.deep_get(*pargs, **kwargs)

def deep_merge(*pargs, **kwargs):
    return mergedeep.merge(*pargs, **kwargs)
