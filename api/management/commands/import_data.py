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


class Command(BaseCommand):
    help = 'Import data from Excel to MySQL'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        excel_file = os.path.join(
            base_dir, '..', '..', 'data', 'suburbs_3.xlsx')

        df = pd.read_excel(excel_file)

        db = MySQLdb.connect(host="localhost", user=username,
                             passwd=password, db=DB)
        cursor = db.cursor()
        # for col in df.columns:
        #     print("Name col: ", col)

        for index, row in df.iterrows():
            nearby_dis = eval(row['Nearby_Dis'])

            instance = Suburbs(
                id_suburb=row['id'],
                Suburb=row['Suburb'],
                State=row['State'],
                Postcode=row['Postcode'],
                Combined=row['Combined'],
                Latitude=row['Latitude'],
                Longitude=row['Longitude'],
                CBD=row['CBD'],
                id_old=row["id_old"],
                Len=row["Len"],
            )
            instance.save()

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
