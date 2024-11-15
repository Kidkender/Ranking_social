from django.core.management.base import BaseCommand
import pandas as pd
import MySQLdb
from ...models import Suburbs
import os
from dotenv import load_dotenv
load_dotenv()

DB = os.environ.get('MYSQL_DATABASE')
username = os.environ.get('MYSQL_USER')
password = os.environ.get('MYSQL_PASSWORD')
host = os.environ.get('DB_HOST')


class Command(BaseCommand):
    help = 'Import data from Excel to MySQL'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Excel file name')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        base_dir = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(base_dir, '..', '..', 'data', excel_file)

        if not os.path.exists(excel_path):
            self.stdout.write(
                self.style.ERROR(f'Excel file {excel_file} not found'))
            return

        df = pd.read_excel(excel_path)

        db = MySQLdb.connect(host=host, user=username,
                             passwd=password, db=DB)
        cursor = db.cursor()

        for index, row in df.iterrows():
            nearby_dis = eval(row['Nearby_Dis'])
            value_of_beach = row['Beach'] != 0 and not pd.isna(row['Beach'])

            value_of_train = row['Train'] != 0 and not pd.isna(row['Train'])

            instance = Suburbs(
                SA1=row['SA1'],
                SAL=row['SAL'],
                SAL_CODE_2021=row['SAL_CODE_2021'],
                Council=row['Council'],
                Suburb=row['Suburb'],
                State=row['State'],
                Postcode=row['Postcode'],
                Combined=row['Combined'],
                Latitude=row['Latitude'],
                Longitude=row['Longitude'],
                CBD=row['CBD'],

                Nearby_Dis=row['Nearby_Dis'],
                Nearby=row['Nearby'],
                Nearby_Dis_List=row['Nearby_Dis_List'],
                Nearby_List=row['Nearby_List'],
                Nearby_List_Codes=row['Nearby_List_Codes'],
                Good_Schools=round(row['Good_Schools'], 1),
                Train=value_of_train,
                Beach=value_of_beach,
            )
            instance.save()

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
