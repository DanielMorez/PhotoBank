from django.db import models
from .models import PhotoType


class RusLang(models.Model):

    #<section class='home-section'>
    home_section_up = models.CharField(max_length=50, verbose_name='Вверхний загаловок', default='Извлеки из момента максимум')
    home_section_first_part = models.CharField(max_length=50, verbose_name='Первая часть заголовка', default='Делаем это ')
    home_section_second_part = models.CharField(max_length=50, verbose_name='Меняющаяся часть', default='легко | просто | креативно')
    #</section>

    #<div class='features-icon'>
    idea_title = models.CharField(max_length=50, verbose_name='Идеи & Концепции', default='Идеи & Концепции')
    idea_text = models.TextField(
        verbose_name='Текст: идеи и концепции',
        default='Бережное отношение к деталям и индивидуальный подход к каждому клиенту — основные правила нашей работы'
    )
    design_title = models.CharField(max_length=50, verbose_name='Дизайн & Интерфейс', default='Дизайн & Интерфейс')
    design_text = models.TextField(
        verbose_name='Текст: дизайн м интерфейс',
        default='Креативный подход и не стандартные решения'
    )
    develop_title = models.CharField(max_length=50, verbose_name='Разработка & Продакшн', default='Разработка & Продакшн')
    develop_text = models.TextField(
        verbose_name='Текст: разработка м продакшн',
        default='Мы используем информационные технологии, чтобы делать вашу жизнь проще'
    )
    support_title = models.CharField(max_length=50, verbose_name='Поддержка',
                                     default='Отзывчивая поддержка')
    support_text = models.TextField(
        verbose_name='Текст: поддержка',
        default='Мы всегда расскажем, покажем, подскажем и объясним что и как'
    )
    #</div>

    about_quotes = models.TextField(
        verbose_name='О нас: цитата',
        default='Наши работы овладевают душой, отправляя вас к тому событию, будто оно происходит здесь и сейчас.'
    )

    about_text = models.TextField(
        verbose_name='О нас: текст',
        default='Наши клиенты всегда остаются для нас в приоритете, поэтому мы постоянно работаем на качество наших услуг. '
    )

    # Часто задаваемые вопросы
    question_one = models.CharField(max_length=512, verbose_name='Вопрос 1', default='Сколько стоят наши услуги?')
    answer_one = models.TextField(
        verbose_name='Вопрос 1: ответ',
        default='Во много это будет зависеть от объема работы и пожеланий клиента. Но однозначно дешевле чем у конкурентов.'
    )
    question_two = models.CharField(max_length=512, verbose_name='Вопрос 2', default='Как быстро вы отдаете фотографии?')
    answer_two = models.TextField(
        verbose_name='Вопрос 2: ответ',
        default='Все работы мы отдаем до 7 дней.'
    )
    question_three = models.CharField(max_length=512, verbose_name='Вопрос 3', default='Проводите ли вы видео трансляции?')
    answer_three = models.TextField(
        verbose_name='Вопрос 3: ответ',
        default='Да'
    )
    question_four = models.CharField(max_length=512, verbose_name='Вопрос 4', default='Возможно заказать вас в другую страну/город?')
    answer_four = models.TextField(
        verbose_name='Вопрос 4: ответ',
        default='Нужно обговаривать индивидуально. Возможно.'
    )

    def __str__(self):
        return f'{self.id}: Русская модель сайта'


class EstLang(models.Model):

    # <section class='home-section'>
    home_section_up = models.CharField(max_length=50, verbose_name='Вверхний загаловок',
                                       default='Kasutage hetke maksimaalselt')
    home_section_first_part = models.CharField(max_length=50, verbose_name='Первая часть заголовка',
                                               default='Tee seda ')
    home_section_second_part = models.CharField(max_length=50, verbose_name='Меняющаяся часть',
                                                default='lihtne | lihtsalt | loovalt')
    # </section>

    # <div class='features-icon'>
    idea_title = models.CharField(max_length=50, verbose_name='Идеи & Концепции', default='Ideed ja kontseptsioonid')
    idea_text = models.TextField(
        verbose_name='Текст: идеи и концепции',
        default='Hoolimine detailide eest ja individuaalne lähenemine igale kliendile on meie töö põhireeglid'
    )
    design_title = models.CharField(max_length=50, verbose_name='Дизайн & Интерфейс', default='Kujundus ja liides')
    design_text = models.TextField(
        verbose_name='Текст: дизайн м интерфейс',
        default='Loov lähenemine ja mittestandardsed lahendused'
    )
    develop_title = models.CharField(max_length=50, verbose_name='Разработка & Продакшн',
                                     default='Arendus ja tootmine')
    develop_text = models.TextField(
        verbose_name='Текст: разработка м продакшн',
        default='Teie elu lihtsustamiseks kasutame infotehnoloogiat'
    )
    support_title = models.CharField(max_length=50, verbose_name='Поддержка',
                                     default='Reageeriv tugi')
    support_text = models.TextField(
        verbose_name='Текст: поддержка',
        default='Me ütleme, näitame, õhutame ja selgitame alati, mida ja kuidas'
    )
    # </div>

    about_quotes = models.TextField(
        verbose_name='О нас: цитата',
        default='Meie teosed saavad hinge valduse, saates teid sündmusele justkui see juhtuks siin ja praegu.'
    )

    about_text = models.TextField(
        verbose_name='О нас: текст',
        default='Meie kliendid on alati meie jaoks esmatähtsad, seetõttu töötame pidevalt oma teenuste kvaliteedi kallal.'
    )

    # Часто задаваемые вопросы
    question_one = models.CharField(max_length=512, verbose_name='Вопрос 1', default='Kui palju meie teenused maksavad?')
    answer_one = models.TextField(
        verbose_name='Вопрос 1: ответ',
        default='See sõltub suuresti töö mahust ja kliendi soovidest. Kuid kindlasti odavam kui konkurent.'
    )
    question_two = models.CharField(max_length=512, verbose_name='Вопрос 2',
                                    default='Kui kiiresti fotosid esitate?')
    answer_two = models.TextField(
        verbose_name='Вопрос 2: ответ',
        default='Tarnime kogu töö 7 päeva jooksul.'
    )
    question_three = models.CharField(max_length=512, verbose_name='Вопрос 3',
                                      default='Kas edastate videot?')
    answer_three = models.TextField(
        verbose_name='Вопрос 3: ответ',
        default='Oh, kindlasti!'
    )
    question_four = models.CharField(max_length=512, verbose_name='Вопрос 4',
                                     default='Kas teid on võimalik tellida mõnda teise riiki/linna?')
    answer_four = models.TextField(
        verbose_name='Вопрос 4: ответ',
        default='Seda tuleb eraldi arutada. Võib olla.'
    )

    def __str__(self):
        return f'{self.id}: Эстонская модель сайта'


class ContactInfo(models.Model):

    company = models.CharField(max_length=50, verbose_name='Название компании', default='FOTOLIFE-SCHOOL')
    address = models.TextField(verbose_name='Адрес', default='', null=True, blank=True)
    city = models.CharField(max_length=25, verbose_name='Город', default='Талин', null=True, blank=True)
    zip = models.CharField(max_length=12, verbose_name='Индекс', default='', null=True, blank=True)

    email = models.EmailField(verbose_name='Email', default='fotolife.school@gmail.com')
    phone = models.CharField(max_length=12, verbose_name='Телефон', default='58256779')

class StaticImage(models.Model):

    MIN_RESOLUTION_BACK = (1920, 1080)
    MIN_RESOLUTION_ABOUT = (1920, 1080)
    MIN_RESOLUTION_REVIEW = (2560, 1440)

    background = models.ImageField(verbose_name='Фотография для главной')
    about = models.ImageField(verbose_name='Фотография для "О нас"')
    review = models.ImageField(verbose_name='Фотография для отзывов')

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.background.storage, self.background.path
        about, apath = self.about.storage, self.about.path
        review, rpath = self.review.storage, self.review.path
        # Delete the model before the file
        super(StaticImage, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)
        about.delete(apath)
        review.delete(rpath)

    def __str__(self):
        return f'{self.id}: Статические избражения на главной'


class Review(models.Model):

    author = models.CharField(max_length=512, verbose_name='Автор')
    company = models.CharField(max_length=512, verbose_name='Школа', null=True, blank=True)
    quote = models.TextField(verbose_name='Отзыв')

    def __str__(self):
        return f'{self.id}: {self.author}'


class Media(models.Model):

    youtube = models.URLField(verbose_name='YouTube', null=True, blank=True)
    facebook = models.URLField(verbose_name='Facebook', null=True, blank=True)
    instagram = models.URLField(verbose_name='Instagram', null=True, blank=True)
    twitter = models.URLField(verbose_name='Twiter', null=True, blank=True)

class Portfolio(models.Model):

    title = models.CharField(max_length=50, verbose_name='Заголовок')
    image = models.ImageField(verbose_name='Фотография')
    type_of_photo = models.ForeignKey(PhotoType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}: {self.title}'

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.Image.storage, self.image.path
        # Delete the model before the file
        super(Portfolio, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)


class ServiceAndPrice(models.Model):

    title = models.CharField(max_length=50, verbose_name='Название услуги')
    description = models.CharField(max_length=256, verbose_name='Краткое описание')
    price = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return f'{self.id}: {self.title}: {self.price}'

class EmailCredentials(models.Model):

    email = models.EmailField(verbose_name='Электронный адрес отправителя')
    password = models.CharField(max_length=50, verbose_name='Пароль от ящика')
    server = models.CharField(max_length=50, verbose_name='Сервер', default='smtp.gmail.com')
    port = models.PositiveSmallIntegerField(verbose_name='Порт', default=587)
    iban = models.CharField(max_length=70, verbose_name='Реквизиты для оплаты', default='OU PHOTOBOUTIQUE EE491010220236822220')

    def __str__(self):
        return f'{self.id}: {self.email}'