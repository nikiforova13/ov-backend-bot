from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
OUTPUT_PATH = DOCUMENTS_DIR / "python-backend-roadmap.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 46

NAVY = colors.HexColor("#1A2330")
INK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#5E584F")
PAPER = colors.HexColor("#F4F2EC")
WHITE = colors.white
ACCENT = colors.HexColor("#1E4D3A")
LINE = colors.HexColor("#DDD6CB")
CODE_BG = colors.HexColor("#F7F4EE")

FONT_REGULAR = "GuideRegular"
FONT_BOLD = "GuideBold"
FONT_MONO = "GuideMono"

CONTACT_TEXT = "Привет, интересно узнать про обучение."
CONTACT_URL = f"https://t.me/O_V_backend?text={quote(CONTACT_TEXT)}"


def register_fonts() -> None:
    windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    regular_candidates = (
        windows_fonts / "arial.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    bold_candidates = (
        windows_fonts / "arialbd.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    )
    mono_candidates = (
        windows_fonts / "consola.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    )
    regular = next((path for path in regular_candidates if path.is_file()), None)
    bold = next((path for path in bold_candidates if path.is_file()), None)
    mono = next((path for path in mono_candidates if path.is_file()), None)
    if regular is None or bold is None or mono is None:
        raise FileNotFoundError("Arial, Arial Bold and Consolas or DejaVu are required")

    pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(regular)))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold)))
    pdfmetrics.registerFont(TTFont(FONT_MONO, str(mono)))


def paragraph_style(
    size: float,
    *,
    color: colors.Color = INK,
    leading: float | None = None,
    bold: bool = False,
    align: int = TA_LEFT,
    mono: bool = False,
) -> ParagraphStyle:
    if mono:
        font_name = FONT_MONO
    elif bold:
        font_name = FONT_BOLD
    else:
        font_name = FONT_REGULAR
    return ParagraphStyle(
        name=f"guide-{size}-{bold}-{align}-{mono}",
        fontName=font_name,
        fontSize=size,
        leading=leading or size * 1.35,
        textColor=color,
        alignment=align,
        spaceAfter=0,
    )


def draw_paragraph(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    top: float,
    width: float,
    style: ParagraphStyle,
) -> float:
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(pdf, x, top - height)
    return top - height


def rounded_card(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    fill: colors.Color = WHITE,
    radius: float = 4,
    *,
    stroke: bool = True,
) -> None:
    pdf.setFillColor(fill)
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(1)
    pdf.roundRect(x, y, width, height, radius, stroke=1 if stroke else 0, fill=1)


def page_chrome(pdf: canvas.Canvas, page_number: int, section: str) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(ACCENT)
    pdf.rect(MARGIN, PAGE_HEIGHT - 40, 8, 8, stroke=0, fill=1)
    pdf.setFont(FONT_REGULAR, 8)
    pdf.setFillColor(MUTED)
    pdf.drawString(MARGIN + 14, PAGE_HEIGHT - 38, section)
    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(1)
    pdf.line(MARGIN, PAGE_HEIGHT - 52, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 52)
    pdf.setFont(FONT_REGULAR, 8)
    pdf.setFillColor(MUTED)
    pdf.drawRightString(PAGE_WIDTH - MARGIN, 28, f"O&V BACKEND  {page_number}")


def section_title(pdf: canvas.Canvas, title: str, subtitle: str) -> float:
    top = PAGE_HEIGHT - 78
    top = draw_paragraph(
        pdf,
        title,
        MARGIN,
        top,
        PAGE_WIDTH - 2 * MARGIN,
        paragraph_style(22, bold=True, leading=26),
    )
    top -= 8
    return draw_paragraph(
        pdf,
        subtitle,
        MARGIN,
        top,
        PAGE_WIDTH - 2 * MARGIN,
        paragraph_style(10.5, color=MUTED, leading=15),
    )


def draw_number_badge(pdf: canvas.Canvas, number: str, x: float, y: float) -> None:
    size = 20
    pdf.setFillColor(ACCENT)
    pdf.rect(x - size / 2, y - size / 2, size, size, stroke=0, fill=1)
    pdf.setFillColor(WHITE)
    pdf.setFont(FONT_BOLD, 8)
    pdf.drawCentredString(x, y - 3, number)


def draw_bullet_list(
    pdf: canvas.Canvas,
    items: list[str],
    x: float,
    top: float,
    width: float,
    *,
    text_color: colors.Color = INK,
    size: float = 10,
) -> float:
    style = paragraph_style(size, color=text_color, leading=size * 1.4)
    for item in items:
        pdf.setFillColor(ACCENT)
        pdf.rect(x, top - 8, 5, 5, stroke=0, fill=1)
        top = draw_paragraph(pdf, item, x + 14, top, width - 14, style) - 7
    return top


def draw_request_diagram(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    gap = 16
    left_width = width * 0.58
    right_width = width - left_width - gap
    rounded_card(pdf, x, y, left_width, height, CODE_BG, radius=2)
    rounded_card(pdf, x + left_width + gap, y, right_width, height, CODE_BG, radius=2)

    pdf.setFillColor(ACCENT)
    pdf.rect(x, y, 3, height, stroke=0, fill=1)
    pdf.rect(x + left_width + gap, y, 3, height, stroke=0, fill=1)

    left_text = (
        "POST /tasks<br/>"
        "Authorization: Bearer ...<br/>"
        "Content-Type: application/json<br/><br/>"
        "1. проверить токен<br/>"
        "2. проверить title и deadline<br/>"
        "3. INSERT INTO tasks<br/>"
        "4. вернуть 201 и JSON"
    )
    draw_paragraph(
        pdf,
        left_text,
        x + 16,
        y + height - 16,
        left_width - 28,
        paragraph_style(9, leading=13, mono=True),
    )
    right_text = (
        "201 Created<br/><br/>"
        "{<br/>"
        '&nbsp;&nbsp;"id": 17,<br/>'
        '&nbsp;&nbsp;"title": "..."<br/>'
        "}"
    )
    draw_paragraph(
        pdf,
        right_text,
        x + left_width + gap + 16,
        y + height - 16,
        right_width - 28,
        paragraph_style(9, leading=13, mono=True),
    )
    pdf.setFont(FONT_REGULAR, 8)
    pdf.setFillColor(MUTED)
    pdf.drawString(x + 16, y + 12, "запрос")
    pdf.drawString(x + left_width + gap + 16, y + 12, "ответ")


def draw_step_row(
    pdf: canvas.Canvas,
    steps: list[tuple[str, str, str]],
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    gap = 8
    box_width = (width - gap * (len(steps) - 1)) / len(steps)
    for index, (number, title, caption) in enumerate(steps):
        box_x = x + index * (box_width + gap)
        rounded_card(pdf, box_x, y, box_width, height, WHITE, radius=2)
        pdf.setFillColor(ACCENT)
        pdf.setFont(FONT_BOLD, 8)
        pdf.drawString(box_x + 10, y + height - 18, number)
        pdf.setFillColor(INK)
        pdf.setFont(FONT_BOLD, 11)
        pdf.drawString(box_x + 10, y + height - 38, title)
        draw_paragraph(
            pdf,
            caption,
            box_x + 10,
            y + height - 48,
            box_width - 18,
            paragraph_style(8, color=MUTED, leading=11),
        )
        if index < len(steps) - 1:
            arrow_y = y + height / 2
            pdf.setStrokeColor(ACCENT)
            pdf.setLineWidth(1)
            pdf.line(box_x + box_width, arrow_y, box_x + box_width + gap, arrow_y)


def build_cover(pdf: canvas.Canvas) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(ACCENT)
    pdf.rect(0, PAGE_HEIGHT - 8, PAGE_WIDTH, 8, stroke=0, fill=1)

    pdf.setFont(FONT_BOLD, 9)
    pdf.setFillColor(INK)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 48, "O&V BACKEND")
    pdf.setFont(FONT_REGULAR, 9)
    pdf.setFillColor(MUTED)
    pdf.drawRightString(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 48, "2026")

    draw_paragraph(
        pdf,
        "Гайд по backend<br/>на Python",
        MARGIN,
        PAGE_HEIGHT - 90,
        360,
        paragraph_style(34, bold=True, leading=38),
    )
    draw_paragraph(
        pdf,
        "Что учить и в каком порядке, если нужно дойти до сервиса, "
        "который принимает запросы, пишет в базу и запускается не только у тебя на ноутбуке.",
        MARGIN,
        PAGE_HEIGHT - 190,
        430,
        paragraph_style(12, color=MUTED, leading=17),
    )

    diagram_y = 348
    diagram_height = 172
    draw_request_diagram(pdf, MARGIN, diagram_y, PAGE_WIDTH - 2 * MARGIN, diagram_height)

    facts = (
        ("12 недель", "Черновик плана для вечеров. Срок можно сдвинуть, порядок — лучше нет."),
        (
            "Один стек",
            "Python, PostgreSQL, FastAPI, pytest, Docker. Остальное после первого сервиса.",
        ),
        ("Три репозитория", "Скрипт или бот, API задач, тот же API в контейнере с тестами."),
    )
    top = diagram_y - 28
    for title, body in facts:
        pdf.setFillColor(ACCENT)
        pdf.rect(MARGIN, top - 14, 3, 14, stroke=0, fill=1)
        pdf.setFont(FONT_BOLD, 10)
        pdf.setFillColor(INK)
        pdf.drawString(MARGIN + 14, top - 12, title)
        top = draw_paragraph(
            pdf,
            body,
            MARGIN + 108,
            top,
            PAGE_WIDTH - 2 * MARGIN - 108,
            paragraph_style(10, color=MUTED, leading=14),
        )
        top -= 16

    pdf.setStrokeColor(LINE)
    pdf.setLineWidth(1)
    pdf.line(MARGIN, 52, PAGE_WIDTH - MARGIN, 52)
    pdf.setFont(FONT_REGULAR, 8)
    pdf.setFillColor(MUTED)
    pdf.drawString(MARGIN, 34, "Дальше — темы, проекты и что должно лежать в репозитории.")
    pdf.showPage()


def build_route_page(pdf: canvas.Canvas) -> None:
    page_chrome(pdf, 2, "Порядок")
    top = section_title(
        pdf,
        "Сначала Python и SQL, потом фреймворк",
        "FastAPI на первой неделе прячет функции, ошибки и данные. "
        "Их проще разобрать на обычном скрипте.",
    )
    top -= 22
    draw_step_row(
        pdf,
        [
            ("01", "Python", "функции, файлы, ошибки"),
            ("02", "SQL", "таблицы, JOIN, индекс"),
            ("03", "API", "HTTP, JSON, доступ"),
            ("04", "Тесты", "pytest и логи"),
            ("05", "Запуск", "Docker и сервер"),
        ],
        MARGIN,
        top - 118,
        PAGE_WIDTH - 2 * MARGIN,
        108,
    )
    top -= 146

    notes = (
        (
            "01",
            "Скрипт без фреймворка",
            "Читает файл, говорит, какая строка битая, и не падает всем трейсбеком наружу.",
        ),
        (
            "02",
            "SQL в консоли",
            "SELECT с JOIN пишешь сам. ORM подключаешь, когда запрос уже понятен.",
        ),
        (
            "03",
            "Один API",
            "Регистрация, список, создание, ошибка в одном формате. Не пять туториалов сразу.",
        ),
        (
            "04",
            "Репозиторий сразу",
            "Коммит после рабочей штуки. Сообщение «fix» или «update» не считается.",
        ),
    )
    card_width = (PAGE_WIDTH - 2 * MARGIN - 12) / 2
    card_height = 108
    for index, (number, title, body) in enumerate(notes):
        column = index % 2
        row = index // 2
        x = MARGIN + column * (card_width + 12)
        y = top - card_height - row * (card_height + 12)
        rounded_card(pdf, x, y, card_width, card_height, WHITE, radius=2)
        draw_number_badge(pdf, number, x + 22, y + card_height - 22)
        draw_paragraph(
            pdf,
            title,
            x + 40,
            y + card_height - 14,
            card_width - 54,
            paragraph_style(11, bold=True, leading=14),
        )
        draw_paragraph(
            pdf,
            body,
            x + 16,
            y + card_height - 46,
            card_width - 32,
            paragraph_style(9.5, color=MUTED, leading=13),
        )
    pdf.showPage()


def build_python_page(pdf: canvas.Canvas) -> None:
    page_chrome(pdf, 3, "1. Python")
    top = section_title(
        pdf,
        "Синтаксис, файлы и ошибки",
        "К концу этапа есть программа, которую можно открыть через неделю "
        "и понять, где данные входят и куда уходят.",
    )
    top -= 18
    column_width = (PAGE_WIDTH - 2 * MARGIN - 14) / 2
    left_height = 320
    left_bottom = top - left_height
    rounded_card(pdf, MARGIN, left_bottom, column_width, left_height, WHITE, radius=2)
    draw_paragraph(
        pdf,
        "Разобрать",
        MARGIN + 16,
        top - 16,
        column_width - 32,
        paragraph_style(14, bold=True),
    )
    draw_bullet_list(
        pdf,
        [
            "Типы, коллекции, условия, циклы",
            "Функции и области видимости",
            "Исключения: что ловить, а что пробрасывать",
            "Классы, когда у данных есть свои правила",
            "Модули, пакеты, venv",
            "Типы у функций, которые вызывают другие",
            "async/await — когда обычные функции уже пишутся без подсказок",
        ],
        MARGIN + 16,
        top - 48,
        column_width - 32,
        size=9.5,
    )

    right_x = MARGIN + column_width + 14
    right_height = 300
    right_bottom = top - right_height
    rounded_card(pdf, right_x, right_bottom, column_width, right_height, WHITE, radius=2)
    draw_paragraph(
        pdf,
        "Написать",
        right_x + 16,
        top - 16,
        column_width - 32,
        paragraph_style(14, bold=True),
    )
    draw_bullet_list(
        pdf,
        [
            "Список задач в консоли, хранение в JSON",
            "Чтение CSV: битые строки печатаются отдельно, скрипт не падает",
            "Бот: /start и одна команда, без базы",
        ],
        right_x + 16,
        top - 48,
        column_width - 32,
        size=9.5,
    )
    box_width = column_width - 28
    box_height = 88
    box_y = right_bottom + 14
    rounded_card(pdf, right_x + 14, box_y, box_width, box_height, NAVY, radius=2, stroke=False)
    draw_paragraph(
        pdf,
        "Можно идти дальше, если",
        right_x + 28,
        box_y + box_height - 14,
        box_width - 28,
        paragraph_style(9, color=colors.HexColor("#D5DDD8"), bold=True),
    )
    draw_paragraph(
        pdf,
        "по трейсбеку находишь строку, а не меняешь код наугад. "
        "Чужой скрипт на сто строк можешь пересказать своими словами.",
        right_x + 28,
        box_y + box_height - 32,
        box_width - 28,
        paragraph_style(9, color=WHITE, leading=12.5),
    )

    tools_y = left_bottom - 84
    rounded_card(pdf, MARGIN, tools_y, PAGE_WIDTH - 2 * MARGIN, 70, WHITE, radius=2)
    draw_paragraph(
        pdf,
        "На компьютере",
        MARGIN + 16,
        tools_y + 54,
        140,
        paragraph_style(11, bold=True),
    )
    draw_paragraph(
        pdf,
        "Git, редактор, venv, pip или uv, ruff, pytest. Docker пока не нужен.",
        MARGIN + 16,
        tools_y + 30,
        PAGE_WIDTH - 2 * MARGIN - 32,
        paragraph_style(10, color=MUTED, leading=14),
    )
    pdf.showPage()


def build_backend_page(pdf: canvas.Canvas) -> None:
    page_chrome(pdf, 4, "2. API")
    top = section_title(
        pdf,
        "Сервер принимает запрос и отдаёт ответ",
        "Между ними проверка данных, правила и запись в базу. "
        "Вот это и есть работа backend.",
    )
    top -= 20
    draw_step_row(
        pdf,
        [
            ("01", "Клиент", "браузер, бот, curl"),
            ("02", "HTTP", "метод, путь, статус"),
            ("03", "Правила", "кто что может"),
            ("04", "База", "PostgreSQL"),
        ],
        MARGIN,
        top - 96,
        PAGE_WIDTH - 2 * MARGIN,
        88,
    )
    top -= 116

    column_width = (PAGE_WIDTH - 2 * MARGIN - 14) / 2
    column_height = 268
    column_bottom = top - column_height
    rounded_card(pdf, MARGIN, column_bottom, column_width, column_height, WHITE, radius=2)
    draw_paragraph(
        pdf,
        "Разобрать",
        MARGIN + 16,
        top - 16,
        column_width - 32,
        paragraph_style(14, bold=True),
    )
    draw_bullet_list(
        pdf,
        [
            "GET, POST, PATCH, DELETE",
            "Коды 200, 201, 400, 401, 404, 500",
            "JSON и проверка тела запроса",
            "Логин и права — разные вещи",
            "Лог, по которому видно упавший запрос",
            "FastAPI. Django — если нужна админка сразу",
        ],
        MARGIN + 16,
        top - 48,
        column_width - 32,
        size=9.5,
    )

    right_x = MARGIN + column_width + 14
    right_height = 250
    right_bottom = top - right_height
    rounded_card(pdf, right_x, right_bottom, column_width, right_height, WHITE, radius=2)
    draw_paragraph(
        pdf,
        "Собрать API задач",
        right_x + 16,
        top - 16,
        column_width - 32,
        paragraph_style(14, bold=True),
    )
    draw_paragraph(
        pdf,
        "POST /register<br/>POST /login<br/>GET /tasks<br/>POST /tasks<br/>PATCH /tasks/{id}",
        right_x + 16,
        top - 46,
        column_width - 32,
        paragraph_style(10, leading=15, mono=True),
    )
    box_width = column_width - 28
    box_height = 72
    box_y = right_bottom + 14
    rounded_card(pdf, right_x + 14, box_y, box_width, box_height, NAVY, radius=2, stroke=False)
    draw_paragraph(
        pdf,
        "В README написано, как запустить. Из /docs создаётся задача. "
        "Запрос без токена возвращает 401, не стек Python.",
        right_x + 28,
        box_y + box_height - 14,
        box_width - 28,
        paragraph_style(9, color=WHITE, leading=12.5),
    )
    pdf.showPage()


def build_quality_page(pdf: canvas.Canvas) -> None:
    page_chrome(pdf, 5, "3. Данные и запуск")
    top = section_title(
        pdf,
        "База, тесты, сервер",
        "API на SQLite в папке проекта ещё нельзя отдать другому человеку. "
        "Нужны нормальная база, проверка сценария и команда запуска.",
    )
    top -= 18
    card_width = (PAGE_WIDTH - 2 * MARGIN - 20) / 3
    cards = (
        (
            "01",
            "База",
            [
                "SELECT, JOIN, индекс",
                "PostgreSQL",
                "SQLAlchemy после SQL",
                "Миграции Alembic",
            ],
        ),
        (
            "02",
            "Проверка",
            [
                "pytest на сценарий и на ошибку",
                "Входные данные до записи",
                "Лог с путём запроса",
                "Секреты не в Git",
            ],
        ),
        (
            "03",
            "Запуск",
            [
                "Процесс и порт",
                "Dockerfile",
                "Переменные окружения",
                "Один прогон в CI",
            ],
        ),
    )
    card_height = 236
    card_bottom = top - card_height
    for index, (number, title, items) in enumerate(cards):
        x = MARGIN + index * (card_width + 10)
        rounded_card(pdf, x, card_bottom, card_width, card_height, WHITE, radius=2)
        draw_number_badge(pdf, number, x + 22, top - 24)
        draw_paragraph(
            pdf,
            title,
            x + 16,
            top - 48,
            card_width - 32,
            paragraph_style(13, bold=True),
        )
        draw_bullet_list(
            pdf,
            items,
            x + 16,
            top - 80,
            card_width - 32,
            size=9,
        )

    project_height = 142
    project_y = card_bottom - 18 - project_height
    rounded_card(
        pdf,
        MARGIN,
        project_y,
        PAGE_WIDTH - 2 * MARGIN,
        project_height,
        NAVY,
        radius=2,
        stroke=False,
    )
    draw_paragraph(
        pdf,
        "Проект",
        MARGIN + 20,
        project_y + project_height - 16,
        80,
        paragraph_style(9, color=colors.HexColor("#D5DDD8"), bold=True),
    )
    draw_paragraph(
        pdf,
        "Запись на слот. Пользователь, время, бронь. Одно время нельзя занять дважды.",
        MARGIN + 20,
        project_y + project_height - 36,
        PAGE_WIDTH - 2 * MARGIN - 40,
        paragraph_style(14, color=WHITE, bold=True, leading=18),
    )
    draw_paragraph(
        pdf,
        "В репозитории PostgreSQL, pytest на успешную бронь и на повтор, "
        "Dockerfile и README с командами. Без этого проект ещё черновик.",
        MARGIN + 20,
        project_y + 48,
        PAGE_WIDTH - 2 * MARGIN - 40,
        paragraph_style(10, color=colors.HexColor("#D7DDE6"), leading=14),
    )
    pdf.showPage()


def build_plan_page(pdf: canvas.Canvas) -> None:
    page_chrome(pdf, 6, "12 недель")
    top = section_title(
        pdf,
        "План, если заниматься по вечерам",
        "Срок сдвигается. Порядок лучше не ломать: к концу недели код должен запускаться.",
    )
    top -= 16
    blocks = (
        ("1–3", "Python", "Список задач в файле. Ошибки в данных не роняют скрипт."),
        ("4–5", "Git и SQL", "Репозиторий и запросы к PostgreSQL, в том числе JOIN."),
        ("6–8", "API", "Регистрация, задачи, /docs, 401 без токена."),
        (
            "9–10",
            "Тесты и Docker",
            "pytest на создание задачи. Контейнер поднимается одной командой.",
        ),
        ("11–12", "Сервис", "Бронь слотов. Другой человек поднимает проект по README."),
    )
    row_height = 78
    row_gap = 8
    for index, (weeks, title, body) in enumerate(blocks):
        y = top - row_height - index * (row_height + row_gap)
        rounded_card(pdf, MARGIN, y, PAGE_WIDTH - 2 * MARGIN, row_height, WHITE, radius=2)
        pdf.setFillColor(ACCENT)
        pdf.rect(MARGIN, y, 4, row_height, stroke=0, fill=1)
        pdf.setFont(FONT_BOLD, 8)
        pdf.setFillColor(ACCENT)
        pdf.drawString(MARGIN + 18, y + row_height - 22, f"НЕДЕЛИ {weeks}")
        draw_paragraph(
            pdf,
            title,
            MARGIN + 18,
            y + row_height - 32,
            150,
            paragraph_style(13, bold=True),
        )
        draw_paragraph(
            pdf,
            body,
            MARGIN + 180,
            y + row_height - 22,
            PAGE_WIDTH - 2 * MARGIN - 198,
            paragraph_style(10, color=MUTED, leading=14),
        )

    pdf.setFont(FONT_REGULAR, 9.5)
    pdf.setFillColor(MUTED)
    draw_paragraph(
        pdf,
        "Три коротких вечера на тему, один длинный — дописать проект. "
        "В конце недели коммит и одна строка: что не получилось.",
        MARGIN,
        92,
        PAGE_WIDTH - 2 * MARGIN,
        paragraph_style(10, color=MUTED, leading=14),
    )
    pdf.showPage()


def build_portfolio_page(pdf: canvas.Canvas) -> None:
    page_chrome(pdf, 7, "Репозиторий")
    top = section_title(
        pdf,
        "Что смотрят в GitHub",
        "Запуск по README и понятные коммиты важнее списка технологий в шапке профиля.",
    )
    top -= 18
    projects = (
        ("01", "Бот", "Команды, пользователи в базе, один внешний API."),
        ("02", "API задач", "Регистрация, роли, PostgreSQL, pytest."),
        ("03", "Тот же сервис", "Docker, лог запроса, полстраницы «как устроено»."),
    )
    card_width = (PAGE_WIDTH - 2 * MARGIN - 16) / 3
    card_height = 132
    card_y = top - card_height
    for index, (number, title, body) in enumerate(projects):
        x = MARGIN + index * (card_width + 8)
        rounded_card(pdf, x, card_y, card_width, card_height, WHITE, radius=2)
        draw_number_badge(pdf, number, x + 22, card_y + card_height - 22)
        draw_paragraph(
            pdf,
            title,
            x + 16,
            card_y + card_height - 48,
            card_width - 32,
            paragraph_style(12, bold=True),
        )
        draw_paragraph(
            pdf,
            body,
            x + 16,
            card_y + card_height - 74,
            card_width - 32,
            paragraph_style(9, color=MUTED, leading=12.5),
        )

    panel_top = card_y - 18
    panel_height = 168
    panel_bottom = panel_top - panel_height
    rounded_card(
        pdf,
        MARGIN,
        panel_bottom,
        PAGE_WIDTH - 2 * MARGIN,
        panel_top - panel_bottom,
        WHITE,
        radius=2,
    )
    draw_paragraph(
        pdf,
        "В каждом репозитории",
        MARGIN + 18,
        panel_top - 16,
        PAGE_WIDTH - 2 * MARGIN - 36,
        paragraph_style(13, bold=True),
    )
    checklist = [
        "README: зачем проект, как запустить, чем проверяли",
        ".env.example без настоящих ключей",
        "Тест на основной сценарий и на ошибку",
        "Коммиты по делу, не пачка «update»",
        "Полстраницы, как устроены части",
        "Ссылка на запущенный сервис или три скриншота",
    ]
    column_width = (PAGE_WIDTH - 2 * MARGIN - 52) / 2
    draw_bullet_list(
        pdf,
        checklist[:3],
        MARGIN + 18,
        panel_top - 48,
        column_width,
        size=9.5,
    )
    draw_bullet_list(
        pdf,
        checklist[3:],
        MARGIN + 18 + column_width + 16,
        panel_top - 48,
        column_width,
        size=9.5,
    )
    draw_paragraph(
        pdf,
        "Два репозитория, которые запускаются, лучше одного большого без инструкции.",
        MARGIN,
        panel_bottom - 18,
        PAGE_WIDTH - 2 * MARGIN,
        paragraph_style(10, color=INK, leading=14),
    )
    pdf.showPage()


def build_cta_page(pdf: canvas.Canvas) -> None:
    pdf.setFillColor(PAPER)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(ACCENT)
    pdf.rect(0, PAGE_HEIGHT - 8, PAGE_WIDTH, 8, stroke=0, fill=1)

    pdf.setFont(FONT_BOLD, 9)
    pdf.setFillColor(INK)
    pdf.drawString(MARGIN, PAGE_HEIGHT - 48, "O&V BACKEND")

    draw_paragraph(
        pdf,
        "Если нужна<br/>проверка кода",
        MARGIN,
        PAGE_HEIGHT - 100,
        420,
        paragraph_style(32, bold=True, leading=36),
    )
    draw_paragraph(
        pdf,
        "По этому гайду можно идти самому. Если хочешь, чтобы кто-то смотрел решения "
        "и говорил, что чинить, напиши. Расскажу, как проходят занятия, и посмотрю, "
        "на каком ты сейчас месте.",
        MARGIN,
        PAGE_HEIGHT - 200,
        460,
        paragraph_style(12, color=MUTED, leading=18),
    )

    box_top = 470
    rounded_card(pdf, MARGIN, box_top - 150, PAGE_WIDTH - 2 * MARGIN, 150, WHITE, radius=2)
    draw_paragraph(
        pdf,
        "Что имеет смысл написать сразу",
        MARGIN + 18,
        box_top - 18,
        PAGE_WIDTH - 2 * MARGIN - 36,
        paragraph_style(12, bold=True),
    )
    draw_bullet_list(
        pdf,
        [
            "Писал ли уже на Python и что именно запускал",
            "Сколько вечеров в неделю реально есть",
            "Нужен разбор с нуля или уже есть свой проект",
        ],
        MARGIN + 18,
        box_top - 50,
        PAGE_WIDTH - 2 * MARGIN - 36,
        size=10.5,
    )

    button_x = MARGIN
    button_y = 230
    button_width = 280
    button_height = 44
    pdf.setFillColor(ACCENT)
    pdf.roundRect(button_x, button_y, button_width, button_height, 2, stroke=0, fill=1)
    pdf.setFillColor(WHITE)
    pdf.setFont(FONT_BOLD, 12)
    pdf.drawCentredString(button_x + button_width / 2, button_y + 16, "Написать в Telegram")
    pdf.linkURL(
        CONTACT_URL,
        (button_x, button_y, button_x + button_width, button_y + button_height),
        relative=0,
    )
    draw_paragraph(
        pdf,
        "Откроется чат @O_V_backend. Текст сообщения уже подставлен: "
        "«Привет, интересно узнать про обучение.»",
        MARGIN,
        button_y - 16,
        420,
        paragraph_style(9, color=MUTED, leading=13),
    )
    pdf.linkURL(
        CONTACT_URL,
        (MARGIN, button_y - 48, MARGIN + 120, button_y - 16),
        relative=0,
    )
    pdf.showPage()


def build_pdf() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT_PATH), pagesize=A4)
    pdf.setTitle("Гайд по backend на Python")
    pdf.setAuthor("O&V Backend")
    pdf.setSubject("Порядок тем, проекты и план на 12 недель")
    build_cover(pdf)
    build_route_page(pdf)
    build_python_page(pdf)
    build_backend_page(pdf)
    build_quality_page(pdf)
    build_plan_page(pdf)
    build_portfolio_page(pdf)
    build_cta_page(pdf)
    pdf.save()


def main() -> None:
    register_fonts()
    build_pdf()
    print(f"Built {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
