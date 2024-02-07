import pandas as pd
from typing import NamedTuple

class DataStore(NamedTuple):
    '''Data Store for all data used in the app'''
    flavor_molecules: pd.core.frame.DataFrame
    ingredients: pd.core.frame.DataFrame 

class FlavorMolecule(NamedTuple):
    '''models a flavor molecule'''
    pubchem_id: int
    common_name: str
    flavor_profile: list

class Ingredient(NamedTuple):
    '''models an ingredient'''
    ingredient_id: int
    alias: str
    synonyms: list
    scientific_name: str
    category: str
    flavor_molecules: list


def parse_list_col(x: str) -> list[str]:
    x = x.replace('{', '[').replace('}', ']')
    return eval(x)

def read_flavor_molecules(molecules_file: str) -> pd.core.frame.DataFrame: 
    molecules = pd.read_csv(molecules_file, 
                            #index_col='pubchem id',
                            usecols = ['pubchem id', 'common name', 'flavor profile'])
    #convert molecules string ("{'sweet', 'creamy', 'caramel', 'lactonic', 'brown'}") to list
    molecules['flavor profile'] = molecules['flavor profile'].apply(parse_list_col)
    return molecules

def read_ingredients(ingredients_data_file: str) -> pd.core.frame.DataFrame:
    ingredients = pd.read_csv(ingredients_data_file, 
                              #index_col='entity id', 
                              usecols=['entity id', 'alias', 'synonyms', 'scientific name', 'category', 'molecules'])
    #convert the two list-like columns to list "{27457, 7976, 31252, 26808, 22201, 26331}"
    ingredients['synonyms'] = ingredients['synonyms'].apply(parse_list_col)
    ingredients['molecules'] = ingredients['molecules'].apply(parse_list_col)
    return ingredients

def create_ingredient_markdown(selected_ingredient):
    ingredient_info = f"""
    ## Ingredient: {selected_ingredient.alias}  
    #### pubchem ID: {selected_ingredient.ingredient_id}  
    #### synonyms: {selected_ingredient.synonyms}  
    #### scientific name: {selected_ingredient.scientific_name}  
    #### category: {selected_ingredient.category}  
    ----  
    #### Flavor molecules
    """
    return ingredient_info

def get_ingredient(selected_ingredient: str, datastore: DataStore, with_flavor_molecules: bool = True) -> Ingredient:
    ingredient = datastore.ingredients[datastore.ingredients['alias'] == selected_ingredient]

    flavor_molecules = None
    if with_flavor_molecules:
        ingredient_flavor_molecules = ingredient['molecules'].iloc[0]
        flavor_molecules = list()
        for id in ingredient_flavor_molecules:
            # fetch flavor molecules
            fm = datastore.flavor_molecules[datastore.flavor_molecules['pubchem id'] == id]
            fm_inst = FlavorMolecule(id, fm.iloc[0, 1], fm.iloc[0, 2])
            flavor_molecules.append(fm_inst)

    ingredient_inst = Ingredient(ingredient.iloc[0, 0], 
                                 ingredient.iloc[0, 1], 
                                 ingredient.iloc[0, 2], 
                                 ingredient.iloc[0, 3], 
                                 ingredient.iloc[0, 4],
                                 flavor_molecules)
    return ingredient_inst
