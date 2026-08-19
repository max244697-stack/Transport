const phoneInput = document.getElementById('phone');
if (phoneInput) {
  IMask(phoneInput, {
    mask: '+380(00)000-00-00',
    lazy: false,
    placeholderChar: '_',
  });
}

document.getElementById('phoneCopy')?.addEventListener('click', e => {
    if (window.matchMedia('(pointer: coarse)').matches) return;
    e.preventDefault();
    navigator.clipboard.writeText(e.currentTarget.dataset.phone);
    showToast('Номер скопійовано');
  });

  function showToast(text) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = text;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 1800);
  }

  // Smooth scroll
  document.addEventListener('click', e => {
    const link = e.target.closest('a[href^="#"]');
    if (!link) return;
    const href = link.getAttribute('href');
    // If href corresponds to panel controls, activate tab first
    if (href === '#overview' || href === '#how-to-order' || href === '#pricing' || href === '#coverage' || href === '#fleet' || href === '#residential' || href === '#office' || href === '#materials' || href === '#advantages') {
      // activate About tab and then scroll to the inner anchor
      activateTab('panel-about');
      const target = document.querySelector(href);
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
      return;
    }
    if (href === '#works') {
      activateTab('panel-works');
      const target = document.querySelector(href);
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
      return;
    }
    if (href === '#prices' || href === '#what-we-transport') {
      activateTab('panel-prices');
      const target = document.querySelector(href);
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
      return;
    }
    const target = document.querySelector(href);
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth' });
  });

  // Tabs: activation
  function activateTab(id){
    document.querySelectorAll('.tab-button').forEach(b=>{ b.classList.toggle('active', b.dataset.target===id); b.setAttribute('aria-selected', b.dataset.target===id) });
    document.querySelectorAll('.tab-panel').forEach(p=> p.classList.toggle('active', p.id===id));
  }

  // Hook tab buttons
  document.querySelectorAll('.tab-button').forEach(b=> b.addEventListener('click', e=>{ activateTab(b.dataset.target); window.scrollTo({top: document.querySelector('.tabs').offsetTop-16, behavior:'smooth'}) }));

  // Order modal
  const orderModal = document.getElementById('order-modal');
  const orderForm = document.getElementById('order-form');
  let lastFocusedElement = null;

  let addressPickers = [];

  function openOrderModal() {
    if (!orderModal || !orderForm) return;
    lastFocusedElement = document.activeElement;
    orderModal.classList.add('open');
    orderModal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
    const firstField = orderForm.querySelector('input, select, textarea, button');
    firstField?.focus();
    const dateInput = orderForm.querySelector('[name="scheduled_date"]');
    if (dateInput) {
      const now = new Date();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      dateInput.min = `${now.getFullYear()}-${month}-${day}`;
    }
    requestAnimationFrame(() => {
      ensureAddressMaps().then((pickers) => {
        pickers.forEach((picker) => picker.invalidate());
      });
    });
  }

  function closeOrderModal() {
    if (!orderModal) return;
    orderModal.classList.remove('open');
    orderModal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
    lastFocusedElement?.focus();
  }

  document.querySelectorAll('[data-open-order]').forEach((btn) => {
    btn.addEventListener('click', openOrderModal);
  });

  orderModal?.querySelectorAll('[data-close-modal]').forEach(el => {
    el.addEventListener('click', closeOrderModal);
  });

  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (photoLightbox && !photoLightbox.hidden) {
      closePhotoLightbox();
      return;
    }
    const openSuggest = document.querySelector('.address-suggest:not([hidden])');
    if (openSuggest) {
      openSuggest.hidden = true;
      return;
    }
    if (orderModal?.classList.contains('open')) {
      closeOrderModal();
    }
  });

  const photoLightbox = document.getElementById('photo-lightbox');
  const photoLightboxImage = photoLightbox?.querySelector('.photo-lightbox-image');

  function openPhotoLightbox(src, alt) {
    if (!photoLightbox || !photoLightboxImage) return;
    photoLightboxImage.src = src;
    photoLightboxImage.alt = alt || 'Виконане замовлення';
    photoLightbox.hidden = false;
    document.body.classList.add('modal-open');
    photoLightbox.querySelector('[data-close-photo]')?.focus();
  }

  function closePhotoLightbox() {
    if (!photoLightbox || !photoLightboxImage) return;
    photoLightbox.hidden = true;
    photoLightboxImage.src = '';
    if (!orderModal.classList.contains('open')) {
      document.body.classList.remove('modal-open');
    }
  }

  document.addEventListener('click', (event) => {
    const link = event.target.closest('.works-link');
    if (!link) return;
    event.preventDefault();
    const img = link.querySelector('img');
    openPhotoLightbox(link.dataset.full || img?.src, img?.alt);
  });

  photoLightbox?.querySelector('[data-close-photo]')?.addEventListener('click', closePhotoLightbox);
  photoLightbox?.addEventListener('click', (event) => {
    if (event.target === photoLightbox || event.target === photoLightboxImage) {
      closePhotoLightbox();
    }
  });

  function setFieldError(field, message) {
    field.classList.add('is-invalid');
    field.setAttribute('aria-invalid', 'true');
    let error = field.parentElement.querySelector('.field-error');
    if (!error) {
      error = document.createElement('div');
      error.className = 'field-error';
      field.parentElement.appendChild(error);
    }
    error.textContent = message;
  }

  function clearFieldError(field) {
    field.classList.remove('is-invalid');
    field.setAttribute('aria-invalid', 'false');
    const error = field.parentElement.querySelector('.field-error');
    if (error) {
      error.remove();
    }
  }

  function validateForm() {
    let isValid = true;
    const fields = orderForm?.querySelectorAll('input[required], select[required], textarea[required]') || [];

    fields.forEach(field => {
      clearFieldError(field);
      const value = field.value.trim();

      if (!value) {
        setFieldError(field, 'Це поле обов’язкове');
        isValid = false;
        return;
      }

      if (field.name === 'phone') {
        const digits = value.replace(/\D/g, '');
        if (digits.length < 10) {
          setFieldError(field, 'Введіть номер у форматі 093 420 53 20');
          isValid = false;
        }
      }

      if (field.name === 'from_location' || field.name === 'to_location') {
        if (value.length < 3) {
          setFieldError(field, 'Введіть не менше 3 символів');
          isValid = false;
        }
      }

      if (field.name === 'scheduled_date') {
        const now = new Date();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const today = `${now.getFullYear()}-${month}-${day}`;
        if (value < today) {
          setFieldError(field, 'Дата не може бути в минулому');
          isValid = false;
        }
      }
    });

    const markerFields = [
      { lat: 'from_lat', lng: 'from_lng', location: 'from_location' },
      { lat: 'to_lat', lng: 'to_lng', location: 'to_location' },
    ];

    markerFields.forEach(({ lat, lng, location }) => {
      const locationInput = orderForm.querySelector(`[name="${location}"]`);
      const latValue = parseFloat(orderForm.querySelector(`[name="${lat}"]`)?.value);
      const lngValue = parseFloat(orderForm.querySelector(`[name="${lng}"]`)?.value);
      const mapEl = locationInput?.closest('.form-field')?.querySelector('.order-map');

      if (Number.isFinite(latValue) && Number.isFinite(lngValue)) {
        mapEl?.classList.remove('is-invalid');
        return;
      }

      if (locationInput) {
        setFieldError(locationInput, 'Поставте мітку на карті');
      }
      mapEl?.classList.add('is-invalid');
      isValid = false;
    });

    return isValid;
  }

  orderForm?.querySelectorAll('input, select, textarea').forEach(field => {
    field.addEventListener('input', () => {
      if (field.value.trim()) {
        clearFieldError(field);
      }
    });
    field.addEventListener('change', () => {
      if (field.value.trim()) {
        clearFieldError(field);
      }
    });
  });

  function formatNominatimAddress(address, fallback = '') {
    if (!address) return fallback;
    const street = address.road || address.pedestrian || address.street || address.residential || address.footway;
    const house = address.house_number;
    const place = address.city || address.town || address.village || address.hamlet;
    const suburb = address.suburb || address.neighbourhood;
    const region = address.state;
    const parts = [];
    if (street) {
      parts.push(house ? `${street}, ${house}` : street);
    } else if (address.amenity || address.building) {
      parts.push(address.amenity || address.building);
    }
    if (suburb && suburb !== place) parts.push(suburb);
    if (place) parts.push(place);
    else if (address.municipality) parts.push(address.municipality);
    if (region && region !== place) parts.push(region);
    return parts.join(', ') || fallback;
  }

  function shortAddressLabel(item) {
    const fallback = (item.display_name || '')
      .split(',')
      .map((part) => part.trim())
      .filter((part) => (
        part
        && part !== 'Україна'
        && part !== 'Ukraine'
        && !/^\d{5}$/.test(part)
        && !/громада$/i.test(part)
        && !/район$/i.test(part)
      ))
      .slice(0, 3)
      .join(', ');
    return formatNominatimAddress(item.address, fallback);
  }

  function loadLeaflet() {
    if (window.L) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Leaflet failed to load'));
      document.head.appendChild(script);
    });
  }

  async function ensureAddressMaps() {
    if (addressPickers.length) return addressPickers;
    await loadLeaflet();
    addressPickers = initAddressMaps();
    return addressPickers;
  }

  function initAddressMaps() {
    if (!orderForm || !window.L) return [];

    const start = [50.5486, 30.221];

    const createPicker = ({ mapId, inputName, latName, lngName }) => {
      const mapEl = document.getElementById(mapId);
      const input = orderForm.querySelector(`[name="${inputName}"]`);
      const latInput = orderForm.querySelector(`[name="${latName}"]`);
      const lngInput = orderForm.querySelector(`[name="${lngName}"]`);
      if (!mapEl || !input) return { invalidate() {} };

      const map = window.L.map(mapEl, {
        scrollWheelZoom: false,
        tap: true,
      }).setView(start, 13);
      window.L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap, &copy; CARTO',
      }).addTo(map);

      let marker = null;
      let skipSearch = false;
      let searchTimer = null;
      let searchAbort = null;
      let suggestItems = [];
      let activeIndex = -1;

      const suggest = document.createElement('ul');
      suggest.className = 'address-suggest';
      suggest.hidden = true;
      suggest.setAttribute('role', 'listbox');
      const wrap = document.createElement('div');
      wrap.className = 'address-input-wrap';
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
      wrap.appendChild(suggest);
      input.setAttribute('role', 'combobox');
      input.setAttribute('aria-autocomplete', 'list');
      input.setAttribute('aria-expanded', 'false');

      const setInputValue = (value) => {
        skipSearch = true;
        input.value = value;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        skipSearch = false;
      };

      const hideSuggest = () => {
        suggest.hidden = true;
        suggest.innerHTML = '';
        suggestItems = [];
        activeIndex = -1;
        input.setAttribute('aria-expanded', 'false');
      };

      const highlightSuggest = (index) => {
        activeIndex = index;
        [...suggest.children].forEach((el, i) => {
          el.classList.toggle('is-active', i === index);
        });
      };

      const placeMarker = (latlng, { fly = false } = {}) => {
        if (marker) {
          marker.setLatLng(latlng);
        } else {
          marker = window.L.marker(latlng, { draggable: true }).addTo(map);
          marker.on('dragend', () => setPointFromMap(marker.getLatLng()));
        }
        latInput.value = latlng.lat.toFixed(6);
        lngInput.value = latlng.lng.toFixed(6);
        mapEl.classList.remove('is-invalid');
        clearFieldError(input);
        if (fly) {
          map.setView(latlng, Math.max(map.getZoom(), 16));
        }
      };

      const applySearchResult = (item) => {
        const latlng = { lat: parseFloat(item.lat), lng: parseFloat(item.lon) };
        if (!Number.isFinite(latlng.lat) || !Number.isFinite(latlng.lng)) return;
        placeMarker(latlng, { fly: true });
        setInputValue(shortAddressLabel(item));
        hideSuggest();
      };

      const renderSuggest = (items, emptyText) => {
        suggest.innerHTML = '';
        suggestItems = items;
        activeIndex = items.length === 1 ? 0 : -1;
        if (!items.length) {
          const empty = document.createElement('li');
          empty.className = 'address-suggest-empty';
          empty.textContent = emptyText;
          suggest.appendChild(empty);
        } else {
          items.forEach((item, index) => {
            const option = document.createElement('li');
            option.className = 'address-suggest-item';
            option.setAttribute('role', 'option');
            option.textContent = shortAddressLabel(item);
            option.addEventListener('mousedown', (event) => {
              event.preventDefault();
              applySearchResult(item);
            });
            if (index === activeIndex) option.classList.add('is-active');
            suggest.appendChild(option);
          });
        }
        suggest.hidden = false;
        input.setAttribute('aria-expanded', 'true');
      };

      const searchAddress = async (query) => {
        if (searchAbort) searchAbort.abort();
        searchAbort = new AbortController();
        const params = new URLSearchParams({
          q: query,
          format: 'json',
          addressdetails: '1',
          limit: '6',
          'accept-language': 'uk',
          countrycodes: 'ua',
          viewbox: '29.9,50.75,30.7,50.2',
          bounded: '0',
        });
        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/search?${params}`,
            { signal: searchAbort.signal, headers: { Accept: 'application/json' } },
          );
          if (!response.ok) throw new Error('search failed');
          const results = await response.json();
          if (!Array.isArray(results) || !results.length) {
            renderSuggest([], 'Адресу не знайдено — поставте мітку на карті');
            return;
          }
          if (results.length === 1) {
            applySearchResult(results[0]);
            return;
          }
          renderSuggest(results);
        } catch (error) {
          if (error.name === 'AbortError') return;
          renderSuggest([], 'Не вдалося знайти адресу. Спробуйте ще раз або поставте мітку.');
        }
      };

      const setPointFromMap = async (latlng) => {
        hideSuggest();
        placeMarker(latlng);
        setInputValue('Шукаємо адресу…');
        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${latlng.lat}&lon=${latlng.lng}&format=json&addressdetails=1&accept-language=uk`,
          );
          if (!response.ok) throw new Error('reverse geocode failed');
          const data = await response.json();
          setInputValue(formatNominatimAddress(data.address, data.display_name) || input.value);
        } catch {
          setInputValue(`${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)}`);
        }
      };

      input.addEventListener('input', () => {
        if (skipSearch) return;
        latInput.value = '';
        lngInput.value = '';
        hideSuggest();
        const query = input.value.trim();
        clearTimeout(searchTimer);
        if (query.length < 3) return;
        searchTimer = setTimeout(() => searchAddress(query), 450);
      });

      input.addEventListener('keydown', (event) => {
        if (suggest.hidden || !suggestItems.length) return;
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          highlightSuggest(Math.min(activeIndex + 1, suggestItems.length - 1));
        } else if (event.key === 'ArrowUp') {
          event.preventDefault();
          highlightSuggest(Math.max(activeIndex - 1, 0));
        } else if (event.key === 'Enter' && activeIndex >= 0) {
          event.preventDefault();
          applySearchResult(suggestItems[activeIndex]);
        }
      });

      input.addEventListener('blur', () => {
        setTimeout(hideSuggest, 150);
      });

      map.on('click', (event) => setPointFromMap(event.latlng));

      const savedLat = parseFloat(latInput.value);
      const savedLng = parseFloat(lngInput.value);
      if (Number.isFinite(savedLat) && Number.isFinite(savedLng)) {
        placeMarker({ lat: savedLat, lng: savedLng }, { fly: true });
      }

      return {
        invalidate() {
          setTimeout(() => map.invalidateSize(), 220);
        },
      };
    };

    return [
      createPicker({ mapId: 'map-from', inputName: 'from_location', latName: 'from_lat', lngName: 'from_lng' }),
      createPicker({ mapId: 'map-to', inputName: 'to_location', latName: 'to_lat', lngName: 'to_lng' }),
    ];
  }

  orderForm?.addEventListener('submit', e => {
    e.preventDefault();
    if (!validateForm()) {
      const firstError = orderForm.querySelector('.is-invalid');
      firstError?.focus();
      showToast('Заповніть усі обов’язкові поля правильно');
      return;
    }
    showToast('Дякуємо! Заявку надіслано — передзвонимо.');
    closeOrderModal();
    orderForm.submit();
  });

  if (document.querySelector('.alert-error')) {
    openOrderModal();
  }