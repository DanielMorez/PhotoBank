from mainapp.models import Order

table_map = {
    'портрет малый 10х15': {'price': 5, 'qty': 6, 'detail': 7},
    'портрет средний 15х21': {'price': 8, 'qty': 9, 'detail': 10},
    'портрет большой а4 21х30': {'price': 11, 'qty': 12, 'detail': 13},
    'фото с другом 10х15': {'price': 14, 'qty': 15, 'detail': 16},
    'фото класса большое а4 21х30': {'price': 17, 'qty': 18, 'detail': 19},
    'фото класса малое а5 15х21': {'price': 20, 'qty': 21, 'detail': 22},
    'дигитальное фото (без сжатия)': {'price': 23, 'qty': 24, 'detail': 25}
}


def order2list(obj: Order):
    row = ['', f'{obj.last_name} {obj.first_name}', obj.email, obj.phone, obj.comment,
           # Раздел фотографий
           # Малый портрет 10х15
           # Цена шт | Кол-во | Детали (фото/шт)
           '', '', '',
           # Средний портрет 15х21
           '', '', '',
           # Большой портрет
           '', '', '',
           # С другом 10х15
           '', '', '',
           # Класс А4 21х30
           '', '', '',
           # Класс А5
           '', '', '',
           # Дигитальные
           '', '', '',
           # Почта | Смарт | Адрес | Сумма доставка
           '', '', '', '',
           # Налик | Банк | Цена
           '', '', '=F3*G3+L3*M3+I3*J3+R3*S3+U3*V3+X3*Y3+AD3'
           ]
    for item in obj.cart.related_products.all():
        for service in item.services.all():
            if service.qty:
                work_section = table_map.get(service.service.title.lower())

                if work_section:
                    row[work_section['price']] = float(service.service.price)
                    if row[work_section['qty']] != '':
                        row[work_section['qty']] = row[work_section['qty']] + service.qty
                    else:
                        row[work_section['qty']] = service.qty
                    row[work_section['detail']] = row[work_section['qty']] + f'{service.service.title} ({service.qty} шт), '
    return row
