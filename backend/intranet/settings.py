from pathlib import Path
import os
from dotenv import load_dotenv

# === Paths / Base ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Env ===
load_dotenv()  # lee variables desde backend/.env
DEBUG = os.getenv("DEBUG", "True") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

# === Apps ===
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Terceros
    "rest_framework",

    # Apps del proyecto
    "libretas",
]

# === Middleware ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === URLs / WSGI / ASGI ===
ROOT_URLCONF = "intranet.urls"
WSGI_APPLICATION = "intranet.wsgi.application"
ASGI_APPLICATION = "intranet.asgi.application"

# === Templates ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # AppDirectoriesLoader buscará en libretas/templates automáticamente,
        # pero además agregamos la ruta explícita:
        "DIRS": [BASE_DIR / "libretas" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# === Base de Datos (MySQL) ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "intranet"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}

# === Static / Media ===
STATIC_URL = "static/"
# Para servir assets (css, fuentes Inter) desde la app libretas:
STATICFILES_DIRS = [BASE_DIR / "libretas" / "static"]
# Para despliegue (collectstatic):
STATIC_ROOT = BASE_DIR / "staticfiles"

# === Zona horaria / Idioma ===
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

# === Django REST Framework (mínimo) ===
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
}

# === Seguridad opcional (ajusta si usas HTTPS/domino) ===
# CSRF_TRUSTED_ORIGINS = ["https://tudominio.com"]

# === Default PK type ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
