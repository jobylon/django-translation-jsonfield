# django-translation-jsonfield


[![Tests](https://github.com/jobylon/django-translation-jsonfield/workflows/Test/badge.svg)](https://github.com/jobylon/django-translation-jsonfield/actions?query=workflow%3ATest)

django-translation-jsonfield is a custom field for Django that allows to store translations in a JSON field.
This package was inspired by [Django JSON Model Translations](https://github.com/ana-balica/django-json-model-translations/).



## Usage/Examples

```python
from django.db import models

from translation_jsonfield.fields import TranslationJSONField
from translation_jsonfield.models import ModelJSONTranslate


class IceCreamFlavour(ModelJSONTranslate):
    flavour = TranslationJSONField()
    topping = TranslationJSONField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
```

```python
activate('en_gb')

ic = IceCreamFlavour.objects.create(flavour='vanilla')
print(ic.flavour)  # vanilla
print(ic.flavour__raw)  # {'en-gb': 'vanilla'}

with override('pt_pt'):
    ic = IceCreamFlavour.objects.get(pk=ic.pk)
    ic.flavour = 'baunilha'
    ic.save()

    print(ic.flavour)  # baunilha
    print(ic.flavour_raw)  # {'en-gb': 'vanilla', 'pt-pt': 'baunilha'}


ic.flavour = {'fr-fr': 'vanille', 'se-se': 'vanilj'}
ic.save()

with override('se-se'):
    print(ic.flavour)  # vanilj
    print(ic.flavour_raw)  # {'fr-fr': 'vanille', 'se-se': 'vanilj'}


with override('nl-nl'):
    # There is no Dutch translation. Fallback to the default language.
    print(ic.flavour)  # vanilla

```
