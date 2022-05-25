import re
import os
import copy
from collections import namedtuple
from collections.abc import Sequence

class TemplateConstants:
    DOLLAR_CURLY_BRACE = '${}'
    DOLLAR_PARENTHESES = '$()'
    DOUBLE_CURLY_BRACES = '{{}}'

    SubPair = namedtuple('SubPair', ['regex', 'slice'])

class Template:

    substitutions = {
        TemplateConstants.DOLLAR_CURLY_BRACE: TemplateConstants.SubPair(re.compile('\${.*?}+'), slice(2, -1)),
        TemplateConstants.DOLLAR_PARENTHESES: TemplateConstants.SubPair(re.compile('\$\(.*?\)+'), slice(2, -1)),
        TemplateConstants.DOUBLE_CURLY_BRACES: TemplateConstants.SubPair(re.compile('{{.*?}}+'), slice(2, -2))
    }

    @classmethod
    def find_variables(cls, variable_to_substitute: str, var_type: str):
        pair = cls.substitutions[var_type]
        return [x[pair.slice] for x in re.findall(pair.regex, variable_to_substitute)]


    @classmethod
    def substitute_string(cls, variable_to_substitute, var_type: str, get_value):
        """
            Substitutes variables under the form var_type (e.g. DOLLAR_CURLY_BRACE), looks for a value returned
            by function get_value and if found, substitutes the variable. Convert floats and int to string
            before substitution.I f the value in the dictionary is a complex type, just assign it instead
            of substituting.
                get_value is a function that returns the value to substitute:
                signature: get_value(variable_name).
                If substituting from a dictionary my_dict,  pass my_dict.get
        """
        pair = cls.substitutions[var_type]
        if isinstance(variable_to_substitute, str):
            variable_names = re.findall(pair.regex, variable_to_substitute)
            for variable in variable_names:
                var = variable[pair.slice]
                v = get_value(var)
                if v is not None:
                    if isinstance(v, Sequence) and not isinstance(v, str):   
                        if len(variable_names) == 1:
                            # v could be a list or a dictionary (complex structure and not a string).
                            # If there is one variable that is the whole
                            # string, we can safely replace, otherwise do nothing.
                            if variable_to_substitute.replace(variable_names[0][pair.slice], '') == var_type:
                                variable_to_substitute = v
                    else:
                        if isinstance(v, float) or isinstance(v, int):
                            v = str(v)
                        if isinstance(v, str):
                            variable_to_substitute = variable_to_substitute.replace(variable, v)
                        else:
                            variable_to_substitute = v
                else:
                    more = re.search(pair.regex, var)
                    if more is not None:
                        new_value = cls.substitute_string(var, var_type, get_value)
                        variable_to_substitute = variable_to_substitute.replace(var, new_value)
        return variable_to_substitute

    @classmethod
    def substitute_structure(cls, structure_to_substitute, var_type: str, get_value):
        """
            Traverses a dictionary and substitutes variables in fields, lists
            and nested dictionaries.
        """
        if isinstance(structure_to_substitute, dict):
            for key, item in structure_to_substitute.items():
                structure_to_substitute[key] = cls.substitute_structure(item, var_type, get_value)
        elif isinstance(structure_to_substitute, Sequence) and not isinstance(structure_to_substitute, str):
            for i, item in enumerate(structure_to_substitute):
                structure_to_substitute[i] = cls.substitute_structure(item, var_type, get_value)
        else:
            structure_to_substitute = cls.substitute_string(structure_to_substitute, var_type, get_value)
        return structure_to_substitute


    @classmethod
    def substitute_structure_from_environment(cls, structure_to_substitute):
        return cls.substitute_structure(structure_to_substitute, TemplateConstants.DOLLAR_CURLY_BRACE, os.environ.get)


    @classmethod
    def substitute_with_dependencies(cls, dictionary, keys, var_type: str, shallow_precedence=True, excluded=()):
        """
            Given a dictionary with a complex (deep) structure, we want to substitute variables,
            using keys, another dictionary that may also have a deep structure (dictionary and keys
            can be the same dictionary if you want to substitute in place).
            We create an index based on keys (see build_index) and substitute values in dictionary
            using index. If variables may refer to other variables, more than one pass of substitution
            may be needed, so we substitute until there is no more change in dictionary (convergence).
        """
        all_variables = cls.build_index(keys, excluded, shallow_precedence)
        previous = {}
        while dictionary != previous:
            previous = copy.deepcopy(dictionary)
            dictionary = cls.substitute_structure(dictionary, var_type, all_variables.get)
        return dictionary

    @classmethod
    def build_index(cls, dictionary, excluded=None, shallow_precedence=True):
        """
            Builds an index of all keys with their values, going deep into the dictionary. The index
            if a flat structure (dictionary).
            If the same key name is present more than once in the structure, we want to
            either prioritise the values that are near the root of the tree (shallow_precedence=True)
            or values that are near the leaves (shallow_precedence=False). We don't anticipated use
            cases where the "nearest variable" should be used, but this could constitute a future
            improvement.
        """
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