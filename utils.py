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
    flavor_molecules = list()
    flavor_molecules.append('| PubChem ID | Name | Flavor profile |\n')
    flavor_molecules.append('| ---------- | ---- | -------------- |\n')
    for fm in selected_ingredient.flavor_molecules:
        flavor_molecules.append(f'| {fm.pubchem_id} | {fm.common_name} | {fm.flavor_profile} |\n') #
    fm_table = ''.join(flavor_molecules)
    #print(f'{fm_table}')
    ingredient_info = f"""
    # Ingredient: {selected_ingredient.alias}  
    ### pubchem ID: {selected_ingredient.ingredient_id}  
    ### synonyms: {selected_ingredient.synonyms}  
    ### scientific name: {selected_ingredient.scientific_name}  
    ### category: {selected_ingredient.category}  
    ----  
    ### Flavor molecules
    """
    ingredient_info = ingredient_info.replace('    ', '')
    ingredient_info += '\n'
    ingredient_info += fm_table
    print(ingredient_info)
    return ingredient_info
    #{''.join(flavor_molecules)}

    # | PubChem ID | Name | Flavor profile |
    # | ---------- | ---- | -------------- |
    # | hallo | moi | doei |