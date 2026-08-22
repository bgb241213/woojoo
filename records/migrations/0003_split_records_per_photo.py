"""사진 행을 실적 행으로 옮긴다 — 한 실적에 한 장.

기존에는 실적 하나가 사진 여러 장을 거느렸다. 첫 장은 그 실적이 그대로
가져가고, 나머지는 같은 정보를 복사한 새 실적이 된다. 파일은 이미 저장소에
있으므로 경로만 옮기면 되고, 새로 올리거나 변환하지 않는다.
"""
from django.db import migrations


def split(apps, schema_editor):
    SalesRecord = apps.get_model('records', 'SalesRecord')
    SalesRecordImage = apps.get_model('records', 'SalesRecordImage')

    for record in SalesRecord.objects.all().order_by('id'):
        photos = list(SalesRecordImage.objects.filter(record=record).order_by('order', 'id'))
        if not photos:
            continue
        record.image = photos[0].image
        record.save(update_fields=['image'])
        for extra in photos[1:]:
            SalesRecord.objects.create(
                image=extra.image,
                model_name=record.model_name,
                shipped_date=record.shipped_date,
                # 폴더 번호는 원본 실적에만 남긴다 — 어느 폴더에서 왔는지는
                # 한 곳에만 적혀 있으면 된다.
                photo_key=None,
                is_active=record.is_active,
            )


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_salesrecord_image'),
    ]

    operations = [
        migrations.RunPython(split, migrations.RunPython.noop),
    ]
