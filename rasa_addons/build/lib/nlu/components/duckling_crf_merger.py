from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from rasa.nlu.components import Component
from typing import Any, List, Optional, Text, Dict

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.nlu.classifiers.classifier import IntentClassifier
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.exceptions import FileIOException

from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.model import Metadata
from rasa.shared.nlu.training_data.message import Message

from rasa.nlu.featurizers.sparse_featurizer.sparse_featurizer import SparseFeaturizer

logger = logging.getLogger(__name__)


class DucklingCrfMerger(GraphComponent, Component):
    """Merges Duckling and CRF entities"""

    name = "DucklingCrfMerger"

    provides = []

    defaults = {
        "entities": None,
        "duckling_name": "DucklingHTTPExtractor",
        "extractor_names": [
            "DIETClassifier",
            "SpacyEntityExtractor",
            "CRFEntityExtractor",
            "MitieEntityExtractor",
        ],
    }

    # def __init__(self, component_config=None):
    # type: (Text, Optional[List[Text]]) -> None

    # super(DucklingCrfMerger, self).__init__(component_config)

    def __init__(self, component_config: Dict[Text, Any]) -> None:
        self.component_config = component_config

    # @classmethod
    # def create(
    #    cls, component_config: Dict[Text, Any], config: RasaNLUModelConfig
    # ) -> "DucklingCrfMerger":
    #    return cls(component_config)
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        return cls(config)

    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None
        crf_entities = list(
            filter(
                lambda e: e["extractor"] in self.component_config["extractor_names"]
                and e["entity"] in self.component_config["entities"].keys(),
                message.get("entities"),
            )
        )
        indices_to_remove = []

        for index, duck_entity in enumerate(message.get("entities")):
            if duck_entity["extractor"].startswith(
                self.component_config["duckling_name"]
            ):
                # looking for CRF entities surrounding the duckling one matching config settings
                containing_crf = list(
                    filter(
                        lambda e: e["start"] <= duck_entity["start"]
                        and e["end"] >= duck_entity["end"]
                        and duck_entity["entity"]
                        in self.component_config["entities"][e["entity"]],
                        crf_entities,
                    )
                )
                # list -> single object
                containing_crf = (
                    containing_crf[0]
                    if type(containing_crf) is list and len(containing_crf) > 0
                    else None
                )
                if containing_crf is not None:
                    # Add duckling value + additional infos
                    containing_crf["value"] = duck_entity["value"]
                    containing_crf["additional_info"] = duck_entity["additional_info"]
                    indices_to_remove.append(index)

        # Remove merged duckling entities
        for i in sorted(indices_to_remove, reverse=True):
            del message.get("entities")[i]

    '''@classmethod
    def load(
        cls,
        component_meta: Dict[Text, Any],
        model_dir: Text = None,
        model_metadata: Metadata = None,
        cached_component: Optional["DucklingCrfMerger"] = None,
        **kwargs: Any
    ) -> "DucklingCrfMerger":
        return cls(component_meta)
    '''
    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> DucklingCrfMerger:
        model_data = {}

        try:
            with model_storage.read_from(resource) as path:

                model_data_file = path / "model_data.json"
                model_data = json.loads(rasa.shared.utils.io.read_file(model_data_file))

        except (ValueError, FileNotFoundError, FileIOException):
            logger.debug(
                f"Couldn't load metadata for component '{cls.__name__}' as the persisted "
                f"model data couldn't be loaded."
            )

        return cls(
            config, model_data=model_data
        )
