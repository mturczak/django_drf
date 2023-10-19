from django.db import migrations


def create_builtin_tiers(apps, schema_editor):
    Tier = apps.get_model("Django_API", "Tier")
    Tier.objects.create(
        name="Basic",
        thumbnail_sizes={"small": "200x200"},
        link_to_original=False,
        expiring_links=False,
    )
    Tier.objects.create(
        name="Premium",
        thumbnail_sizes={"small": "200x200", "large": "400x400"},
        link_to_original=True,
        expiring_links=False,
    )
    Tier.objects.create(
        name="Enterprise",
        thumbnail_sizes={"small": "200x200", "large": "400x400"},
        link_to_original=True,
        expiring_links=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("Django_API", "previous_migration_name"),
    ]

    operations = [
        migrations.RunPython(create_builtin_tiers),
    ]
