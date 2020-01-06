from typing import List,Union
from snowshu.core.utils import key_for_value
from snowshu.core.models.materializations import Materialization
from snowshu.core.models.attribute import Attribute
import pandas as pd
import os
import re
from snowshu.logger import Logger
logger=Logger().logger

class Relation:

    data:pd.DataFrame
    compiled_query:str
    core_query:str
    population_size:int
    sample_size:int
    source_extracted:bool=False
    target_loaded:bool=False
    unsampled=False


    def __init__(self,
                    database:str,
                    schema:str,
                    name:str,
                    materialization:Materialization,
                    attributes:List[Attribute]):

        self.database=database
        self.schema=schema
        self.name=name
        self.materialization=materialization
        self.attributes=attributes
        

    def __repr__(self)->str:
        return f"<Relation object {self.database}.{self.schema}.{self.name}>"

    @property
    def dot_notation(self)->str:
        return f"{self.database}.{self.schema}.{self.name}"

    @property
    def quoted_dot_notation(self)->str:
        return f'"{self.database}"."{self.schema}"."{self.name}"'
    
    @property
    def star(self)->str:
        attr_string=str()
        for attr in self.attributes:
            attr_string+=f',{attr.name}\n'
        return attr_string[1:]

    ## Relation.relation is confusing compared to Relation.name, but in other objects the 
    ## <database>.<schema>.<relation> convention makes this convenient.
    @property
    def relation(self)->str:
        return self.name

    @relation.setter
    def relation(self,value:str)->None:
        self.name=value

    def typed_columns(self,data_type_mappings:dict)->str:
        """ generates the column section of a create statement in format <attr> <datatype>"""
        attr_string=str()
        for attr in self.attributes:
            attr_string+=f",{attr.name} {key_for_value(data_type_mappings, attr.data_type)}\n"
        return attr_string[1:]


    def lookup_attribute(self,attr:str)->Union[Attribute,None]:
        """finds the attribute by name or returns None"""
        return next((a for a in self.attributes if a.name == attr),None)




def lookup_relation(lookup:dict,relation_set:iter)->Relation:
    """ looks up a single relation by dict given the relation_set, returns None if not found.
        ARGS:
            lookup(dict) a dict of database, schema, relation keys
            relation_set(iter) any iterable of relations
    """
    logger.debug(f'looking for relation {lookup}...')
    found=next((rel for rel in relation_set if \
                                        rel.database==lookup['database'] \
                                    and rel.schema==lookup['schema'] \
                                    and rel.name==lookup['relation']),None)            

    logger.debug(f'found {found}.')
    return found

def single_full_pattern_match(rel:Relation,pattern:dict)->bool:
    """ determines if a relation matches a regex pattern dictionary of database,schema,name(relation)."""
    attributes=('database','schema','name',)
    return all([(lambda r,p : re.match(r,p)) (pattern[attr],rel.__dict__[attr],) for attr in attributes])

def at_least_one_full_pattern_match(rel:Relation,patterns:iter)->bool:
    """ determines if a relation matches any of a collection of pattern dictionaries (database,schema,name)."""
    return any([single_full_pattern_match(rel,pattern) for pattern in patterns])