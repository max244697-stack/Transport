from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from threading import Thread
from functools import lru_cache
from html import escape
import logging
import urllib3

from app.models import Category, Tariff, CompletedOrder, Order
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
from collections import defaultdict


from datetime import datetime
from urllib3.util.retry import Retry
from urllib3.util.timeout import Timeout


logger = logging.getLogger(__name__)

_telegram_http = urllib3.PoolManager(
    timeout=Timeout(connect=5.0, read=15.0),
    retries=Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({'POST'}),
        raise_on_status=False,
    ),
)


def send_telegram_message(text):
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '') or os.getenv('TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '') or os.getenv('TELEGRAM_CHAT_ID', '')

    if not token or not chat_id:
        logger.warning('Telegram notifications are not configured')
        return False

    try:
        response = _telegram_http.request(
            'POST',
            f'https://api.telegram.org/bot{token}/sendMessage',
            body=json.dumps({
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
            }).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
        )
        if response.status != 200:
            logger.warning('Telegram notification failed with status %s: %s', response.status, response.data)
            return False
        logger.info('Telegram notification sent')
        return True
    except Exception as exc:
        logger.exception('Telegram notification error: %s', exc)
        return False


def _coords(lat, lng):
    try:
        return float(lat), float(lng)
    except (TypeError, ValueError):
        return None


def _google_maps_url(lat, lng):
    return f'https://www.google.com/maps?q={lat:.6f},{lng:.6f}'


def _with_maps_link(address, lat, lng):
    point = _coords(lat, lng)
    if not point:
        return address, None
    url = _google_maps_url(*point)
    return f'{address}\n{url}', url


def _telegram_place_line(label, address, maps_url):
    display = (address or '').split('\n', 1)[0]
    line = f'{label} {escape(display)}'
    if maps_url:
        line += f'\n   <a href="{escape(maps_url, quote=True)}">Відкрити в Google Maps</a>'
    return line


def _parse_scheduled_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def _parse_scheduled_time(value):
    if not value:
        return None
    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def send_telegram_async(order, from_maps=None, to_maps=None):
    when = 'не вказано'
    if order.scheduled_date and order.scheduled_time:
        when = f'{order.scheduled_date.strftime("%d.%m.%Y")}, орієнтовно {order.scheduled_time.strftime("%H:%M")}'
    elif order.scheduled_date:
        when = order.scheduled_date.strftime('%d.%m.%Y')

    text = (
        f"<b>🚚 Нове замовлення #{order.pk}</b>\n\n"
        f"📞 Телефон: {escape(order.namber)}\n"
        f"📦 Тип: {escape(order.type)}\n"
        f"🧰 Вантажники: {'так' if order.need_loaders else 'ні'}\n"
        f"📅 Коли: {escape(when)}\n"
        f"{_telegram_place_line('📍 Звідки:', order.adress_from, from_maps)}\n"
        f"{_telegram_place_line('🏁 Куди:', order.adress_to, to_maps)}\n"
        f"🕐 Заявка: {timezone.localtime(order.date).strftime('%d.%m.%Y %H:%M')}"
    )
    Thread(target=send_telegram_message, args=(text,), daemon=True).start()


def _index_context():
    tariff_groups = []
    categories = Category.objects.prefetch_related('tariffs')

    for category in categories:
        items = list(category.tariffs.all())
        if not items:
            continue
        tariff_groups.append({
            'name': category.name,
            'tariffs': items,
            'is_featured': any(item.is_featured for item in items),
        })

    uncategorized = list(Tariff.objects.filter(category__isnull=True))
    if uncategorized:
        tariff_groups.append({
            'name': 'Інші послуги',
            'tariffs': uncategorized,
            'is_featured': any(item.is_featured for item in uncategorized),
        })

    return {
        'tariff_groups': tariff_groups,
        'completed_orders': CompletedOrder.objects.filter(is_published=True),
        'categories': Category.objects.all(),
        'static_v': _static_version(),
    }


def _static_version():
    version = 0
    for relative in ('css/style.css', 'js/main.js'):
        path = settings.BASE_DIR / 'static' / relative
        try:
            version = max(version, int(path.stat().st_mtime))
        except OSError:
            continue
    return version or 1


def index(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        transport_type = request.POST.get('transport_type', '').strip()
        from_location = request.POST.get('from_location', '').strip()
        to_location = request.POST.get('to_location', '').strip()

        errors = []

        if not phone:
            errors.append('Вкажіть номер телефону.')
        else:
            digits = ''.join(ch for ch in phone if ch.isdigit())
            if len(digits) < 10:
                errors.append('Номер телефону має містити не менше 10 цифр.')

        valid_types = set(Category.objects.values_list('name', flat=True))
        if not transport_type:
            errors.append('Оберіть тип перевезення.')
        elif transport_type not in valid_types:
            errors.append('Оберіть тип перевезення зі списку.')

        if len(from_location) < 3:
            errors.append('Поле «Звідки» має містити не менше 3 символів.')
        if not _coords(request.POST.get('from_lat'), request.POST.get('from_lng')):
            errors.append('Поставте мітку на карті «Звідки».')

        if len(to_location) < 3:
            errors.append('Поле «Куди» має містити не менше 3 символів.')
        if not _coords(request.POST.get('to_lat'), request.POST.get('to_lng')):
            errors.append('Поставте мітку на карті «Куди».')

        scheduled_date = _parse_scheduled_date(request.POST.get('scheduled_date', '').strip())
        scheduled_time = _parse_scheduled_time(request.POST.get('scheduled_time', '').strip())
        if not scheduled_date:
            errors.append('Вкажіть бажану дату перевезення.')
        elif scheduled_date < timezone.localdate():
            errors.append('Дата перевезення не може бути в минулому.')
        if not scheduled_time:
            errors.append('Вкажіть орієнтовний час перевезення.')

        need_loaders_raw = request.POST.get('need_loaders', '').strip()
        if need_loaders_raw not in ('yes', 'no'):
            errors.append('Оберіть, чи потрібні вантажники.')
        need_loaders = need_loaders_raw == 'yes'

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'app/index.html', _index_context())

        from_location, from_maps = _with_maps_link(
            from_location,
            request.POST.get('from_lat'),
            request.POST.get('from_lng'),
        )
        to_location, to_maps = _with_maps_link(
            to_location,
            request.POST.get('to_lat'),
            request.POST.get('to_lng'),
        )

        order = Order.objects.create(
            namber=phone,
            type=transport_type,
            adress_from=from_location,
            adress_to=to_location,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            need_loaders=need_loaders,
        )

        send_telegram_async(order, from_maps=from_maps, to_maps=to_maps)

        logger.info(
            'Received form submission: Phone=%s, Transport_type=%s, From_location=%s, To_location=%s',
            phone,
            transport_type,
            from_location,
            to_location,
        )
        messages.success(request, 'Заявку успішно надіслано!')
        return redirect('home')

    return render(request, 'app/index.html', _index_context())
