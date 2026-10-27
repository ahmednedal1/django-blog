from django.db import migrations, models


def copy_categories(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    links = Post.categories.through
    database = schema_editor.connection.alias
    posts = Post.objects.using(database).exclude(category_id=None)
    for post in posts.iterator():
        links.objects.using(database).create(
            post_id=post.pk,
            category_id=post.category_id,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0005_remove_post_name_post_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='categories',
            field=models.ManyToManyField(
                blank=True,
                related_name='posts',
                to='blog.category',
            ),
        ),
        migrations.RunPython(copy_categories),
        migrations.RemoveField(
            model_name='post',
            name='category',
        ),
    ]
