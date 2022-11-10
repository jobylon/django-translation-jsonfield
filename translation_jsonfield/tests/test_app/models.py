from django.db.models import DecimalField
from django.db.models import Model

from translation_jsonfield.fields import TranslationJSONField


class IceCreamFlavour(Model):
    flavour = TranslationJSONField()
    topping = TranslationJSONField(null=True, blank=True)
    price = DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)