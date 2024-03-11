from flamapy.metamodels.fm_metamodel.transformations import UVLReader

from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import (
    Glucose3Valid,
    Glucose3ProductsNumber,
    Glucose3Products,
    Glucose3CoreFeatures,
    Glucose3DeadFeatures,
    Glucose3ValidProduct,
    Glucose3ValidConfiguration
)

from flamapy.metamodels.configuration_metamodel.models import Configuration


FM_PATH = 'models/Pizzas.uvl'


def test_main():
    ###############################################################################################
    # Load the feature model from UVL
    ###############################################################################################
    fm = UVLReader(FM_PATH).transform()

    ###############################################################################################
    # Work with the feature model
    ###############################################################################################

    # Obtain the list of all features
    features = fm.get_features()
    print(f'Features: {len(features)} {[f.name for f in features]}')

    # The root feature
    print(f'Root feature: {fm.root.name}')

    # Obtain the mandatory features
    mandatory_features = [f for f in features if f.is_mandatory()]
    print(f'Mandatory features: {len(mandatory_features)} {[f.name for f in mandatory_features]}')

    # Obtain the optional features
    optional_features = [f for f in features if f.is_optional()]
    print(f'Optional features: {len(optional_features)} {[f.name for f in optional_features]}')

    # Obtain the or-group features
    or_group_features = [f for f in features if f.is_or_group()]
    print(f'Or-group features: {len(or_group_features)} {[f.name for f in or_group_features]}')

    # Obtain the alternative (xor) group features
    xor_group_features = [f for f in features if f.is_alternative_group()]
    print(f'Xor-group features: {len(xor_group_features)} {[f.name for f in xor_group_features]}')

    # Obtain the leaf features (those features that have no children)
    leaf_features = [f for f in features if f.is_leaf()]
    print(f'Leaf features: {len(leaf_features)} {[f.name for f in leaf_features]}')

    # Obtain the internal features (those features that are no leaf)
    internal_features = [f for f in features if not f.is_leaf()]
    print(f'Internal features: {len(internal_features)} {[f.name for f in internal_features]}')

    # Obtain the list of all constraints
    constraints = fm.get_constraints()
    print(f'Constraints: {len(constraints)}')
    for i, ctc in enumerate(constraints, 1):
        print(f'{i}: {ctc.ast.pretty_str()}')
    
    ###############################################################################################
    # Analyze the feature model    
    ###############################################################################################

    # Transform the feature model to propositional logic (SAT model)
    sat_model = FmToPysat(fm).transform()

    # Check if the model is valid
    valid = Glucose3Valid().execute(sat_model).get_result()
    print(f'Valid?: {valid}')

    # Number of products (configurations)
    n_configurations = Glucose3ProductsNumber().execute(sat_model).get_result()
    print(f'#Configurations: {n_configurations}')

    # List all products (configurations)
    configurations = Glucose3Products().execute(sat_model).get_result()
    for i, config in enumerate(configurations, 1):
        print(f'{i}: {config}')

    # Obtain the core features (those features that are present in all configurations)
    core_features = Glucose3CoreFeatures().execute(sat_model).get_result()
    print(f'Core features: {core_features}')

    # Obtain the dead features (those features that are not present in any configuration)
    dead_features = Glucose3DeadFeatures().execute(sat_model).get_result()
    print(f'Dead features: {dead_features}')

    ###############################################################################################
    # Work with configurations
    ###############################################################################################

    # Create a valid configuration, but an invalid product because there is no any Size selected ('Normal' nor 'Big')
    elements = ['Pizza', 'Topping', 'Mozzarella', 'Dough', 'Sicilian', 'Size']  
    features = {fm.get_feature_by_name(e): True for e in elements}
    my_config = Configuration(features)
    print(f'My configuration: {[f.name for f in my_config.get_selected_elements()]}')

    # Check if the configuration is valid
    valid_config_operation = Glucose3ValidConfiguration()
    valid_config_operation.set_configuration(my_config)
    valid_config = valid_config_operation.execute(sat_model).get_result()
    print(f'Valid config?: {valid_config}')

    # Check if the configuration is a valid product (that is, if the configuration is completed)
    valid_product_operation = Glucose3ValidProduct()
    valid_product_operation.set_configuration(my_config)
    valid_product = valid_product_operation.execute(sat_model).get_result()
    print(f'Valid product?: {valid_product}')


if __name__ == '__main__':
    test_main()