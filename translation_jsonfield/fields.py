import json

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _

from .utils import get_normalised_language
from .utils import normalise_language_code


class TranslationJSONField(JSONField):
    description = _('A JSON object with translations')

    def from_db_value(self, value, expression, connection):
        self.json_value = {}
        fdv = super().from_db_value(value, expression, connection)
        if isinstance(fdv, dict):
            self.json_value = fdv
            clean_value = self._get_value(fdv)
            self._prepare_json(clean_value)
            return clean_value
        return fdv

    def _get_value(self, json_value):
        """
        Returns the translated value for the active language or the default language if the
        active language is not available.

        This method is used to get the translated value of the field.
        """
        if isinstance(json_value, dict):
            lang = get_normalised_language()
            if lang is None:
                raise ImproperlyConfigured('Enable translations to use TranslationJSONField.')

            if lang not in json_value:
                lang = normalise_language_code(settings.LANGUAGE_CODE)

            return json_value.get(lang, None)

    def get_prep_value(self, value):
        if value is None:
            return value
        clean_value = self._prepare_json(value)
        return json.dumps(clean_value, cls=self.encoder)

    def _update_field(self, previous_value, new_value):
        """
        This method is used to create or update the translations of the field.
        """
        lang = get_normalised_language()
        if lang is None:
            raise ImproperlyConfigured('Enable translations to use TranslationJSONField.')
        if previous_value is not None and lang in previous_value:
            previous_value[lang] = new_value
        else:
            if isinstance(previous_value, dict):
                previous_value.update({lang: new_value})
            else:
                previous_value = {lang: new_value}
        return previous_value

    def _prepare_json(self, new_value):
        """
        Called by the save method of the model.
        This method ensures that the data is always saved as a JSON object with all the
        available translations.
        """
        if isinstance(self, TranslationJSONField):
            previous_value = getattr(self, 'json_value', None)
            if new_value != previous_value:
                if isinstance(new_value, dict):
                    # If a dict is received, it is assumed that the user wants to update all the
                    # translations of the field.
                    update_json = new_value
                else:
                    # If a string is received, it is assumed that the user wants to create or
                    # update only the translation of the active language.
                    update_json = self._update_field(previous_value, new_value)
                return update_json
            return new_value

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Attach the raw value to the model attribute to control access to the field values.
        """
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, f'{name}__raw', TranslationJSONFieldRaw(name))


class TranslationJSONFieldRaw:
    def __init__(self, field_name):
        self.field_name = field_name

    def __get__(self, instance, owner):
        field_obj = instance._meta.get_field(self.field_name)
        return getattr(field_obj, 'json_value', None)
