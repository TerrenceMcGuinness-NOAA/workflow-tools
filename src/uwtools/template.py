import re
import os
import copy
from collections import namedtuple
from collections.abc import Sequence

class Template:

    DOLLAR_CURLY_BRACE = '${}'
    DOLLAR_PARENTHESES = '$()'
    DOUBLE_CURLY_BRACES = '{{}}'

    ENV_regex = re.compile('\${.*?}+')
    SUB_regex = re.compile('\$\(.*?\)+')
    CYC_regex = re.compile('{{.*?}}+')

    var_name = namedtuple('var_name', ['regex', 'slice'])

    replacements = {
         DOLLAR_CURLY_BRACE: var_name(ENV_regex,slice(2,-1)),
         DOLLAR_PARENTHESES: var_name(SUB_regex,slice(2,-1)),
         DOUBLE_CURLY_BRACES: var_name(ENV_regex,slice(2,-2))  }

    @classmethod
    def replace_string(cls, var_to_sub, var_type: str, get_value):
        pair = cls.replacements[var_type]
        if isinstance(var_to_sub, str):
            variable_names = re.findall(pair.regex, var_to_sub)
            for variable in variable_names:
                var = variable[pair.slice]
                v = get_value(var)
                if v is not None:
                    if isinstance(v, Sequence) and not isinstance(v, str):   
                        if len(variable_names) == 1:
                            if var_to_sub.replace(variable_names[0][pair.slice], '') == var_type:
                                var_to_sub = v
                    else:
                        if isinstance(v, float) or isinstance(v, int):
                            v = str(v)
                        if isinstance(v, str):
                            var_to_sub = var_to_sub.replace(variable, v)
                        else:
                            var_to_sub = v
                else:
                    more = re.search(pair.regex, var)
                    if more is not None:
                        new_value = cls.replace_string(var, var_type, get_value)
                        var_to_sub = var_to_sub.replace(var, new_value)
        return var_to_sub

    @classmethod
    def replace_structure(cls, strcture_to_replace, var_type: str, get_value):
        if isinstance(strcture_to_replace, dict):
            for key, item in strcture_to_replace.items():
                strcture_to_replace[key] = cls.replace_structure(item, var_type, get_value)
        elif isinstance(strcture_to_replace, Sequence) and not isinstance(strcture_to_replace, str):
            for i, item in enumerate(strcture_to_replace):
                strcture_to_replace[i] = cls.replace_structure(item, var_type, get_value)
        else:
            strcture_to_replace = cls.replace_string(strcture_to_replace, var_type, get_value)
        return strcture_to_replace


    @classmethod
    def replace_from_environment(cls, strcture_to_replace):
        return cls.replace_structure(strcture_to_replace, cls.DOLLAR_CURLY_BRACE, os.environ.get)


    @classmethod
    def replace_with_dependencies(cls, dictionary, keys, shallow_precedence=True, excluded=()):
        var_type = cls.DOLLAR_PARENTHESES
        all_variables = cls.build_index(keys, excluded, shallow_precedence)
        previous = {}
        while dictionary != previous:
            previous = copy.deepcopy(dictionary)
            dictionary = cls.replace_structure(dictionary, var_type, all_variables.get)
        return dictionary

    @classmethod
    def build_index(cls, dictionary, excluded=None, shallow_precedence=True):
        def build(structure, variables):
            if isinstance(structure, dict):
                for k, i in structure.items():
                    if ((k not in variables) or (k in variables and not shallow_precedence)) and k not in excluded:
                        variables[k] = i
                        build(i, variables)
            elif isinstance(structure, Sequence) and not isinstance(structure, str):
                for v in structure:
                    build(v, variables)
        var = {}
        if excluded is None:
            excluded = set()
        build(dictionary, var)
        return var