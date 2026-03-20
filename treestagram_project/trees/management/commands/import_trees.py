import csv
from django.core.management.base import BaseCommand
from trees.models import Tree
import boto3


class Command(BaseCommand):
    help = "Import all trees from CSV"

    def download_csv():
        bucket = "treestagram-data-2026"
        key = "cleaned_tree_data.csv"
        local_path = "/tmp/cleaned_tree_data.csv"

        s3 = boto3.client("s3")
        s3.download_file(bucket, key, local_path)

        return local_path

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        file_path = self.download_csv()
        trees_to_create = []

        bool_cols = [
            "root_stone",
            "root_grate",
            "root_other",
            "trunk_wire",
            "trnk_light",
            "trnk_other",
            "brch_light",
            "brch_shoe",
            "brch_other",
        ]

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert Yes/No to True/False for boolean columns
                bool_data = {
                    col: True if row[col] == "True" else False for col in bool_cols
                }

                trees_to_create.append(
                    Tree(
                        tree_id=int(row["tree_id"]),
                        created_at=row["created_at"],
                        tree_dbh=int(row["tree_dbh"]),
                        stump_diam=int(row["stump_diam"]),
                        curb_loc=row["curb_loc"],
                        status=row["status"],
                        health=row["health"],
                        spc_latin=row["spc_latin"],
                        spc_common=row["spc_common"],
                        sidewalk=row["sidewalk"],
                        problems=row["problems"],
                        root_stone=bool_data["root_stone"],
                        root_grate=bool_data["root_grate"],
                        root_other=bool_data["root_other"],
                        trunk_wire=bool_data["trunk_wire"],
                        trnk_light=bool_data["trnk_light"],
                        trnk_other=bool_data["trnk_other"],
                        brch_light=bool_data["brch_light"],
                        brch_shoe=bool_data["brch_shoe"],
                        brch_other=bool_data["brch_other"],
                        address=row["address"],
                        zip_city=row["zip_city"],
                        borough=row["borough"],
                        latitude=float(row["latitude"]),
                        longitude=float(row["longitude"]),
                    )
                )

        Tree.objects.bulk_create(trees_to_create, batch_size=10000)
        self.stdout.write(self.style.SUCCESS("Import completed!"))
