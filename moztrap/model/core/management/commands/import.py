"""
Import Suite and Case data for a given Product Version.

The "suites" or "cases" sections are optional.
The data must be in JSON format and structured like this::

    {
        "suites": [
            {
                "name": "suite1 name",
                "description": "suite description"
            }
        ]
        "cases": [
            {
                "name": "case title",
                "description": "case description",
                "tags": ["tag1", "tag2", "tag3"],
                "suites": ["suite1 name", "suite2 name", "suite3 name"],
                "created_by": "cdawson@mozilla.com"
                "steps": [
                    {
                        "instruction": "insruction text",
                        "expected": "expected text"
                    }
                ]
            }
        ]
    }

"""

from django.core.management.base import BaseCommand, CommandError

import json

from moztrap.model.core.models import Product, ProductVersion
from moztrap.model.library.importer import Importer



class Command(BaseCommand):
    args = "<product_name> <product_version> <filename>"
    help = (
        "Imports the cases from a JSON file into "
        "the specified Product Version")


    def handle(self, *args, **options):
        if not len(args) == 3:
            raise CommandError("Usage: {0}".format(self.args))

        try:
            product = Product.objects.get(name=args[0])
        except Product.DoesNotExist:
            raise CommandError('Product "{0}" does not exist'.format(args[0]))

        try:
            product_version = ProductVersion.objects.get(
                product=product, version=args[1])
        except ProductVersion.DoesNotExist:
            raise CommandError(
                'Version "{0}" of product "{1}" does not exist'.format(
                    args[1], args[0])
                )

        try:
            with open(args[2]) as fh:

                # try to import this as JSON
                try:
                    case_data = json.load(fh)   # pragma: no branch
                except ValueError as e:
                    raise CommandError(
                        "Could not parse JSON: {0}".format(str(e)))

                # @@@: support importing as CSV.  Rather than returning an
                # error above, just try CSV import instead.

        except IOError as (errno, strerror):
            raise CommandError(
                'Could not open "{0}", I/O error {1}: {2}'.format(
                    args[2], errno, strerror)
                )

        result_list = Importer().import_data(
            product_version, case_data).get_as_list()
        result_list.append("")
        self.stdout.write("\n".join(result_list))
