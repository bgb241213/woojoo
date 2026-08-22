"""사진 테이블을 걷어낸다. 사진은 앞 단계에서 실적 행으로 모두 옮겨졌다.

테이블만 사라질 뿐 저장소의 파일은 그대로다 — 마이그레이션은 모델 시그널을
타지 않으므로 R2 파일이 함께 지워지지 않는다.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0003_split_records_per_photo'),
    ]

    operations = [
        migrations.RemoveField(model_name='salesrecordimage', name='record'),
        migrations.DeleteModel(name='SalesRecordImage'),
    ]
