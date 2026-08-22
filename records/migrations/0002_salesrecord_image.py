from django.db import migrations, models


class Migration(migrations.Migration):
    """실적 하나에 사진 한 장. 사진 칸을 실적 행으로 옮긴다."""

    dependencies = [
        ('records', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesrecord',
            name='image',
            field=models.ImageField(blank=True, upload_to='records/', verbose_name='사진'),
        ),
        # 사진 여러 장짜리 실적은 장마다 행으로 쪼개지므로 폴더 번호가 겹친다.
        migrations.AlterField(
            model_name='salesrecord',
            name='photo_key',
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name='사진 폴더 ID',
                help_text='처음 사진을 불러온 폴더 번호입니다. 비워두셔도 됩니다.'),
        ),
    ]
