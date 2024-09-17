from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.pysat_metamodel.models import PySATModel
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import PySATSatisfiableConfiguration
from flamapy.metamodels.pysat_diagnosis_metamodel.transformations import FmToDiagPysat
from flamapy.metamodels.pysat_diagnosis_metamodel.operations import PySATDiagnosis, PySATConflict


FM_PATH = 'models/Pizzas.uvl'


def get_all_parents(feature: Feature) -> list[str]:
    parent = feature.get_parent()
    return [] if parent is None  else [parent.name] + get_all_parents(parent)


def get_all_mandatory_children(feature: Feature) -> list[str]:
    children = []
    for child in feature.get_children():
        if child.is_mandatory():
            children.append(child.name)
            children.extend(get_all_mandatory_children(child))
    return children


def complete_configuration(configuration: Configuration, fm_model: FeatureModel) -> Configuration:
    """Given a partial configuration completes it by adding the parent's features and
    children's features that must be included because of the tree relationships of the 
    provided FM model."""
    configs_elements = dict(configuration.elements)
    for element in configuration.get_selected_elements():
        feature = fm_model.get_feature_by_name(element)
        if feature is None:
            raise Exception(f'Error: the element "{element}" is not present in the FM model.')
        children = {child: True for child in get_all_mandatory_children(feature)}
        parents = {parent: True for parent in get_all_parents(feature)}
        for parent in parents:
            parent_feature = fm_model.get_feature_by_name(parent)
            parent_children = get_all_mandatory_children(parent_feature)
            children.update({child: True for child in parent_children})
        configs_elements.update(children)
        configs_elements.update(parents)
    return Configuration(configs_elements)


def valid_config(configuration: list[str], fm_model: FeatureModel, sat_model: PySATModel) -> bool:
    """Given a list of features representing a configuration, checks whether the configuration
    is satisfiable (valid) according to the provided SAT model."""
    config = Configuration(elements={e: True for e in configuration})
    config = complete_configuration(config, fm_model)
    config.set_full(True)
    satisfiable_op = PySATSatisfiableConfiguration()
    satisfiable_op.set_configuration(config)
    return satisfiable_op.execute(sat_model).get_result()


if __name__ == '__main__':
    # You need the model in SAT
    fm_model = UVLReader(FM_PATH).transform()
    sat_model = FmToPysat(fm_model).transform()
    diagsat_model = FmToDiagPysat(fm_model).transform()

    # You need the configuration as a list of features
    elements = ['Pizza', 'Topping', 'Mozzarella', 'Dough', 'Sicilian', 'Size', 'Normal']

    # Call the valid operation
    valid = valid_config(elements, fm_model, sat_model)

    # Output the result
    print(f'Valid? {valid}')

    # Another example of a partial configuration
    elements = ['Mozzarella', 'Sicilian', 'Big']
    valid = valid_config(elements, fm_model, sat_model)
    print(f'Valid? {valid}')

    # Another example of a invalid configuration
    elements = ['Topping', 'Mozzarella', 'Dough', 'Sicilian', 'Size']
    valid = valid_config(elements, fm_model, sat_model)
    print(f'Valid? {valid}')

    ## Diagnosis
    config = Configuration(elements={e: True for e in elements})
    config = complete_configuration(config, fm_model)
    config.set_full(True) 
    satisfiable_op = PySATSatisfiableConfiguration()
    satisfiable_op.set_configuration(config)
    valid = satisfiable_op.execute(sat_model).get_result()
    print(f'Valid: {valid}')

    diag_op = PySATDiagnosis()
    diag_op.set_configuration(config)
    result = diag_op.execute(diagsat_model).get_result()
    print(f'Diagnosis: {result}')

    conflict_op = PySATConflict()
    conflict_op.set_configuration(config)
    result = conflict_op.execute(diagsat_model).get_result()
    print(f'Conflict: {result}')