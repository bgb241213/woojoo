"""칸을 실제 행으로 세운다.

사진마다 칸 이름을 문자열로 적던 것을 OptionColumn 행으로 옮기고, 사진은
그 칸을 가리키게 한다. 같은 장치 안에서 이름이 같던 사진들이 한 칸으로
모이고, 칸 순서는 그 이름이 처음 나온 사진의 순서를 따른다 — 지금 화면에
놓인 좌우 순서가 그대로 유지된다.
"""
from django.db import migrations, models
import django.db.models.deletion


def build_columns(apps, schema_editor):
    OptionDevice = apps.get_model('options', 'OptionDevice')
    OptionColumn = apps.get_model('options', 'OptionColumn')
    OptionPhoto = apps.get_model('options', 'OptionPhoto')

    for device in OptionDevice.objects.all():
        seen = {}
        for photo in OptionPhoto.objects.filter(device=device).order_by('order', 'id'):
            key = photo.column_label
            column = seen.get(key)
            if column is None:
                column = OptionColumn.objects.create(
                    device=device, label=key, tag=photo.column_tag, order=len(seen),
                )
                seen[key] = column
            photo.column = column
            photo.save(update_fields=['column'])


class Migration(migrations.Migration):

    dependencies = [
        ('options', '0003_optionphoto_caption'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionColumn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('label', models.CharField(help_text='칸 위에 굵게 나옵니다. 예: 철망/메쉬망 보양',
                                           max_length=100, verbose_name='칸 제목')),
                ('tag', models.CharField(blank=True, help_text='선택. 제목 위 회색 글씨입니다. 예: 장착 A타입',
                                         max_length=50, verbose_name='작은 라벨')),
                ('order', models.PositiveIntegerField(default=0, help_text='작을수록 왼쪽에 놓입니다.',
                                                      verbose_name='순서')),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                             related_name='columns_set', to='options.optiondevice',
                                             verbose_name='옵션 장치')),
            ],
            options={
                'verbose_name': '칸',
                'verbose_name_plural': '칸',
                'ordering': ['order', 'id'],
            },
        ),
        # 채우는 동안은 비어 있어도 되도록 null 로 만들고, 옮긴 뒤 조인다.
        migrations.AddField(
            model_name='optionphoto',
            name='column',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='photos', to='options.optioncolumn',
                                    verbose_name='어느 칸에'),
        ),
        migrations.RunPython(build_columns, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='optionphoto',
            name='column',
            field=models.ForeignKey(help_text='위에서 만든 칸 중 하나를 고르세요.',
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='photos', to='options.optioncolumn',
                                    verbose_name='어느 칸에'),
        ),
        migrations.AlterField(
            model_name='optionphoto',
            name='device',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='photos', to='options.optiondevice',
                                    verbose_name='옵션 장치'),
        ),
        migrations.RemoveField(model_name='optionphoto', name='column_label'),
        migrations.RemoveField(model_name='optionphoto', name='column_tag'),
    ]
