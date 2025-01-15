from flamapy.metamodels.fm_metamodel.transformations import UVLReader

from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import (
    PySATSatisfiable,
    PySATConfigurationsNumber,
    PySATConfigurations,
    PySATCoreFeatures,
    PySATDeadFeatures,
    PySATSatisfiableConfiguration
)
from flamapy.metamodels.bdd_metamodel.transformations import FmToBDD, PNGWriter
from flamapy.metamodels.bdd_metamodel.operations import (
    BDDConfigurationsNumber,
    BDDSampling,
    BDDCoreFeatures,
    BDDDeadFeatures,
    BDDProductDistribution,
    BDDFeatureInclusionProbability
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

    # Obtain the children of a given feature
    children = fm.root.get_children()
    print(f'Children of the root feature {fm.root.name}: {[f.name for f in children]}')
    feature = fm.get_feature_by_name('Topping')  # Obtain a feature from its name
    children = feature.get_children()
    print(f'Children of the feature {feature}: {[f.name for f in children]}')

    # Obtain the parent of a feature (NOTE: the root feature has not parent)
    parent = feature.get_parent()
    print(f'Parent of {feature}: {parent}')
    print(f'Parent of the root feature {fm.root}: {fm.root.get_parent()}')

    # Obtain all relations of a feature
    feature = fm.get_feature_by_name('Pizza')  # Obtain a feature from its name
    print(f'Relations of {feature}:')
    for i, relation in enumerate(feature.get_relations(), 1):
        print(f' |-Relation {i}: {relation} -> parent: {relation.parent.name}, children: {[f.name for f in relation.children]}, card_min: {relation.card_min}, card_max: {relation.card_max}')

    # Obtain specific information for a relation
    feature = fm.get_feature_by_name('Topping')  # Obtain a feature from its name
    print(f'Relations of {feature}:')
    for i, relation in enumerate(feature.get_relations(), 1):
        print(f' |-Relation {i}: {relation} -> parent: {relation.parent.name}, children: {[f.name for f in relation.children]}, card_min: {relation.card_min}, card_max: {relation.card_max}')
        if relation.is_mandatory():  # [1..1] and only one children
            relation_type = 'MANDATORY'
        elif relation.is_optional():  # [0..1] and only one children
            relation_type = 'OPTIONAL'
        if relation.is_or():  # [1..n] and two or more children
            relation_type = 'OR'
        elif relation.is_alternative():  # [1..1] and two or more children
            relation_type = 'XOR'
        elif relation.is_mutex():  # [0..1] and two or more children
            relation_type = 'MUX'
        elif relation.is_cardinal():  # [a..b] and two or more children
            relation_type = 'CARDINAL'
        print(f' |-Relation type: {relation_type}')
        print(f' |-Is group?: {relation.is_group()}')


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

    ###############################################################################################
    # Working with SAT
    ###############################################################################################

    # Transform the feature model to propositional logic (SAT model)
    sat_model = FmToPysat(fm).transform()

    # Check if the model is valid
    valid = PySATSatisfiable().execute(sat_model).get_result()
    print(f'Valid?: {valid}')

    # Number of products (configurations)
    n_configurations = PySATConfigurationsNumber().execute(sat_model).get_result()
    print(f'#Configurations: {n_configurations}')

    # List all products (configurations)
    configurations = PySATConfigurations().execute(sat_model).get_result()
    for i, config in enumerate(configurations, 1):
        print(f'{i}: {config}')

    # Obtain the core features (those features that are present in all configurations)
    core_features = PySATCoreFeatures().execute(sat_model).get_result()
    print(f'Core features: {core_features}')

    # Obtain the dead features (those features that are not present in any configuration)
    dead_features = PySATDeadFeatures().execute(sat_model).get_result()
    print(f'Dead features: {dead_features}')

    ###############################################################################################
    # Work with configurations
    ###############################################################################################

    # Create a valid configuration, but an invalid product because there is no any Size selected ('Normal' nor 'Big')
    elements = ['Pizza', 'Topping', 'Mozzarella', 'Dough', 'Sicilian', 'Size']  
    features = {e: True for e in elements}
    my_config = Configuration(features)
    print(f'My configuration: {[f for f in my_config.get_selected_elements()]}')

    # Check if the configuration is valid
    valid_config_operation = PySATSatisfiableConfiguration()
    valid_config_operation.set_configuration(my_config)
    valid_config = valid_config_operation.execute(sat_model).get_result()
    print(f'Valid config?: {valid_config}')

    # Check if the configuration is a valid product (that is, if the configuration is completed)
    valid_product_operation = PySATSatisfiableConfiguration()
    my_config.set_full(True)  # Mark the configuration as completed
    valid_product_operation.set_configuration(my_config)
    valid_product = valid_product_operation.execute(sat_model).get_result()
    print(f'Valid product?: {valid_product}')


    ###############################################################################################
    # Working with BDD
    ###############################################################################################

     # Create the BDD from the FM
    bdd_model = FmToBDD(fm).transform()

    # # Save the BDD as a .png
    PNGWriter(bdd_model.root.var + '.png', bdd_model).transform()

    # BDD number of products
    nof_products = BDDConfigurationsNumber().execute(bdd_model).get_result()
    print(f'#Products: {nof_products}')

   # BDD Sampling
    sampling_op = BDDSampling()
    sampling_op.set_sample_size(5)
    sampling_op.set_with_replacement(False)
    sample = sampling_op.execute(bdd_model).get_result()
    print('Uniform Random Sampling:')
    for i, prod in enumerate(sample):
        print(f'Product {i}: {[feat for feat in prod.elements if prod.elements[feat]]}')

    # BDD product distribution
    dist = BDDProductDistribution().execute(bdd_model).get_result()
    print(f'Product Distribution: {dist}')

    assert sum(dist) == nof_products

    # BDD feature inclusion probabilities
    prob = BDDFeatureInclusionProbability().execute(bdd_model).get_result()
    print('Feature Inclusion Probabilities:')
    for feat in prob.keys():
        print(f'{feat}: {prob[feat]}')


if __name__ == '__main__':
    test_main()