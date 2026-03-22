import csv
import boto3
from django.core.management.base import BaseCommand
from trees.models import Tree


class Command(BaseCommand):
    help = "Import all trees from CSV stored in S3"

    def download_csv(self):
        bucket = "treestagram-data-2026"
        key = "cleaned_tree_data.csv"
        local_path = "/tmp/cleaned_tree_data.csv"

        self.stdout.write("Downloading CSV from S3...")
        s3 = boto3.client("s3")
        s3.download_file(bucket, key, local_path)

        self.stdout.write(f"Downloaded file to {local_path}")
        return local_path

    def handle(self, *args, **kwargs):
        # ✅ Prevent duplicate imports
        if Tree.objects.exists():
            self.stdout.write("Data already exists, skipping import.")
            return

        try:
            file_path = self.download_csv()

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

            batch = []
            batch_size = 1000
            total_inserted = 0

            self.stdout.write("Starting CSV processing...")

            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for i, row in enumerate(reader):
                    try:
                        bool_data = {
                            col: True if row[col] == "True" else False
                            for col in bool_cols
                        }

                        batch.append(
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

                        # ✅ Bulk insert in batches
                        if len(batch) >= batch_size:
                            Tree.objects.bulk_create(batch, batch_size=batch_size)
                            total_inserted += len(batch)
                            batch = []

                            self.stdout.write(f"Inserted {total_inserted} records...")

                    except Exception as row_error:
                        self.stderr.write(f"Skipping row {i}: {row_error}")

                # Insert remaining records
                if batch:
                    Tree.objects.bulk_create(batch, batch_size=batch_size)
                    total_inserted += len(batch)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import completed! Total inserted: {total_inserted}"
                )
            )

        except Exception as e:
            self.stderr.write(f"Import failed: {str(e)}")
            raise
