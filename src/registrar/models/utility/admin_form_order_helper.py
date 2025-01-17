import logging
from typing import Dict
from django.forms import ModelChoiceField

logger = logging.getLogger(__name__)


class SortingDict:
    """Stores a sorting dictionary object"""

    _sorting_dict: Dict[type, type] = {}

    def __init__(self, model_list, sort_list):
        self._sorting_dict = {
            "dropDownSelected": self.convert_list_to_dict(model_list),
            "sortBy": sort_list,
        }

    # Used in __init__ for model_list for performance reasons
    def convert_list_to_dict(self, value_list):
        """Used internally to convert model_list to a dictionary"""
        return {item: item for item in value_list}

    def get_dict(self):
        """Grabs the associated dictionary item,
        has two fields: 'dropDownSelected': model_list and 'sortBy': sort_list"""
        # This should never happen so we need to log this
        if self._sorting_dict is None:
            raise ValueError("_sorting_dict was None")
        return self._sorting_dict


class AdminFormOrderHelper:
    """A helper class to order a dropdown field in Django Admin,
    takes the fields you want to order by as an array"""

    # Used to keep track of how we want to order_by certain FKs
    _sorting_list: list[SortingDict] = []

    def __init__(self, sort: list[SortingDict]):
        self._sorting_list = sort

    def get_ordered_form_field(self, form_field, db_field) -> ModelChoiceField | None:
        """Orders the queryset for a ModelChoiceField
        based on the order_by_dict dictionary"""
        _order_by_list = []

        for item in self._sorting_list:
            item_dict = item.get_dict()
            drop_down_selected = item_dict.get("dropDownSelected")
            sort_by = item_dict.get("sortBy")

            if db_field.name in drop_down_selected:
                _order_by_list = sort_by
                # Exit loop when order_by_list is found
                break

        # Only order if we choose to do so
        # noqa for the linter... reduces readability otherwise
        if _order_by_list is not None and _order_by_list != []:  # noqa
            form_field.queryset = form_field.queryset.order_by(*_order_by_list)

        return form_field
