from django.db import models


class Tree(models.Model):
    tree_id = models.IntegerField(unique=True)
    created_at = models.CharField(max_length=50)  # CSV has object type
    tree_dbh = models.IntegerField()
    stump_diam = models.IntegerField()
    curb_loc = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    health = models.CharField(max_length=20)
    spc_latin = models.CharField(max_length=100)
    spc_common = models.CharField(max_length=100)
    sidewalk = models.CharField(max_length=20)
    problems = models.CharField(max_length=200, null=True, blank=True)

    # Boolean fields
    root_stone = models.BooleanField()
    root_grate = models.BooleanField()
    root_other = models.BooleanField()
    trunk_wire = models.BooleanField()
    trnk_light = models.BooleanField()
    trnk_other = models.BooleanField()
    brch_light = models.BooleanField()
    brch_shoe = models.BooleanField()
    brch_other = models.BooleanField()

    address = models.CharField(max_length=200)
    zip_city = models.CharField(max_length=50)
    borough = models.CharField(max_length=50)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)

    def __str__(self):
        return f"{self.spc_common} ({self.tree_id})"
    
    class Meta:
        indexes = [
            models.Index(fields=["latitude", "longitude"]),
        ]
