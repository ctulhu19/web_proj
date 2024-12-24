# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=256, verbose_name="Аффилиация ")

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Base(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату "
                  "и время в будущем — "
                  "можно делать отложенные публикации."
    )

    class Meta:
        ordering = '-pub_date'
        abstract = True


class Category(Base):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(unique=True,
                            verbose_name="Идентификатор",
                            help_text="Идентификатор страницы для URL; "
                                      "разрешены символы латиницы, "
                                      "цифры, дефис и подчёркивание."
                            )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Edition(Base):
    title = models.CharField(max_length=256, verbose_name="Название издания или журнала")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(unique=True,
                            verbose_name="Идентификатор",
                            help_text="Идентификатор страницы для URL; "
                                      "разрешены символы латиницы, "
                                      "цифры, дефис и подчёркивание."
                            )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        null=True,
    )
    image = models.ImageField(
        upload_to="media/",
        null=True,
        verbose_name="Обложка журнала",
        blank=True,
    )
    edition_file = models.FileField(upload_to="archive")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Издание'
        verbose_name_plural = 'Издание'


class Tags(models.Model):
    name = models.CharField(max_length=256, verbose_name="Ключевое слово")

    def __str__(self):
        return self.name


class Publication(Base):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    annotation = models.TextField(verbose_name="Аннотация", )
    text = models.TextField(verbose_name="Текст", )
    key_words = models.ManyToManyField(Tags, verbose_name="Ключевые слова", )
    pages = models.CharField(max_length=256, verbose_name="Страницы")
    authors = models.ManyToManyField(
        Author,
        verbose_name="Авторы публикации",
    )
    edition = models.ForeignKey(
        Edition,
        on_delete=models.SET_NULL,
        verbose_name="Издание",
        null=True,
    )
    link = models.ManyToManyField(
        "self",
        null=True,
        blank=True
    )
    article = models.FileField(upload_to="archive")
    application = models.BooleanField(default=False, verbose_name="В статусе заявки(True) или опубликовано(False)")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
