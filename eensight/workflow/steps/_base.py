# -*- coding: utf-8 -*-

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import abc

from typing import Any, Dict
from omegaconf.dictconfig import DictConfig

from eensight.io._data_catalog import DataCatalog 


class WorkflowStep(abc.ABC):
    """``WorkflowStep`` is the base class for all workflow step implementations.

    Parameters
    __________
    catalog: eensight.io.DataCatalog
        The data catalog of the program. The data catalog acts as a single point 
        of reference, relaying load and save functions to the underlying data sets.
    parameters: omegaconf.dictconfig.DictConfig
        A configuration dictionary that provides values to the parameters of the
        functions called by this step. 
    name: str (default=None)
        Meaningful name for this step, should be something that is distinguishable and 
        understandable for debugging, logging and any other similar purposes.
    requires: dict (default=None)
        A dictionary that associates a dataset that is required input for this steps's 
        `execute` method with a dataset name in the program's data catalog
    provides: dict (default=None)
        A dictionary that associates a dataset that is generated by this step with a 
        dataset name in the program's data catalog
    ml_stage : str (default=None)
        The type of the produced data: `train`, `val` or `test`.
    rebind: A dict of key/value pairs used to redefine column names for the datasets that 
        are inputs to this steps's ``execute`` method.
    run_id : str (default=None)
        The active MLflow run's ID that this step runs under. If it is None, no tracking will 
        take place. 
    tracking_uri : str (default=None)
        The address of the local or remote MLflow tracking server. It must be provided, if
        `run_id` is not None.
    experiment_name : str (default='Default')
        The name of the experiment.
    tags : dict (default=None) 
        Tags to be added to the active MLflow run.
    """

    default_requires = []
    default_provides = []

    
    def __init__(self, catalog          : DataCatalog, 
                       parameters       : DictConfig, 
                       name             : str=None,
                       requires         : Dict[str, str]=None, 
                       provides         : Dict[str, str]=None,
                       ml_stage         : str=None,
                       rebind           : Dict[str, str]=None,
                       run_id           : str = None,
                       tracking_uri     : str=None,
                       experiment_name  : str = None,
                       tags             : Dict[str, Any] = None):
        
        if not requires:
            requires = {val: val for val in self.default_requires} 
        if ml_stage:
            requires = {key: f'{val}_{ml_stage}' for key, val in requires.items()}

        if not provides:
            provides = {val: val for val in self.default_provides}
        if ml_stage:
            provides = {key: f'{val}_{ml_stage}' for key, val in provides.items()}
        
        rebind = rebind if rebind is not None else {}
        
        if (run_id is not None) and (tracking_uri is None):
            raise ValueError('If tracking is enabled, a `tracking_uri` must be provided')
        
        experiment_name = experiment_name if experiment_name is not None else 'Default'
        tags = tags if tags is not None else {}
        
        self.catalog = catalog
        self.parameters = parameters
        self.name = name
        self.requires = requires
        self.provides = provides
        self.ml_stage = ml_stage
        self.rebind = rebind
        self.run_id = run_id
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        self.tags = tags
        

    def pre_execute(self):
        """Code to be run prior to executing the step."""
        pass 


    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the step."""
        raise NotImplementedError(
            "`{}` is a subclass of WorkflowStep and"
            "it must implement the `execute` method".format(self.__class__.__name__)
        )


    def post_execute(self):
        """Code to be run after executing the step."""
        pass 