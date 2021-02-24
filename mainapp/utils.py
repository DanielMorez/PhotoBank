import smtplib

from os.path import basename

from django.db import models

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .model_static import EmailCredentials


def contact_mail(name, email, message):

    credentials = EmailCredentials.objects.last()
    # create message object instance
    msg = MIMEMultipart("alternative")

    # setup the parameters of the message
    password = credentials.password
    msg['From'] = credentials.email
    msg['To'] = credentials.email
    msg['Subject'] = f"Письмо от {name}"

    html = f"""\
        <h2 style="text-align: left;">Письмо от {name}, {email}.</h2>
        <br>
        <p><i>{message}</i></p>
    """
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP(f'{credentials.server}: {credentials.port}') as server:
        server.starttls()
        # Login Credentials for sending the mail
        server.login(msg['From'], password)
        # send the message via the server.
        response = server.sendmail(msg['From'], msg['To'], msg.as_string())

    return response


def send_mail(addr_to, first_name, last_name, phone, comment, cart):

    credentials = EmailCredentials.objects.last()

    # create message object instance
    msg = MIMEMultipart("alternative")

    # setup the parameters of the message
    password = credentials.password
    msg['From'] = credentials.email
    msg['To'] = addr_to
    msg['Subject'] = "Заказ #1"

    html = f"""\
        <html>
            </head>
          <body>
            <h3 style='text-align:center;'>Оплата</h3>
            <br>
            <table style='text-align: left; margin-left: auto; margin-right: auto; border: 1px solid black;'>
                <tbody>
                    <tr>
                        <td>Реквизиты для оплаты</td>
                        <td style="text-align:left; padding-left:20px"><strong>{credentials.iban}</strong></td>
                    </tr>
                    <tr>
                        <td>В комментарие к оплате укажите</td>
                        <td style="text-align:left; padding-left:20px"><strong>школу, класс, имя ребенка</strong></td>
                    </tr>
                    <tr>
                        <td>Имя покупателя</td>
                        <td style="text-align:left; padding-left:20px"><strong>{first_name.upper()} {last_name.upper()}</strong></td>
                    </tr>
                    <tr>
                        <td>Телефон покупателя</td>
                        <td style="text-align:left; padding-left:20px"><strong>{phone}</strong></td>
                    </tr>
                    <tr>
                        <td>Email покупателя</td>
                        <td style="text-align:left; padding-left:20px"><strong>{addr_to}</strong></td>
                    </tr>
                    <tr>
                        <td>Комментарий к заказу</td>
                        <td style="text-align:left; padding-left:20px"><strong>{comment}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <br>
            <br>
            <h3 style='text-align: center;'>Заказ #{cart.id}</h3>
            <table style='text-align: center; margin-left: auto; margin-right: auto; border: 1px solid black;'>
                <thead>
                    <tr>
                        <td><strong>ID</strong></td>
                        <td style="text-align:left; padding-left:20px"><strong>Название</strong></td>
                        <td style="text-align:left; padding-left:20px"><strong>Формат</strong></td>
                        <td style="text-align:left; padding-left:20px"><strong>Цена</td>
                        <td style="text-align:left; padding-left:20px"><strong>Кол-во</strong></td>
                        <td style="text-align:left; padding-left:20px"><strong>Общая цена</strong></td>
                    </tr>
                </thead>
                <tbody>
    """
    for item in cart.related_products.all():
        html += f"""\
            <tr>
              <td rowspan="{item.services.count}">
                  {item.content_object.id}
              </td>
              <td style="text-align:left; padding-left:20px" rowspan="{item.services.count()}">
                <h5>{item.content_object.title}</h5>
              </td>
              <td style="text-align:left; padding-left:20px">
                <h5>{item.services.all().last().service.title}</h5>
              </td>
              <td style="text-align:left; padding-left:20px">
                <h5>€ {item.services.all().last().service.price}</h5>
              </td>
              <td style="text-align:left; padding-left:20px">
                <h5>€ {item.services.all().last().qty}</h5>
              </td>
              <td style="text-align:left; padding-left:20px" rowspan="{item.services.count()}">
                <h5>€ {item.final_price}</h5>
              </td>
            </tr>
        """

        for service in item.services.all():
            if item.services.last() != service:
                html += f"""
                    <tr>
                        <td>
                        <h5>{service.service.title}</h5>
                      </td>
    
                      <td>
                        <h5>€ {service.service.price}</h5>
                      </td>
                      <td>
                          <h5>{ service.qty }</h5>
                      </td>
                    </tr>
                """

    html += f"""\
                <tr>
                    <td col='4'></td>
                    <td><strong>Итог</strong></td>
                    <td><strong>{cart.final_price}</strong></td>
                </tr>
                </tbody>
            </table>
            <br>
            <h4 style='text-align: center;'>Возникли вопросы?</h4>
            Решение спорных моментов, проблем с заказами: <i>Алексей</i> 58256779
            <br>
            Email: fotolife.school@gmail.com
            <br>
            <br>
            <hr>
            <strong>АДМИНИСТРАЦИЯ ШКОЛЫ НЕ ВЛАДЕЕТ ИНФОРМАЦИЕЙ ПО ЗАКАЗАМ, ДЕНЬГИ И ДОЗАКАЗЫ НЕ ПРИНИМАЕТ, РЕШЕНИЕМ ПРОБЛЕМ НЕ ЗАНИМАЕТСЯ.
            СВЯЖИТЕСЬ, ПОЖАЛУЙСТА, С НАМИ.</strong>
        </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))

    # for item in cart.products.all():
    #     with open(item.content_object.selling_image.path, 'rb') as file:
    #         msgImage = MIMEImage(file.read())
    #         msgImage.add_header('Content-ID', item.content_object.title)
    #         msg.attach(msgImage)

    with smtplib.SMTP(f'{credentials.server}: {credentials.port}') as server:
        server.starttls()
        # Login Credentials for sending the mail
        server.login(msg['From'], password)
        # send the message via the server.
        response = server.sendmail(msg['From'], msg['To'], msg.as_string())

    return response


def recalc_cart(cart):
    cart_data = cart.products.aggregate(models.Sum('services__final_price'), models.Count('id'))
    if cart_data.get('services__final_price__sum'):
        cart.final_price = cart_data['services__final_price__sum']
    else:
        cart.final_price = 0
    cart.total_products = cart_data['id__count']
    cart.save()

def recalc_cart_product(cart_product):
    cp = cart_product.services.aggregate(models.Sum('final_price'))
    if cp.get('final_price__sum'):
        cart_product.final_price = cp['final_price__sum']
    else:
        cart_product.final_price = 0
    cart_product.save()

# def recalc_cart(cart):
#     total_sum = 0
#     for cart_prod in cart.products.all():
#         final_sum = 0
#         for service in cart_prod.services.all():
#             service.final_price = service.qty * service.service.price
#             service.save()
#             final_sum += service.final_price
#         cart_prod.final_price = final_sum
#         total_sum += cart_prod.final_price
#     cart.final_price = total_sum
#     cart.save()


# def recalc_cart(cart):
#
#     cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
#     if cart_data.get('final_price__sum'):
#         cart.final_price = cart_data['final_price__sum']
#     else:
#         cart.final_price = 0
#
#     cart.total_products = cart_data['id__count']
#     cart.save()