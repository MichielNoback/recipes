import utils
from utils import FlavorMolecule
from utils import DataStore
from utils import Ingredient
import configparser
import pandas as pd
import panel as pn
pn.extension()



def read_all_data(config: configparser.ConfigParser) -> DataStore:
    flavor_molecules = utils.read_flavor_molecules(config['FILES']['molecules'])
    ingredients = utils.read_ingredients(config['FILES']['flavors'])
    return DataStore(flavor_molecules, ingredients)

def read_config(config_file: str) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def create_ingredients_search_widget():
    search = pn.widgets.AutocompleteInput(name = "Search Ingredients", 
                                          options = list(datastore.ingredients['alias']),
                                          case_sensitive=False,
                                          placeholder='Start typing an ingredient name',
                                          search_strategy='includes').servable(target='sidebar')
    return search

def create_ingredient_details_panel(selected_ingredient):
    ingredient = datastore.ingredients[datastore.ingredients['alias'] == selected_ingredient]
    print(ingredient)
    #print(ingredient.iloc[0, 1])

    ingredient_flavor_molecules = ingredient['molecules'].iloc[0]
    flavor_molecules = list()
    for i, id in enumerate(ingredient_flavor_molecules):
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

    ## fetch markdown content
    md = utils.create_ingredient_markdown(ingredient_inst)
    return pn.pane.Markdown(md)


def build_gui():
    app = pn.template.BootstrapTemplate(title='Ingredient Browser')

    ## widgets
    ingredients_search = create_ingredients_search_widget()

    ## ingredient details pane
    ingredient_details_pane = create_ingredient_details_panel('japanese pumpkin')

    ## higher order layout elements
    filter_column = pn.Column(ingredients_search)
    app.sidebar.append(filter_column)

    ## the tabs pane
    main_tabs = pn.Tabs(('Ingredient Info', ingredient_details_pane), ('Ingredient Network', "FOO"))
    app.main.append(main_tabs)
    ## displays the app in a browser tab
    app.show()


def main():
    global datastore
    config = read_config("config.ini")
    datastore = read_all_data(config)
    #print(datastore)

    build_gui()

if __name__ == '__main__':
    main()