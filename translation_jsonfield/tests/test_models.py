from django.test import TestCase
from django.utils.translation import activate
from django.utils.translation import override

from translation_jsonfield.tests.test_app.models import IceCreamFlavour


class TranslationModelTest(TestCase):

    def test_start_with_string(self):
        activate('en_gb')

        ic = IceCreamFlavour.objects.create(flavour='vanilla')
        ic = IceCreamFlavour.objects.get(pk=ic.pk)

        self.assertEqual(ic.flavour, 'vanilla')
        self.assertIsNone(ic.topping)
        self.assertIsNone(ic.price)

        with override('fr_fr'):
            ic.flavour = 'vanille'
            ic.save()
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            self.assertEqual(ic.flavour, 'vanille')

        with override('en_gb'):
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            self.assertEqual(ic.flavour, 'vanilla')

        with override('fr_fr'):
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            self.assertEqual(ic.flavour, 'vanille')

        ic.topping = 'chocolate'
        ic.save()
        ic = IceCreamFlavour.objects.get(pk=ic.pk)
        self.assertEqual(ic.topping, 'chocolate')

        with override('fr_fr'):
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            ic.topping = 'chocolat'
            ic.price = 1.5
            ic.save()
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            self.assertEqual(ic.flavour, 'vanille')
            self.assertEqual(ic.topping, 'chocolat')
            self.assertEqual(ic.price, 1.5)

    def test_start_with_json(self):
        activate('en_gb')

        ic = IceCreamFlavour.objects.create(flavour={'en-gb': 'vanilla', 'fr-fr': 'vanille'})
        ic = IceCreamFlavour.objects.get(pk=ic.pk)
        self.assertEqual(ic.flavour, 'vanilla')
        self.assertIsNone(ic.topping)
        self.assertIsNone(ic.price)

        with override('fr_fr'):
            ic.flavour = 'vanille'
            ic.save()
            ic.refresh_from_db()
            self.assertEqual(ic.flavour, 'vanille')
            self.assertIsNone(ic.topping)
            self.assertIsNone(ic.price)

        ic.flavour = {'en-gb': 'vanilla', 'fr-fr': 'vanille', 'pt-pt': 'baunilha'}
        ic.save()
        ic = IceCreamFlavour.objects.get(pk=ic.pk)
        self.assertEqual(ic.flavour, 'vanilla')
        self.assertIsNone(ic.topping)
        self.assertIsNone(ic.price)

        with override('pt_pt'):
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            self.assertEqual(ic.flavour, 'baunilha')
            self.assertIsNone(ic.topping)
            self.assertIsNone(ic.price)

        ic = IceCreamFlavour.objects.create(
            flavour={'en-gb': 'vanilla', 'fr-fr': 'vanille'},
            topping={'en-gb': 'strawberry', 'fr-fr': 'fraise'}
        )

        ic = IceCreamFlavour.objects.get(pk=ic.pk)
        self.assertEqual(ic.flavour, 'vanilla')
        self.assertEqual(ic.topping, 'strawberry')

        with override('pt_pt'):
            ic.flavour = 'baunilha'
            ic.topping = 'morango'
            ic.price = 1.5
            ic.save()
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            self.assertEqual(ic.flavour, 'baunilha')
            self.assertEqual(ic.topping, 'morango')
            self.assertEqual(ic.price, 1.5)

        with override('se_se'):
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            # There are no translations for Swedish, so the default language is used
            self.assertEqual(ic.flavour, 'vanilla')
            self.assertEqual(ic.topping, 'strawberry')
            self.assertEqual(ic.price, 1.5)

    def test_raw_value(self):
        activate('en_gb')

        ic = IceCreamFlavour.objects.create(
            flavour={'en-gb': 'vanilla', 'fr-fr': 'vanille'},
            topping={'en-gb': 'strawberry', 'fr-fr': 'fraise'}
        )

        ic = IceCreamFlavour.objects.get(pk=ic.pk)
        self.assertEqual(ic.flavour, 'vanilla')
        self.assertEqual(ic.topping, 'strawberry')
        self.assertIsNone(ic.price)

        self.assertEqual(ic.flavour__raw, {'en-gb': 'vanilla', 'fr-fr': 'vanille'})
        self.assertEqual(ic.topping__raw, {'en-gb': 'strawberry', 'fr-fr': 'fraise'})
        self.assertTrue('price__raw' not in ic.__dict__)

        with override('se_se'):
            ic.flavour = 'vanilj'
            ic.topping = 'jordgubbe'
            ic.price = 1.5
            ic.save()
            ic = IceCreamFlavour.objects.get(pk=ic.pk)
            self.assertEqual(ic.flavour, 'vanilj')
            self.assertEqual(ic.topping, 'jordgubbe')
            self.assertEqual(ic.price, 1.5)

            self.assertEqual(
                ic.flavour__raw,
                {'en-gb': 'vanilla', 'fr-fr': 'vanille', 'se-se': 'vanilj'}
            )
            self.assertEqual(
                ic.topping__raw,
                {'en-gb': 'strawberry', 'fr-fr': 'fraise', 'se-se': 'jordgubbe'}
            )
            self.assertTrue('price__raw' not in ic.__dict__)
