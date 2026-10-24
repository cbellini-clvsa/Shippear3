# Plan de Implementación — Plata Clara (Fase 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir y dejar publicada (Render + Neon) la app web Django de educación financiera gratuita para Argentina: aprendizaje (temas/módulos/lecciones + quizzes), glosario, datos de mercado reales con gráficos, herramientas (calculadoras) y ruta de 5 pasos, con login opcional con Google para guardar progreso.

**Architecture:** Un proyecto Django único con apps por responsabilidad (`core`, `cuentas`, `educacion`, `glosario`, `quizzes`, `mercado`, `herramientas`). Plantillas server-side + JS liviano (nada de SPA). Datos de mercado traídos de APIs públicas y cacheados en un snapshot en base. Deploy en Render (web) + Neon (PostgreSQL). Desarrollo con SQLite.

**Tech Stack:** Python 3.12, Django 5.1, django-allauth (Google OAuth), requests, dj-database-url, psycopg[binary], gunicorn, whitenoise, Lightweight Charts (TradingView, vía CDN). Tests con pytest-django.

**Spec:** `docs/specs/2026-10-24-fase1-diseno.md` (leer junto con `docs/specs/2026-10-24-ideas-asesoria-integracion.md`).

**Material de referencia ya existente en el repo (se porta, no se reinventa):**
- `docs/mockups/index.html` — maqueta funcional completa: markup, CSS (tokens, dark mode), y JS (navegación, quiz, glosario, mercado + gráficos de velas/línea, calculadoras, ruta, login simulado). **Es la fuente de verdad del diseño y del front.**
- `content/glosario.json` — 8 términos semilla (categorías + definiciones + ejemplos + relacionados).
- `content/ruta.json` — 5 pasos de la ruta.
- `scripts/fetch_mercado_demo.py` — lógica real de fetch + muestreo mensual + agregación de velas OHLC para dólar, indicadores (ArgentinaDatos/datos.gob.ar), acciones y bonos (Yahoo/data912) y crypto (CoinGecko). **Es la fuente de verdad del fetcher de mercado.**

## Global Constraints

- **Lenguaje de la app:** español rioplatense, registro llano ("vos"). Copiar el tono de la maqueta.
- **Encuadre responsable (spec §2):** todo contenido es educativo/informativo, **no** asesoramiento de inversión personalizado. Las secciones de inversión, el mercado, las calculadoras y (a futuro) cualquier perfil llevan el aviso: *"Contenido educativo. No es asesoramiento de inversión; no reemplaza la consulta con un profesional."* Los datos legales/impositivos (fases futuras) llevan fuente + fecha.
- **Datos de mercado:** cada valor se muestra con su **fecha/hora de actualización**; ante fallo de una API se muestra el **último valor conocido**, nunca un error crudo.
- **Privacidad:** sin login no se recolecta nada (progreso en `localStorage`). Con Google solo se guardan nombre/email/foto + progreso. **No** se almacenan contraseñas.
- **Secretos fuera del repo:** `SECRET_KEY`, credenciales de Google OAuth y URL de la base van por **variables de entorno**. `.env` está en `.gitignore`; existe `.env.example` sin valores reales.
- **Config por entorno:** `DEBUG=True` + SQLite en desarrollo; `DEBUG=False` + PostgreSQL (Neon) en producción, vía `DATABASE_URL`.
- **Versiones:** fijar Django 5.1.x y Python 3.12. No usar paquetes sin fijar versión.
- **Commits frecuentes:** un commit por tarea como mínimo (los pasos lo indican).

---

## Estructura de archivos

```
finanzas-app/
├── manage.py
├── requirements.txt
├── .env.example                 # plantilla de variables (sin secretos)
├── render.yaml                  # infra Render (web service)
├── Procfile                     # gunicorn (alternativa a render.yaml)
├── config/
│   ├── __init__.py
│   ├── settings.py              # settings por entorno (lee os.environ)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/                        # home, páginas estáticas, base template, disclaimer
│   ├── views.py  urls.py  templates/core/{base,home,acerca,aviso_legal}.html
├── cuentas/                     # allauth Google + progreso del usuario + "Mis avances"
│   ├── models.py  views.py  urls.py  admin.py  templates/cuentas/avances.html
├── educacion/                   # Tema → Modulo → Leccion
│   ├── models.py  views.py  urls.py  admin.py  managers.py  templates/educacion/*.html
├── glosario/                    # Termino + búsqueda + seed
│   ├── models.py  views.py  urls.py  admin.py  templates/glosario/glosario.html
│   └── management/commands/seed_glosario.py
├── quizzes/                     # Quiz/Pregunta/Opcion + scoring
│   ├── models.py  views.py  urls.py  admin.py  templates/quizzes/*.html
├── mercado/                     # fetch + snapshot + grupos/detalle + gráficos
│   ├── models.py  services.py  views.py  urls.py  templates/mercado/*.html
│   └── management/commands/refresh_mercado.py
├── herramientas/                # calculadoras (JS cliente) + ruta de 5 pasos
│   ├── views.py  urls.py  templates/herramientas/{herramientas,ruta}.html
│   └── management/commands/seed_ruta.py
├── static/                      # css/app.css, js/*.js (portados de la maqueta)
├── templates/                   # (si se usa carpeta global; si no, por app)
├── content/                     # glosario.json, ruta.json (ya existen)
├── docs/
└── tests/  o  <app>/tests.py    # pytest-django
```

---

## Task 1: Scaffolding del proyecto y settings por entorno

**Files:**
- Create: `requirements.txt`, `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`, `.env.example`, `pytest.ini`
- Create: `core/__init__.py`, `core/apps.py`, `core/views.py`, `core/urls.py`
- Test: `core/tests.py`

**Interfaces:**
- Produces: proyecto Django ejecutable (`python manage.py runserver`), `config.settings` que lee `os.environ` (`SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`), y una vista `core:home` montada en `/`.

- [ ] **Step 1: Crear el entorno y requirements**

`requirements.txt`:
```
Django==5.1.6
django-allauth==65.4.1
requests==2.32.3
dj-database-url==2.3.0
psycopg[binary]==3.2.4
gunicorn==23.0.0
whitenoise==6.8.2
python-dotenv==1.0.1
pytest==8.3.4
pytest-django==4.9.0
```

Run:
```bash
cd C:/finanzas-app
py -m venv .venv
.venv/Scripts/pip install -r requirements.txt
```

- [ ] **Step 2: Generar el esqueleto Django**

Run:
```bash
.venv/Scripts/django-admin startproject config .
.venv/Scripts/python manage.py startapp core
```

- [ ] **Step 3: Escribir `config/settings.py` por entorno**

```python
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth", "allauth.account", "allauth.socialaccount", "allauth.socialaccount.providers.google",
    "core", "cuentas", "educacion", "glosario", "quizzes", "mercado", "herramientas",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": dj_database_url.config(
    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}", conn_max_age=600)}

AUTH_PASSWORD_VALIDATORS = []  # no usamos login con contraseña (solo Google)
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {"staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# sites / allauth
SITE_ID = 1
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend",
                           "allauth.account.auth_backends.AuthenticationBackend"]
LOGIN_REDIRECT_URL = "/mis-avances/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
SOCIALACCOUNT_PROVIDERS = {"google": {
    "APP": {"client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""), "key": ""},
    "SCOPE": ["profile", "email"], "AUTH_PARAMS": {"access_type": "online"}}}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

- [ ] **Step 4: `.env.example` (sin secretos reales)**

```
SECRET_KEY=generar-con-get_random_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

- [ ] **Step 5: `pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py
```

- [ ] **Step 6: Vista home mínima + URLs**

`core/views.py`:
```python
from django.shortcuts import render

def home(request):
    return render(request, "core/home.html")
```
`core/urls.py`:
```python
from django.urls import path
from . import views
app_name = "core"
urlpatterns = [path("", views.home, name="home")]
```
`config/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("core.urls")),
]
```
`core/templates/core/home.html` (provisorio, se reemplaza en Task 2):
```html
<!doctype html><html lang="es-ar"><head><meta charset="utf-8"><title>Plata Clara</title></head>
<body><h1>Plata Clara</h1></body></html>
```

- [ ] **Step 7: Escribir el test de humo**

`core/tests.py`:
```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_home_200(client):
    resp = client.get(reverse("core:home"))
    assert resp.status_code == 200
    assert b"Plata Clara" in resp.content
```

- [ ] **Step 8: Migrar y correr el test**

Run:
```bash
.venv/Scripts/python manage.py migrate
.venv/Scripts/pytest core/tests.py -v
```
Expected: migraciones OK y test PASS.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: scaffolding Django + settings por entorno + home de humo"
```

---

## Task 2: App `core` — base template, home real, páginas estáticas y disclaimer

**Files:**
- Create: `core/templates/core/base.html`, `core/home.html`, `core/acerca.html`, `core/aviso_legal.html`
- Create: `static/css/app.css`
- Modify: `core/views.py`, `core/urls.py`
- Test: `core/tests.py`

**Interfaces:**
- Produces: `base.html` con `{% block content %}`, header con nav (Inicio, Aprender, Mercado hoy, Herramientas, Glosario, Mis avances), footer con disclaimer, toggle de tema; vistas `core:home`, `core:acerca`, `core:aviso_legal`.

- [ ] **Step 1: Test de las páginas**

`core/tests.py` (agregar):
```python
@pytest.mark.django_db
def test_acerca_y_aviso(client):
    from django.urls import reverse
    assert client.get(reverse("core:acerca")).status_code == 200
    r = client.get(reverse("core:aviso_legal"))
    assert r.status_code == 200
    assert b"No es asesoramiento" in r.content  # disclaimer presente
```

- [ ] **Step 2: Correr y ver fallar** — `pytest core/tests.py -v` → FAIL (urls faltantes).

- [ ] **Step 3: `base.html` portando el layout de la maqueta**

Portar de `docs/mockups/index.html`: el `<style>` completo (tokens de color, dark mode de 3 bloques, header `.topbar`, footer, utilidades) a `static/css/app.css` (quitando lo específico de secciones que irán a sus apps, o dejándolo todo: es un solo CSS). El `base.html` incluye `<link rel="stylesheet" href="{% static 'css/app.css' %}">`, el link de Google Fonts, el header con la nav (links Django `{% url %}`), el footer con el disclaimer (copiar el texto del `<footer>` de la maqueta), el toggle de tema (portar el JS de tema a `static/js/base.js`), y `{% block content %}{% endblock %}`. La nav marca activo con una variable de contexto `active` por página.

- [ ] **Step 4: home real**

`core/home.html` extiende `base.html` y porta el `<section id="inicio">` de la maqueta (hero, chips, tarjeta de progreso/login, tira "Mercado hoy", grilla "Explorá por tema"). Las partes dinámicas (tira de mercado real, grilla de temas) quedan como include vacío/placeholder hasta Task 4/Task 10; de momento, markup estático con texto real.

- [ ] **Step 5: páginas y views**

`core/views.py`: agregar `acerca` y `aviso_legal` (render de sus templates, pasando `active`). `core/urls.py`: `path("acerca/", ...)`, `path("aviso-legal/", ...)`. El disclaimer vive en `base.html` (footer) y expandido en `aviso_legal.html`.

- [ ] **Step 6: Correr tests** — `pytest core/tests.py -v` → PASS.

- [ ] **Step 7: Verificar a ojo** — `python manage.py runserver`, abrir `http://127.0.0.1:8000/`, ver la home con estilos y el toggle de tema.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat(core): base template, home, paginas estaticas y disclaimer (portado de la maqueta)"
```

---

## Task 3: App `educacion` — modelos Tema/Modulo/Leccion + admin

**Files:**
- Create: `educacion/models.py`, `educacion/managers.py`, `educacion/admin.py`
- Test: `educacion/tests.py`

**Interfaces:**
- Produces: modelos `Tema`, `Modulo`, `Leccion` con `slug`, `orden`, `publicado`; manager `publicados()`; relaciones FK Tema→Modulo→Leccion; admin registrado.

- [ ] **Step 1: Test de modelos**

`educacion/tests.py`:
```python
import pytest
from educacion.models import Tema, Modulo, Leccion

@pytest.mark.django_db
def test_jerarquia_y_publicados():
    t = Tema.objects.create(nombre="Acciones", slug="acciones", orden=1)
    m = Modulo.objects.create(tema=t, titulo="¿Qué es una acción?", slug="que-es", nivel="principiante", orden=1, publicado=True)
    Leccion.objects.create(modulo=m, titulo="Ser dueño", slug="ser-dueno", contenido="...", orden=1, publicado=True)
    oculta = Leccion.objects.create(modulo=m, titulo="Borrador", slug="draft", contenido="...", orden=2, publicado=False)
    assert str(t) == "Acciones"
    assert m.lecciones.count() == 2
    assert Leccion.publicados.count() == 1
    assert oculta not in Leccion.publicados.all()
```

- [ ] **Step 2: Correr y ver fallar** — `pytest educacion/tests.py -v` → FAIL (modelos no existen).

- [ ] **Step 3: Implementar modelos + manager**

`educacion/managers.py`:
```python
from django.db import models
class PublicadosManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(publicado=True)
```
`educacion/models.py`:
```python
from django.db import models
from .managers import PublicadosManager

NIVELES = [("principiante","Principiante"),("intermedio","Intermedio"),("avanzado","Avanzado")]

class Tema(models.Model):
    nombre = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    color = models.CharField(max_length=32, default="#0E9F77")
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)
    objects = models.Manager(); publicados = PublicadosManager()
    class Meta: ordering = ["orden"]
    def __str__(self): return self.nombre

class Modulo(models.Model):
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name="modulos")
    titulo = models.CharField(max_length=160); slug = models.SlugField()
    nivel = models.CharField(max_length=20, choices=NIVELES, default="principiante")
    resumen = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)
    objects = models.Manager(); publicados = PublicadosManager()
    class Meta: ordering = ["orden"]; unique_together = [("tema","slug")]
    def __str__(self): return self.titulo

class Leccion(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="lecciones")
    titulo = models.CharField(max_length=160); slug = models.SlugField()
    contenido = models.TextField()
    minutos = models.PositiveIntegerField(default=5)
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)
    objects = models.Manager(); publicados = PublicadosManager()
    class Meta: ordering = ["orden"]; unique_together = [("modulo","slug")]
    def __str__(self): return self.titulo
```

- [ ] **Step 4: Admin**

`educacion/admin.py`:
```python
from django.contrib import admin
from .models import Tema, Modulo, Leccion
@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ("nombre","orden","publicado"); prepopulated_fields = {"slug": ("nombre",)}
@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("titulo","tema","nivel","orden","publicado"); list_filter = ("tema","nivel","publicado"); prepopulated_fields = {"slug": ("titulo",)}
@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ("titulo","modulo","orden","publicado"); list_filter = ("modulo","publicado"); prepopulated_fields = {"slug": ("titulo",)}
```

- [ ] **Step 5: Migraciones + test**

Run:
```bash
.venv/Scripts/python manage.py makemigrations educacion
.venv/Scripts/python manage.py migrate
.venv/Scripts/pytest educacion/tests.py -v
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(educacion): modelos Tema/Modulo/Leccion + manager publicados + admin"
```

---

## Task 4: App `educacion` — vistas y plantillas (temario, módulo, lección) + grilla de temas en home

**Files:**
- Create: `educacion/views.py`, `educacion/urls.py`, `educacion/templates/educacion/{temario,tema,leccion}.html`
- Modify: `config/urls.py` (incluir `educacion.urls` bajo `aprender/`), `core/home.html` (grilla de temas real)
- Test: `educacion/tests.py`

**Interfaces:**
- Consumes: modelos de Task 3.
- Produces: `educacion:temario` (`/aprender/`), `educacion:tema` (`/aprender/<slug>/`), `educacion:leccion` (`/aprender/<tema>/<modulo>/<leccion>/`). Context: solo objetos `publicado=True`.

- [ ] **Step 1: Test de vistas (publicado se respeta)**

```python
@pytest.mark.django_db
def test_temario_oculta_no_publicados(client):
    from django.urls import reverse
    Tema.objects.create(nombre="Visible", slug="visible", orden=1, publicado=True)
    Tema.objects.create(nombre="Oculto", slug="oculto", orden=2, publicado=False)
    html = client.get(reverse("educacion:temario")).content
    assert b"Visible" in html and b"Oculto" not in html
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Vistas + urls**

`educacion/views.py`: `temario` (lista `Tema.publicados` + banner "Renta fija vs variable" y la Ruta — la Ruta se incluye vía `{% include %}` del template de `herramientas` en Task 11), `tema` (módulos+lecciones del tema), `leccion` (detalle). Usar `get_object_or_404(Tema.publicados, slug=...)`. Portar el markup de la sección Aprender de la maqueta (índice agrupado y la ficha de lección) a estos templates, reemplazando el contenido JS embebido por bucles `{% for %}` sobre los modelos.

- [ ] **Step 4: Grilla de temas en la home**

`core/home.html`: reemplazar la grilla estática por `{% for tema in temas %}` (pasar `temas=Tema.publicados.all()` desde `core.views.home`), cada tarjeta enlaza a `educacion:tema`.

- [ ] **Step 5: Correr tests** → PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(educacion): temario, tema y leccion + grilla de temas en home"
```

---

## Task 5: App `glosario` — modelo + búsqueda + seed desde content/glosario.json

**Files:**
- Create: `glosario/models.py`, `glosario/admin.py`, `glosario/views.py`, `glosario/urls.py`, `glosario/templates/glosario/glosario.html`, `glosario/management/commands/seed_glosario.py`
- Test: `glosario/tests.py`

**Interfaces:**
- Produces: modelo `Termino(palabra, slug, categoria, definicion, ejemplo, relacionados M2M self, publicado)`; vista `glosario:index` con filtro `?q=`; comando `seed_glosario`.

- [ ] **Step 1: Test de modelo + búsqueda**

```python
import pytest
from glosario.models import Termino

@pytest.mark.django_db
def test_busqueda_glosario(client):
    from django.urls import reverse
    Termino.objects.create(palabra="UVA", slug="uva", categoria="macro", definicion="unidad...", publicado=True)
    Termino.objects.create(palabra="Acción", slug="accion", categoria="inversiones", definicion="parte de empresa", publicado=True)
    html = client.get(reverse("glosario:index") + "?q=uva").content
    assert b"UVA" in html and b"Acci" not in html
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Modelo + admin**

```python
from django.db import models
class Termino(models.Model):
    palabra = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    categoria = models.CharField(max_length=40, blank=True)
    definicion = models.TextField()
    ejemplo = models.TextField(blank=True)
    relacionados = models.ManyToManyField("self", blank=True, symmetrical=True)
    publicado = models.BooleanField(default=True)
    class Meta: ordering = ["palabra"]
    def __str__(self): return self.palabra
```
Admin con `search_fields=("palabra","definicion")`, `prepopulated_fields={"slug":("palabra",)}`.

- [ ] **Step 4: Vista con búsqueda**

```python
from django.shortcuts import render
from .models import Termino
def index(request):
    q = request.GET.get("q", "").strip()
    qs = Termino.objects.filter(publicado=True)
    if q:
        qs = qs.filter(models.Q(palabra__icontains=q) | models.Q(definicion__icontains=q))
    return render(request, "glosario/glosario.html", {"terminos": qs, "q": q, "active": "glosario"})
```
(importar `from django.db import models`). Template: portar la grilla de tarjetas del glosario de la maqueta; el input de búsqueda hace GET a la misma URL (y, opcional, filtrado en vivo con el JS de la maqueta portado a `static/js`).

- [ ] **Step 5: Comando seed**

`seed_glosario.py`: leer `content/glosario.json`, `update_or_create` por `slug` (palabra, categoria, definicion, ejemplo, publicado), y en una segunda pasada resolver `relacionados` por slug. Idempotente.

- [ ] **Step 6: Migrar, correr test y seed**

```bash
.venv/Scripts/python manage.py makemigrations glosario && .venv/Scripts/python manage.py migrate
.venv/Scripts/pytest glosario/tests.py -v
.venv/Scripts/python manage.py seed_glosario
```

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat(glosario): modelo + busqueda + seed desde content/glosario.json"
```

---

## Task 6: App `quizzes` — modelos + corrección (scoring)

**Files:**
- Create: `quizzes/models.py`, `quizzes/admin.py`, `quizzes/views.py`, `quizzes/urls.py`, `quizzes/templates/quizzes/quiz.html`
- Test: `quizzes/tests.py`

**Interfaces:**
- Produces: `Quiz(titulo, modulo FK opcional, publicado)`, `Pregunta(quiz FK, enunciado, explicacion, orden)`, `Opcion(pregunta FK, texto, es_correcta)`; endpoint `quizzes:responder` (POST) que devuelve JSON `{correctas, total, detalle:[{pregunta_id, ok, explicacion}]}`.

- [ ] **Step 1: Test de scoring**

```python
import pytest, json
from quizzes.models import Quiz, Pregunta, Opcion

@pytest.mark.django_db
def test_scoring(client):
    from django.urls import reverse
    q = Quiz.objects.create(titulo="T", publicado=True)
    p = Pregunta.objects.create(quiz=q, enunciado="¿?", explicacion="porque sí", orden=1)
    ok = Opcion.objects.create(pregunta=p, texto="correcta", es_correcta=True)
    Opcion.objects.create(pregunta=p, texto="mala", es_correcta=False)
    resp = client.post(reverse("quizzes:responder", args=[q.id]),
                       data=json.dumps({"respuestas": {str(p.id): ok.id}}),
                       content_type="application/json")
    data = resp.json()
    assert data["correctas"] == 1 and data["total"] == 1
    assert data["detalle"][0]["ok"] is True
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Modelos + admin** (con `TabularInline` de Opcion dentro de Pregunta, y Pregunta dentro de Quiz).

- [ ] **Step 4: Endpoint de corrección**

```python
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Quiz, Opcion

@require_POST
def responder(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id, publicado=True)
    enviadas = json.loads(request.body or "{}").get("respuestas", {})
    detalle, correctas = [], 0
    for p in quiz.preguntas.all():
        elegida = enviadas.get(str(p.id))
        ok = Opcion.objects.filter(id=elegida, pregunta=p, es_correcta=True).exists()
        correctas += 1 if ok else 0
        detalle.append({"pregunta_id": p.id, "ok": ok, "explicacion": p.explicacion})
    return JsonResponse({"correctas": correctas, "total": quiz.preguntas.count(), "detalle": detalle})
```
Template `quiz.html`: portar el markup del quiz de la maqueta; el JS envía las respuestas por `fetch` (con CSRF token) a `quizzes:responder` y pinta el feedback.

- [ ] **Step 5: Migrar + test** → PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(quizzes): modelos + endpoint de correccion con feedback"
```

---

## Task 7: App `cuentas` — login con Google (allauth) y página "Mis avances"

**Files:**
- Create: `cuentas/views.py`, `cuentas/urls.py`, `cuentas/templates/cuentas/avances.html`
- Modify: `config/urls.py`
- Test: `cuentas/tests.py`

**Interfaces:**
- Consumes: settings de allauth de Task 1.
- Produces: vista `cuentas:avances` (`/mis-avances/`) que, sin sesión, muestra el estado "logueate con Google" y, con sesión, el panel de avances; botón "Entrar con Google" apunta a `{% provider_login_url 'google' %}`.

- [ ] **Step 1: Test de acceso**

```python
import pytest
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_avances_anon_y_logueado(client):
    from django.urls import reverse
    r = client.get(reverse("cuentas:avances"))
    assert r.status_code == 200
    assert b"con Google" in r.content           # estado deslogueado
    u = User.objects.create_user("maria", "maria@gmail.com", "x")
    client.force_login(u)
    r2 = client.get(reverse("cuentas:avances"))
    assert b"Mis avances" in r2.content          # panel logueado
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Vista + template**

`cuentas/views.py`: `avances(request)` renderiza `avances.html`; el template usa `{% if user.is_authenticated %}` para alternar entre el estado bloqueado (portar el `#avancesLocked` de la maqueta, con el botón Google real) y el panel (portar `#avancesDash`, con datos reales en Task 8). El botón usa `{% load socialaccount %}{% provider_login_url 'google' %}`.

- [ ] **Step 4: Crear el SocialApp de Google desde settings**

Como el `client_id/secret` vienen por env (settings de Task 1, `SOCIALACCOUNT_PROVIDERS.google.APP`), allauth usa esa app sin fila en el admin. Documentar en `.env.example` que en local se puede dejar vacío (el botón existe pero Google rechaza hasta configurar credenciales de prueba).

- [ ] **Step 5: Correr test** → PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(cuentas): login con Google (allauth) y pagina Mis avances"
```

---

## Task 8: App `cuentas` — progreso del usuario (modelos + endpoints + merge de localStorage)

**Files:**
- Create: `cuentas/models.py`, `static/js/progreso.js`
- Modify: `cuentas/views.py`, `cuentas/urls.py`, `cuentas/admin.py`, `cuentas/templates/cuentas/avances.html`, templates de lección/quiz (marcar completado)
- Test: `cuentas/tests.py`

**Interfaces:**
- Produces: modelos `ProgresoLeccion(user, leccion, fecha)`, `IntentoQuiz(user, quiz, puntaje, fecha)`, `Logro(user, tipo, fecha)`; endpoints `cuentas:marcar_leccion` (POST, login req.), `cuentas:registrar_quiz` (POST), `cuentas:merge` (POST, recibe el estado de localStorage al loguearse). `avances` agrega totales (lecciones completadas, temas empezados, promedio de quizzes, logros).

- [ ] **Step 1: Test de progreso y agregación**

```python
@pytest.mark.django_db
def test_marcar_leccion_y_resumen(client, django_user_model):
    from django.urls import reverse
    from educacion.models import Tema, Modulo, Leccion
    u = django_user_model.objects.create_user("m","m@gmail.com","x"); client.force_login(u)
    t = Tema.objects.create(nombre="A", slug="a"); mo = Modulo.objects.create(tema=t, titulo="M", slug="m")
    le = Leccion.objects.create(modulo=mo, titulo="L", slug="l", contenido="x")
    assert client.post(reverse("cuentas:marcar_leccion", args=[le.id])).status_code == 200
    from cuentas.models import ProgresoLeccion
    assert ProgresoLeccion.objects.filter(user=u, leccion=le).count() == 1
    # idempotente
    client.post(reverse("cuentas:marcar_leccion", args=[le.id]))
    assert ProgresoLeccion.objects.filter(user=u, leccion=le).count() == 1
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Modelos (con `unique_together`) + admin.**

```python
from django.db import models
from django.contrib.auth.models import User
from educacion.models import Leccion
from quizzes.models import Quiz
class ProgresoLeccion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = [("user","leccion")]
class IntentoQuiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    puntaje = models.FloatField()
    fecha = models.DateTimeField(auto_now_add=True)
class Logro(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=60)
    fecha = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = [("user","tipo")]
```

- [ ] **Step 4: Endpoints** `marcar_leccion` (login req., `get_or_create`), `registrar_quiz` (guarda puntaje), `merge` (recibe JSON de localStorage y crea los `ProgresoLeccion`/`IntentoQuiz` faltantes). Todos devuelven JSON.

- [ ] **Step 5: `avances` real** — calcular totales (counts + `Avg('puntaje')`), pasar al template, portar el `#avancesDash` de la maqueta con esos valores + "Sincronizado con tu Google · {{ user.email }}".

- [ ] **Step 6: `static/js/progreso.js`** — portar la lógica de localStorage de la maqueta (guardar lección leída / quiz hecho sin sesión). Al cargar una página con usuario logueado, hacer `fetch` a `cuentas:merge` con el contenido de localStorage una sola vez (flag), y limpiar.

- [ ] **Step 7: Migrar + test** → PASS.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "feat(cuentas): progreso por usuario, endpoints y merge de localStorage"
```

---

## Task 9: App `mercado` — servicio de datos + snapshot en base (portar el fetcher)

**Files:**
- Create: `mercado/models.py`, `mercado/services.py`, `mercado/management/commands/refresh_mercado.py`
- Test: `mercado/tests.py`

**Interfaces:**
- Produces: `MercadoSnapshot(data JSONField, creado)`; `services.build_payload()` (porta `scripts/fetch_mercado_demo.py`: dólar, indicadores del Estado, acciones, bonos, crypto; muestreo mensual + velas OHLC) devolviendo el mismo dict `{generado, grupos}` que ya consume la maqueta; `services.get_mercado()` que devuelve el snapshot si tiene < `MERCADO_TTL_MIN` (30) minutos, si no refetch + guarda, y ante error de red devuelve el último snapshot disponible; funciones puras `monthly_from_series`, `aggregate_candles` testeables.

- [ ] **Step 1: Test de las funciones puras (muestreo y velas)**

```python
from mercado.services import monthly_from_series, aggregate_candles

def test_monthly_sampling():
    serie = [{"fecha":"2026-01-10","valor":"10"},{"fecha":"2026-01-28","valor":"12"},
             {"fecha":"2026-02-05","valor":"20"}]
    out = monthly_from_series(serie, "fecha", "valor")
    assert out == [{"m":"2026-01","v":12.0}, {"m":"2026-02","v":20.0}]  # último valor del mes

def test_aggregate_candles():
    # dos velas de enero -> open=primera, high=max, low=min, close=última
    raw = [[1704067200000, 10, 15, 8, 12], [1704672000000, 12, 20, 11, 18]]  # ene 2026
    out = aggregate_candles(raw)
    assert out[-1]["o"] == 10 and out[-1]["h"] == 20 and out[-1]["l"] == 8 and out[-1]["c"] == 18
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Implementar `services.py`** — portar `scripts/fetch_mercado_demo.py` (usar `requests` en vez de `urllib`), exponer `monthly_from_series`, `aggregate_candles`, `build_payload`. Las URLs y la selección de instrumentos son las del script (ya validadas). `get_mercado()` y `MercadoSnapshot` manejan el cacheo/resiliencia.

```python
# bosquejo de get_mercado
from django.utils import timezone
from datetime import timedelta
from .models import MercadoSnapshot
MERCADO_TTL = timedelta(minutes=30)
def get_mercado():
    snap = MercadoSnapshot.objects.order_by("-creado").first()
    if snap and timezone.now() - snap.creado < MERCADO_TTL:
        return snap.data
    try:
        data = build_payload()
        snap = MercadoSnapshot.objects.create(data=data)
        return data
    except Exception:
        return snap.data if snap else {"generado": None, "grupos": {}}
```

- [ ] **Step 4: Comando `refresh_mercado`** — llama `build_payload()` y crea un `MercadoSnapshot` (para precalentar; se puede correr en el deploy o manual).

- [ ] **Step 5: Migrar + test** (solo las funciones puras; no pegar a la red en tests) → PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(mercado): servicio de datos (portado del fetcher) + snapshot en base + tests de muestreo/velas"
```

---

## Task 10: App `mercado` — vistas (grupos + detalle con gráfico)

**Files:**
- Create: `mercado/views.py`, `mercado/urls.py`, `mercado/templates/mercado/{index,detalle}.html`
- Modify: `core/home.html` (tira "Mercado hoy" real)
- Test: `mercado/tests.py`

**Interfaces:**
- Consumes: `services.get_mercado()`.
- Produces: `mercado:index` (grupos) y `mercado:detalle` (`/mercado/<key>/`) con el histórico/velas del instrumento; el template de detalle carga Lightweight Charts (CDN) y dibuja velas (crypto/acciones) o línea (dólar/indicadores), igual que la maqueta.

- [ ] **Step 1: Test de vistas con servicio mockeado**

```python
import pytest
from unittest.mock import patch
FAKE = {"generado":"2026-10-24 12:00","grupos":{"Crypto":[{"key":"bitcoin","name":"Bitcoin","val":80000,"unit":"USD","hist":[{"m":"2026-09","v":1},{"m":"2026-10","v":2}],"candles":[{"t":"2026-10-01","o":1,"h":3,"l":1,"c":2}],"src":"CoinGecko"}]}}

@pytest.mark.django_db
@patch("mercado.views.get_mercado", return_value=FAKE)
def test_mercado_index_y_detalle(_m, client):
    from django.urls import reverse
    assert b"Bitcoin" in client.get(reverse("mercado:index")).content
    assert client.get(reverse("mercado:detalle", args=["bitcoin"])).status_code == 200
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Vistas** (`index` arma los grupos; `detalle` busca el instrumento por `key` en el payload y pasa `hist`/`candles` serializados a JSON para el template). Portar el markup de Mercado de la maqueta; el JS de velas/línea (Lightweight Charts + el SVG de línea) va a `static/js/mercado.js`, leyendo los datos desde un `<script type="application/json">` embebido por la vista (no fetch externo).

- [ ] **Step 4: Tira de mercado en home** — `core.views.home` llama `get_mercado()` y pasa unos pocos valores (dólar oficial/blue/MEP, IPC, riesgo) a la tira.

- [ ] **Step 5: Correr tests** → PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(mercado): vistas de grupos y detalle con grafico (velas/linea) + tira en home"
```

---

## Task 11: App `herramientas` — calculadoras + Ruta de 5 pasos

**Files:**
- Create: `herramientas/views.py`, `herramientas/urls.py`, `herramientas/templates/herramientas/{herramientas,ruta.html}`, `static/js/herramientas.js`, `herramientas/management/commands/seed_ruta.py` (opcional si la ruta va a base) o `herramientas/ruta.py` (si va embebida)
- Modify: `educacion/templates/.../temario.html` (incluir la Ruta arriba)
- Test: `herramientas/tests.py`

**Interfaces:**
- Produces: `herramientas:index` (`/herramientas/`) con las 4 calculadoras (interés compuesto, meta de ahorro, fondo de emergencia, 50/30/20) client-side; la Ruta de 5 pasos renderizada desde `content/ruta.json` (cargada en la vista) e incluida en el temario.

- [ ] **Step 1: Test de que la página rinde y trae las calculadoras**

```python
@pytest.mark.django_db
def test_herramientas_rinde(client):
    from django.urls import reverse
    html = client.get(reverse("herramientas:index")).content
    assert b"Interes" in html or b"compuesto" in html
    assert b"50" in html  # 50/30/20
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Vista + templates + JS** — portar la sección Herramientas de la maqueta (markup de las 4 calculadoras) y `recomputeHerramientas()` a `static/js/herramientas.js`. La vista `index` lee `content/ruta.json` para pasar los pasos (o se renderiza en `ruta.html` incluido en el temario). El disclaimer educativo va en la página.

- [ ] **Step 4: Incluir la Ruta en el temario** — `{% include "herramientas/ruta.html" %}` al tope de `educacion/temario.html`, con los 5 pasos y botones "Abrir calculadora" → `herramientas:index`.

- [ ] **Step 5: Correr test** → PASS.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(herramientas): calculadoras client-side + ruta de 5 pasos (portado de la maqueta)"
```

---

## Task 12: Datos semilla iniciales (temas/módulos/lecciones + quizzes)

**Files:**
- Create: `educacion/management/commands/seed_educacion.py` (o fixtures `educacion/fixtures/seed.json` + `quizzes/fixtures/seed.json`)
- Test: `educacion/tests.py`

**Interfaces:**
- Produces: comando `seed_educacion` que carga ~8–10 lecciones de los temas clave (acciones, cripto, dólar, plazo fijo, FCI, bonos, CEDEARs, inflación/IPC, UVA, PBI) y un quiz por módulo, tomando el contenido ya redactado en el objeto `CURSOS` de la maqueta (`docs/mockups/index.html`). Idempotente (`update_or_create` por slug).

- [ ] **Step 1: Test** — correr el comando y verificar counts > 0 de Tema/Leccion/Quiz.

```python
@pytest.mark.django_db
def test_seed_educacion():
    from django.core.management import call_command
    call_command("seed_educacion")
    from educacion.models import Tema, Leccion
    assert Tema.objects.count() >= 8 and Leccion.objects.count() >= 8
```

- [ ] **Step 2: Correr y ver fallar.**

- [ ] **Step 3: Implementar el comando** portando el contenido de `CURSOS` (bloques `¿Qué es?`, `¿Cómo funciona?`, etc.) de la maqueta a Tema/Modulo/Leccion, y las preguntas `quiz` a Quiz/Pregunta/Opcion.

- [ ] **Step 4: Correr test + seed** → PASS.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: comando seed_educacion con el contenido inicial (portado de la maqueta)"
```

---

## Task 13: Suite completa, estilos finales y revisión integral

**Files:**
- Modify: `static/css/app.css` (consolidar todos los estilos de la maqueta), templates (consistencia de nav/active), `core/templates/core/base.html`
- Test: toda la suite

**Interfaces:**
- Produces: la app corriendo end-to-end en local (SQLite) con todo el contenido semilla cargado, dark mode, responsive y navegación consistente.

- [ ] **Step 1: Consolidar CSS/JS** — asegurar que `static/css/app.css` tiene todos los tokens + dark mode + estilos de cada sección (de la maqueta), y que cada template referencia los `static/js/*.js` que usa.
- [ ] **Step 2: Correr toda la suite** — `pytest -v` → todo PASS.
- [ ] **Step 3: Verificación a ojo** — `runserver`, recorrer Inicio, Aprender (ruta + lección + quiz), Mercado (velas), Herramientas, Glosario, y Mis avances (login simulado local o con credenciales de prueba).
- [ ] **Step 4: Cargar todo el seed** — `seed_glosario`, `seed_educacion`, (`seed_ruta` si aplica).
- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: consolidar estilos y pasar la suite completa"
```

---

## Task 14: Deploy a producción (GitHub → Render + Neon + Google OAuth)

**Files:**
- Create: `render.yaml`, `Procfile`, `build.sh`
- Modify: `config/settings.py` (si falta algún ajuste de prod), `.env.example`
- Test: `config/tests.py` (smoke de settings de prod)

**Interfaces:**
- Produces: la app publicada en una URL pública de Render con base PostgreSQL en Neon y login con Google funcionando.

- [ ] **Step 1: Test de settings de producción**

```python
import importlib, os
def test_prod_settings(monkeypatch):
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.setenv("SECRET_KEY", "x")
    monkeypatch.setenv("ALLOWED_HOSTS", "plataclara.onrender.com")
    import config.settings as s; importlib.reload(s)
    assert s.DEBUG is False
    assert "plataclara.onrender.com" in s.ALLOWED_HOSTS
    assert s.SECURE_SSL_REDIRECT is True
```

- [ ] **Step 2: Correr y ver fallar** (si falta algún ajuste) y corregir settings.

- [ ] **Step 3: `build.sh` + `Procfile` + `render.yaml`**

`build.sh`:
```bash
#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```
`Procfile`:
```
web: gunicorn config.wsgi:application
```
`render.yaml`:
```yaml
services:
  - type: web
    name: plataclara
    runtime: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: "3.12.4"
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        sync: false
      - key: CSRF_TRUSTED_ORIGINS
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
```

- [ ] **Step 4: Subir a GitHub** (pasos manuales del usuario)

```bash
git add -A && git commit -m "chore: config de deploy (Render + Neon)"
# crear repo en GitHub y:
git remote add origin https://github.com/<usuario>/plata-clara.git
git push -u origin main
```

- [ ] **Step 5: Neon (manual, en el dashboard de Neon)** — crear proyecto PostgreSQL gratuito, copiar la **connection string** (con `?sslmode=require`) para usarla como `DATABASE_URL` en Render.

- [ ] **Step 6: Render (manual, en el dashboard de Render)** — New → Web Service → conectar el repo de GitHub → Render detecta `render.yaml`. Cargar las env vars: `ALLOWED_HOSTS=plataclara.onrender.com`, `CSRF_TRUSTED_ORIGINS=https://plataclara.onrender.com`, `DATABASE_URL=<cadena de Neon>`. Deploy.

- [ ] **Step 7: Google OAuth (manual, en Google Cloud Console)** — crear credenciales OAuth 2.0 (tipo Web), **Authorized redirect URI** `https://plataclara.onrender.com/accounts/google/login/callback/`, cargar `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` en Render. (El `Site` de Django debe tener el dominio de Render — set en el admin o por `SITE_ID`/data migration.)

- [ ] **Step 8: Post-deploy** — correr (o incluir en `build.sh`) los seeds (`seed_glosario`, `seed_educacion`), crear superusuario (`createsuperuser` vía Render shell) y verificar la URL pública: home, mercado (datos reales), login con Google.

- [ ] **Step 9: Commit final**

```bash
git add -A
git commit -m "chore: deploy a Render + Neon con Google OAuth"
```

---

## Self-review (cobertura vs. spec)

- **Educación (temas/módulos/lecciones):** Tasks 3, 4, 12. ✅
- **Glosario + búsqueda + semilla:** Task 5. ✅
- **Quizzes + feedback:** Task 6, seed en 12. ✅
- **Login con Google + progreso + Mis avances:** Tasks 7, 8. ✅
- **Progreso sin cuenta (localStorage) + merge:** Task 8. ✅
- **Mercado agrupado + histórico + velas:** Tasks 9, 10 (porta `fetch_mercado_demo.py`). ✅
- **Herramientas + Ruta (ideas de asesoría):** Task 11. ✅
- **Encuadre responsable / disclaimers:** Task 2 (footer + aviso legal), reiterado en mercado/herramientas. ✅
- **Admin para cargar contenido:** Tasks 3, 5, 6 (admin registrado). ✅
- **Deploy gratuito (Render + Neon) + OAuth prod:** Task 14. ✅
- **Secretos por env / config por entorno:** Tasks 1, 14. ✅

**Fuera de alcance (fases futuras, NO en este plan):** perfiles laborales ("qué me corresponde"), escáner de deudas (OCR), simulador de deudas, test de perfil de ahorrista, histórico mensual de bonos.
