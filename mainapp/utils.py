import smtplib

from os.path import basename

from django.db import models

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.utils.datetime_safe import datetime

from .model_static import EmailCredentials, ContactInfo


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


def send_mail(addr_to, first_name, last_name, phone, comment, cart, order):

    credentials = EmailCredentials.objects.last()
    contact = ContactInfo.objects.last()
    album = cart.products.last().content_object.album
    # create message object instance
    msg = MIMEMultipart("alternative")

    # setup the parameters of the message
    password = credentials.password
    msg['From'] = credentials.email
    msg['To'] = addr_to
    msg['Subject'] = f"Заказ #{order.id}"

    html = """\
        <!DOCTYPE html>
	<html>
		<head>
			<meta charset="utf-8" />
			<title>Выставленный счет</title>

			<style>
				body {
					font-family: 'Calibri Light', 'Helvetica', Helvetica, Arial, sans-serif;
				}

				.invoice-box {
					max-width: 800px;
					margin: auto;
					padding: 30px;
					border: 1px solid #eee;
					box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
					font-size: 16px;
					line-height: 24px;
					color: #555;
				}

				.invoice-box table {
					width: 100%;
					line-height: inherit;
					text-align: left;
				}

				.invoice-box table td {
					padding: 5px;
					vertical-align: top;
				}

				.invoice-box table tr td:nth-child(2) {
					text-align: right;
				}

				.invoice-box table tr.top table td {
					padding-bottom: 20px;
				}

				.invoice-box table tr.top table td.title {
					font-size: 45px;
					line-height: 45px;
					color: #333;
				}

				.invoice-box table tr.information table td {
					padding-bottom: 40px;
				}

				.invoice-box table tr.heading td {
					background: #eee;
					border-bottom: 1px solid #ddd;
					font-weight: bold;
				}

				.invoice-box table tr.details td {
					padding-bottom: 20px;
				}

				.invoice-box table tr.item td {
					border-bottom: 1px solid #eee;
				}

				.invoice-box table tr.item.last td {
					border-bottom: none;
				}

				.invoice-box table tr.total td:nth-child(2) {
					border-top: 2px solid #eee;
					font-weight: bold;
				}

				@media only screen and (max-width: 600px) {
					.invoice-box table tr.top table td {
						width: 100%;
						display: block;
						text-align: center;
					}

					.invoice-box table tr.information table td {
						width: 100%;
						display: block;
						text-align: center;
					}
				}

				/** RTL **/
				.rtl {
					direction: rtl;
				}

				.rtl table {
					text-align: right;
				}

				.rtl table tr td:nth-child(2) {
					text-align: left;
				}
			</style>
		</head>"""
    html += f"""
		<body>
			<div class="invoice-box">
				<table cellpadding="0" cellspacing="0">
					<tr class="top">
						<td colspan="4">
							<table>
								<tr>
									<td>
										<h1 style="padding-top: 24px;">Школьный фотобанк</h1>
									</td>

									<td style="text-align: right;">
										Выставленный счёт №{order.id}<br />
										{datetime.today().strftime('%d-%m-%Y')}<br />
										Alex Nazarati, {contact.phone}
									</td>
								</tr>
							</table>
						</td>
					</tr>

					<tr class="information">
						<td colspan="4">
							<table>
								<tr>
									<td>
										{contact.company}<br />
										{contact.address}<br />
										{contact.city}, {contact.zip}
									</td>

									<td style='text-align: right;'>
									    {first_name} {last_name}<br />
										{phone}<br />
										{addr_to}
									</td>
								</tr>
							</table>
						</td>
					</tr>

					<tr class="heading">
						<td colspan="4">Альбомы</td>
					</tr>
					<tr class="item">
						<td colspan="4">{album.name}</td>
					</tr>


					<tr class="heading">
						<td>Название</td>
						<td style="text-align: left;">Формат</td>
						<td style="text-align: center;">Цена</td>
						<td style="text-align: right;">Количество</td>
					</tr>
    """
    for item in cart.related_products.all():
        for service in item.services.all():
            if service.qty:
                html += f"""
                <tr class="item">
					<td>{item.content_object.title}</td>
					<td style="text-align: left;">{service.service.title}</td>
					<td style="text-align: center;">€{service.service.price}</td>
					<td style="text-align: right;">{service.qty}</td>
				</tr>
            """

    html += f"""\
                <tr class="total">
					<td></td>
					<td></td>
					<td>Доставка: €{album.ship_price}</td>
					<td style="text-align: right;">Итог: €{cart.total}</td>
				</tr>
			</table>
		</div>
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
