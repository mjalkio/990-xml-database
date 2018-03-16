import csv
import os

from django.core.management.base import BaseCommand
from filing.models import Filing
from django.conf import settings
from irsx.settings import INDEX_DIRECTORY


BATCH_SIZE = 10000

class Command(BaseCommand):
    help = '''
        Read the yearly csv file line by line and add new lines if 
        they don't exist. Lines are added in bulk at the end.
    '''

    def add_arguments(self, parser):
            # Positional arguments
            parser.add_argument('year', nargs='+', type=int)

    def handle(self, *args, **options):

        for year in options['year']:
            filepath = os.path.join(INDEX_DIRECTORY, "index_%s.csv" % year)
            print("Entering xml submissions from %s" % filepath)
            fh = open(filepath, 'r')
            reader = csv.reader(fh)
            rows_to_enter = []

            # ignore header rows

            # python 2 idiom: headers = reader.next() <--- but this is a django 2 thing, so no python 2.X
            next(reader)
            count = 0
            for line in reader:
                (return_id, filing_type, ein, tax_period, sub_date, taxpayer_name, return_type, dln, object_id) = line
                
                try:
                    obj = Filing.objects.get(object_id=object_id)
                except Filing.DoesNotExist:
                    new_sub  = Filing(
                        return_id=return_id,
                        submission_year=year,
                        filing_type=filing_type,
                        ein=ein,
                        tax_period=tax_period,
                        sub_date=sub_date,
                        taxpayer_name=taxpayer_name,
                        return_type=return_type,
                        dln=dln,
                        object_id=object_id
                    )
                    
                    rows_to_enter.append(new_sub)
                    count += 1

                if count % BATCH_SIZE == 0 and count > 0:
                    print("Committing %s total entered=%s" % (BATCH_SIZE, count) )
                    Filing.objects.bulk_create(rows_to_enter)
                    print("commit complete")
                    rows_to_enter = []

            Filing.objects.bulk_create(rows_to_enter)
            print("Added %s new entries." % (count) )