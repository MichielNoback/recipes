#!/Users/michielnoback/opt/miniconda3/envs/education/bin/python

import utils
from utils import FlavorMolecule
from utils import DataStore
from utils import Ingredient
import configparser
import pandas as pd
import panel as pn
import param
from bokeh.models.widgets.tables import NumberFormatter
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
    if not selected_ingredient:
        return "NO INGREDIENT SELECTED"
    ingredient_inst = utils.get_ingredient(selected_ingredient, datastore)
    ## fetch markdown content
    md = utils.create_ingredient_markdown(ingredient_inst)
    return pn.pane.Markdown(md)

def create_flavor_molecules_table(selected_ingredient):
    if not selected_ingredient:
        return "NO INGREDIENT SELECTED"
    ingredient_inst = utils.get_ingredient(selected_ingredient, datastore)
    flavor_molecules = ingredient_inst.flavor_molecules
    fm_df = pd.DataFrame(flavor_molecules)
    table_editors = {'pubchem_id': None, 'common_name': None, 'flavor_profile': None}
    formatters = {'pubchem_id': NumberFormatter(format='0[.]0')}
    tabulator = pn.widgets.Tabulator(fm_df, height=250, editors = table_editors, formatters=formatters)
    tabulator.on_click(update_flavor_molecule_param)
    return tabulator

def update_flavor_molecule_param(event):
    #print(f'event: value={event.value}, column={event.column}, row={event.row}')
    if event.column == 'pubchem_id':
        global_reactive_values.flavor_molecule = event.value

def create_flavor_molecule_details():
    return pn.widgets.TextInput(name='Selected Flavor Molecule', value=str(644104))


def update_flavor_molecule_details(event):
    #print(f'param value: {global_reactive_values.flavor_molecule}, event: {event}')
    # accesses the global flavor_molecule_details widget
    flavor_molecule_details.value = str(global_reactive_values.flavor_molecule)

class GlobalReactiveValues(param.Parameterized):
    flavor_molecule = param.Number(default=644104) #CID 644104


def build_gui():
    app = pn.template.BootstrapTemplate(title='Ingredient Browser')

    ## ingredient_search is a widget and a reactive object.
    ingredients_search = create_ingredients_search_widget()
    
    ## TODO remove this default value
    ingredients_search.value = 'semolina'

    ## higher order layout elements
    filter_column = pn.Column(ingredients_search)
    app.sidebar.append(filter_column)
    
    ## ingredient details pane
    ingredient_details_panel = pn.bind(create_ingredient_details_panel, selected_ingredient=ingredients_search)
    ingredient_flavor_molecules_table = pn.bind(create_flavor_molecules_table, selected_ingredient=ingredients_search)

    global flavor_molecule_details
    flavor_molecule_details = create_flavor_molecule_details()
    
    global_reactive_values.param.watch(update_flavor_molecule_details, 'flavor_molecule')

    ingredient_details_col = pn.Column(ingredient_details_panel, 
                                       ingredient_flavor_molecules_table, 
                                       flavor_molecule_details)
    ## the tabs pane
    main_tabs = pn.Tabs(('Ingredient DF', ingredient_details_col), 
                        ('Ingredient Network', "FOO"))
    app.main.append(main_tabs)

    ## displays the app in a browser tab
    app.show()

# CLASS TO HOLD ALL REACTIVE VALUES
class GlobalReactiveValues(param.Parameterized):
    flavor_molecule = param.Number(default=644104)

def main():
    global datastore
    global global_reactive_values

    config = read_config("config.ini")
    datastore = read_all_data(config)
    global_reactive_values = GlobalReactiveValues()

    build_gui()

if __name__ == '__main__':
    main()