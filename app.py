import json
import re
import urllib.parse
import uuid

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    from google import genai
except ImportError:
    genai = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SmartLibrary AI Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# MODERN UI STYLING
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --primary: #7c3aed;
        --primary-dark: #5b21b6;
        --cyan: #0891b2;
        --success: #059669;
        --danger: #dc2626;
        --warning: #ea580c;
        --text: #172033;
        --muted: #64748b;
        --border: #e2e8f0;
        --shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
        --shadow-hover: 0 18px 45px rgba(124, 58, 237, 0.2);
    }

    .stApp {
        color: var(--text);
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(124, 58, 237, 0.12),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 0%,
                rgba(6, 182, 212, 0.12),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #f8fafc 0%,
                #eef2ff 48%,
                #ecfeff 100%
            );
    }

    .main {
        background: transparent;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(18px);
    }

    h1,
    h2,
    h3,
    h4 {
        color: #172033 !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
    }

    h1 {
        font-size: 2.55rem !important;
        background: linear-gradient(
            100deg,
            #5b21b6,
            #7c3aed,
            #0891b2
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    h2 {
        font-size: 1.85rem !important;
    }

    h3 {
        font-size: 1.35rem !important;
    }

    p,
    label,
    span,
    div {
        font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    .stCaption,
    small {
        color: var(--muted) !important;
    }

    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #171329 0%,
                #25144f 45%,
                #123747 100%
            );
        border-right: 1px solid rgba(255, 255, 255, 0.12);
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
        background: none;
        -webkit-text-fill-color: white;
    }

    section[data-testid="stSidebar"] .stButton > button {
        color: white !important;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.24);
    }

    /* --------------------------------------------------------
       HERO BANNER
    -------------------------------------------------------- */

    .hero-banner {
        position: relative;
        overflow: hidden;
        padding: 2.4rem 2.7rem;
        margin-bottom: 1.8rem;
        border-radius: 28px;
        color: white;
        background:
            linear-gradient(
                115deg,
                rgba(76, 29, 149, 0.98),
                rgba(124, 58, 237, 0.94) 46%,
                rgba(8, 145, 178, 0.94)
            );
        box-shadow: 0 22px 55px rgba(76, 29, 149, 0.24);
    }

    .hero-banner::before {
        content: "";
        position: absolute;
        width: 330px;
        height: 330px;
        right: -90px;
        top: -160px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.13);
    }

    .hero-banner::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        left: 42%;
        bottom: -150px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
    }

    .hero-banner h1,
    .hero-banner h2,
    .hero-banner h3,
    .hero-banner p {
        position: relative;
        z-index: 1;
        color: white !important;
        background: none;
        -webkit-text-fill-color: white;
    }

    .hero-banner h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.4rem;
    }

    .hero-banner p {
        max-width: 780px;
        font-size: 1.05rem;
        opacity: 0.92;
    }

    /* --------------------------------------------------------
       BOOK CARDS
    -------------------------------------------------------- */

    .book-container {
        position: relative;
        overflow: hidden;
        padding: 1.55rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.72);
        border-radius: 22px;
        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.94),
                rgba(248, 250, 252, 0.84)
            );
        box-shadow: var(--shadow);
        transition:
            transform 0.25s ease,
            box-shadow 0.25s ease,
            border-color 0.25s ease;
    }

    .book-container:hover {
        transform: translateY(-4px);
        border-color: rgba(124, 58, 237, 0.35);
        box-shadow: var(--shadow-hover);
    }

    .book-container h3 {
        color: #312e81 !important;
    }

    /* --------------------------------------------------------
       RECOMMENDATION CARDS
    -------------------------------------------------------- */

    .recommendation-card {
        height: 100%;
        min-height: 205px;
        padding: 1.35rem;
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 22px;
        background:
            linear-gradient(
                150deg,
                rgba(255, 255, 255, 0.96),
                rgba(238, 242, 255, 0.9)
            );
        box-shadow: var(--shadow);
        transition:
            transform 0.25s ease,
            box-shadow 0.25s ease;
    }

    .recommendation-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-hover);
    }

    .recommendation-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 46px;
        height: 46px;
        margin-bottom: 0.8rem;
        border-radius: 15px;
        color: white;
        font-size: 1.35rem;
        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #0891b2
            );
    }

    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    .stButton > button,
    .stDownloadButton > button,
    .stLinkButton > a {
        min-height: 2.75rem;
        border: 0;
        border-radius: 13px;
        color: white !important;
        font-weight: 700;
        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #0891b2
            );
        box-shadow: 0 8px 18px rgba(124, 58, 237, 0.2);
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease,
            filter 0.2s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stLinkButton > a:hover {
        color: white !important;
        transform: translateY(-2px);
        filter: brightness(1.08);
        box-shadow: 0 12px 25px rgba(124, 58, 237, 0.3);
    }

    /* --------------------------------------------------------
       INPUTS
    -------------------------------------------------------- */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"] {
        border: 1px solid #dbe4f0 !important;
        border-radius: 13px !important;
        color: var(--text) !important;
        background: rgba(255, 255, 255, 0.86) !important;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04);
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: #8b5cf6 !important;
        box-shadow:
            0 0 0 3px rgba(124, 58, 237, 0.13) !important;
    }

    /* --------------------------------------------------------
       TABS
    -------------------------------------------------------- */

    button[data-baseweb="tab"] {
        color: #64748b !important;
        font-weight: 700;
        border-radius: 12px 12px 0 0;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #5b21b6 !important;
        background: rgba(124, 58, 237, 0.1);
    }

    div[data-baseweb="tab-highlight"] {
        background:
            linear-gradient(
                90deg,
                #7c3aed,
                #06b6d4
            );
    }

    /* --------------------------------------------------------
       ALERTS, TABLES AND EXPANDERS
    -------------------------------------------------------- */

    div[data-testid="stAlert"] {
        border: 1px solid rgba(124, 58, 237, 0.16);
        border-radius: 15px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stDataFrame"] {
        overflow: hidden;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        box-shadow: var(--shadow);
    }

    details {
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.76) !important;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.04);
    }

    details summary {
        color: #4c1d95 !important;
        font-weight: 700 !important;
    }

    /* --------------------------------------------------------
       METRIC CARDS
    -------------------------------------------------------- */

    [data-testid="stMetric"] {
        padding: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.78);
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.76);
        box-shadow: var(--shadow);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #4c1d95 !important;
        font-weight: 800;
    }

    /* --------------------------------------------------------
       CHAT
    -------------------------------------------------------- */

    [data-testid="stChatMessage"] {
        padding: 1rem;
        margin: 0.65rem 0;
        border: 1px solid rgba(255, 255, 255, 0.7);
        border-radius: 18px;
        box-shadow: 0 7px 20px rgba(15, 23, 42, 0.06);
    }

    /* --------------------------------------------------------
       LOGIN
    -------------------------------------------------------- */

    .login-shell {
        max-width: 900px;
        margin: 5vh auto 1.5rem auto;
        padding: 2.2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.75);
        border-radius: 30px;
        background: rgba(255, 255, 255, 0.76);
        box-shadow: 0 25px 70px rgba(76, 29, 149, 0.16);
        backdrop-filter: blur(18px);
    }

    .login-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 82px;
        height: 82px;
        margin: 0 auto 1rem auto;
        border-radius: 26px;
        color: white;
        font-size: 2.7rem;
        background:
            linear-gradient(
                135deg,
                #7c3aed,
                #0891b2
            );
        box-shadow: 0 15px 30px rgba(124, 58, 237, 0.26);
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.8rem 2rem 0.8rem;
        }

        h1 {
            font-size: 2rem !important;
        }

        .hero-banner {
            padding: 1.7rem;
            border-radius: 22px;
        }

        .hero-banner h1 {
            font-size: 1.9rem !important;
        }

        .book-container {
            padding: 1.15rem;
            border-radius: 18px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILES AND CONSTANTS
# ============================================================

DATA_FILE = Path("books.csv")
USERS_FILE = Path("users.json")
BORROW_FILE = Path("borrow_records.json")
REVIEWS_FILE = Path("reviews.json")
HOLDS_FILE = Path("holds.json")
RESTOCK_FILE = Path("restock_requests.json")
NOTIFICATIONS_FILE = Path("notifications.json")

TEXTBOOK_FOLDER = Path("textbook_files")
TEXTBOOK_METADATA_FILE = Path(
    "textbook_metadata.json"
)

DAILY_FINE_RATE = 1.0
STANDARD_LOAN_DAYS = 14

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATETIME_FORMAT = "%Y-%m-%d %H:%M"

TEXTBOOK_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# UI HELPERS
# ============================================================

def render_hero(
    title,
    subtitle,
    icon="📚",
):
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>{icon} {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(
    title,
    author,
    genre,
):
    st.markdown(
        f"""
        <div class="recommendation-card">
            <div class="recommendation-icon">
                📖
            </div>
            <h3>{title}</h3>
            <p>
                <strong>Author:</strong>
                {author}
            </p>
            <p>
                <strong>Genre:</strong>
                {genre}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(
    label,
    value,
    icon="📊",
):
    st.markdown(
        f"""
        <div class="recommendation-card"
             style="min-height:125px;">
            <div class="recommendation-icon">
                {icon}
            </div>
            <p style="margin:0;color:#64748b;">
                {label}
            </p>
            <h2 style="margin:.25rem 0 0 0;">
                {value}
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(
    text,
    status="info",
):
    colors = {
        "success": "#059669",
        "danger": "#dc2626",
        "warning": "#ea580c",
        "info": "#0891b2",
    }

    color = colors.get(
        status,
        colors["info"],
    )

    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:.4rem .8rem;
            border-radius:999px;
            color:white;
            font-size:.82rem;
            font-weight:700;
            background:{color};
            box-shadow:0 5px 12px {color}44;
        ">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )


def text_value(
    value,
    default="",
):
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (
        TypeError,
        ValueError,
    ):
        pass

    return str(value)


def normalize_text(value):
    return text_value(value).strip().lower()


def clean_file_name(filename):
    filename = Path(filename).name

    return re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        filename,
    )


# ============================================================
# JSON FILE MANAGEMENT
# ============================================================

def save_json(
    filepath,
    data,
):
    filepath = Path(filepath)

    with filepath.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


def load_json(
    filepath,
    default_value,
):
    filepath = Path(filepath)

    if not filepath.exists():
        save_json(
            filepath,
            default_value,
        )
        return default_value

    try:
        with filepath.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
        TypeError,
    ):
        save_json(
            filepath,
            default_value,
        )
        return default_value


def initialize_files():
    default_files = {
        USERS_FILE: {},
        BORROW_FILE: [],
        REVIEWS_FILE: [],
        HOLDS_FILE: [],
        RESTOCK_FILE: [],
        NOTIFICATIONS_FILE: [],
        TEXTBOOK_METADATA_FILE: {},
    }

    for filepath, default_value in default_files.items():
        if not filepath.exists():
            save_json(
                filepath,
                default_value,
            )


initialize_files()


# ============================================================
# TEXTBOOK PDF MANAGEMENT
# ============================================================

def load_textbook_metadata():
    return load_json(
        TEXTBOOK_METADATA_FILE,
        {},
    )


def save_textbook_metadata(metadata):
    save_json(
        TEXTBOOK_METADATA_FILE,
        metadata,
    )


def get_book_file_info(book_title):
    metadata = load_textbook_metadata()

    return metadata.get(
        normalize_text(book_title)
    )


def save_uploaded_textbook(
    book_title,
    uploaded_file,
    uploaded_by,
):
    if uploaded_file is None:
        return (
            False,
            "Please choose a PDF file.",
        )

    original_filename = text_value(
        uploaded_file.name
    )

    if not original_filename.lower().endswith(
        ".pdf"
    ):
        return (
            False,
            "Only PDF files are allowed.",
        )

    if uploaded_file.size <= 0:
        return (
            False,
            "The uploaded PDF is empty.",
        )

    safe_filename = clean_file_name(
        original_filename
    )

    unique_filename = (
        f"{uuid.uuid4().hex[:12]}_"
        f"{safe_filename}"
    )

    saved_path = (
        TEXTBOOK_FOLDER / unique_filename
    )

    try:
        with saved_path.open(
            "wb"
        ) as output_file:
            output_file.write(
                uploaded_file.getbuffer()
            )

    except OSError as error:
        return (
            False,
            f"Could not save PDF: {error}",
        )

    metadata = load_textbook_metadata()

    book_key = normalize_text(book_title)

    old_file_info = metadata.get(book_key)

    if old_file_info:
        old_filename = old_file_info.get(
            "saved_filename"
        )

        if old_filename:
            old_path = (
                TEXTBOOK_FOLDER / old_filename
            )

            try:
                if old_path.exists():
                    old_path.unlink()
            except OSError:
                pass

    metadata[book_key] = {
        "book_title": text_value(book_title),
        "original_filename": original_filename,
        "saved_filename": unique_filename,
        "uploaded_by": text_value(
            uploaded_by,
            "Admin",
        ),
        "uploaded_at": datetime.now().strftime(
            DISPLAY_DATETIME_FORMAT
        ),
    }

    save_textbook_metadata(metadata)

    return (
        True,
        "PDF uploaded successfully.",
    )


def read_textbook_pdf(book_title):
    file_info = get_book_file_info(
        book_title
    )

    if not file_info:
        return None, None

    saved_filename = file_info.get(
        "saved_filename"
    )

    if not saved_filename:
        return None, None

    pdf_path = (
        TEXTBOOK_FOLDER / saved_filename
    )

    if not pdf_path.exists():
        return None, None

    try:
        return (
            pdf_path.read_bytes(),
            file_info,
        )
    except OSError:
        return None, None


def delete_uploaded_textbook(book_title):
    metadata = load_textbook_metadata()

    book_key = normalize_text(book_title)

    file_info = metadata.get(book_key)

    if not file_info:
        return (
            False,
            "No PDF is linked to this book.",
        )

    saved_filename = file_info.get(
        "saved_filename"
    )

    if saved_filename:
        saved_path = (
            TEXTBOOK_FOLDER / saved_filename
        )

        try:
            if saved_path.exists():
                saved_path.unlink()
        except OSError as error:
            return (
                False,
                f"Could not delete PDF: {error}",
            )

    metadata.pop(book_key, None)

    save_textbook_metadata(metadata)

    return (
        True,
        "PDF deleted successfully.",
    )


# ============================================================
# USERS
# ============================================================

def load_users():
    return load_json(
        USERS_FILE,
        {},
    )


def save_users(users):
    save_json(
        USERS_FILE,
        users,
    )


def generate_next_userid(users_db):
    existing_numbers = []

    for user_data in users_db.values():
        userid = text_value(
            user_data.get("userid")
        )

        if (
            userid.startswith("user")
            and userid[4:].isdigit()
        ):
            existing_numbers.append(
                int(userid[4:])
            )

    next_number = max(
        existing_numbers,
        default=0,
    ) + 1

    return f"user{next_number}"


# ============================================================
# BORROWING AND FINES
# ============================================================

def load_borrow_records():
    return load_json(
        BORROW_FILE,
        [],
    )


def get_next_record_id(records):
    record_ids = []

    for record in records:
        try:
            record_ids.append(
                int(
                    record.get(
                        "record_id",
                        0,
                    )
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            pass

    return max(
        record_ids,
        default=0,
    ) + 1


def get_overdue_days(due_date_string):
    try:
        due_date = datetime.strptime(
            due_date_string,
            DATETIME_FORMAT,
        )
    except (
        TypeError,
        ValueError,
    ):
        return 0

    today = datetime.now().date()

    if today > due_date.date():
        return (
            today - due_date.date()
        ).days

    return 0


def calculate_current_fine(due_date_string):
    overdue_days = get_overdue_days(
        due_date_string
    )

    fine_amount = (
        overdue_days
        * DAILY_FINE_RATE
    )

    return (
        fine_amount,
        overdue_days,
    )


def save_borrow_record(
    username,
    userid,
    book_title,
    action,
    record_id=None,
):
    records = load_borrow_records()

    now = datetime.now()

    if action == "Borrowed":
        due_date = now + timedelta(
            days=STANDARD_LOAN_DAYS
        )

        records.append(
            {
                "record_id": get_next_record_id(
                    records
                ),
                "username": username,
                "userid": userid,
                "book_title": book_title,
                "borrow_date": now.strftime(
                    DATETIME_FORMAT
                ),
                "due_date": due_date.strftime(
                    DATETIME_FORMAT
                ),
                "return_date": None,
                "status": "Active",
                "fine_amount": 0.0,
            }
        )

    elif (
        action == "Returned"
        and record_id is not None
    ):
        for record in records:
            if (
                record.get("record_id")
                == record_id
                and record.get("status")
                == "Active"
            ):
                record["status"] = "Returned"

                record["return_date"] = (
                    now.strftime(
                        DATETIME_FORMAT
                    )
                )

                overdue_days = get_overdue_days(
                    record.get("due_date")
                )

                record["fine_amount"] = (
                    overdue_days
                    * DAILY_FINE_RATE
                )

                break

    save_json(
        BORROW_FILE,
        records,
    )


# ============================================================
# HOLDS
# ============================================================

def load_holds():
    return load_json(
        HOLDS_FILE,
        [],
    )


def get_next_hold_id(holds):
    hold_ids = []

    for hold in holds:
        try:
            hold_ids.append(
                int(
                    hold.get(
                        "hold_id",
                        0,
                    )
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            pass

    return max(
        hold_ids,
        default=0,
    ) + 1


def add_hold_request(
    username,
    userid,
    book_title,
):
    holds = load_holds()

    clean_title = text_value(
        book_title
    ).strip()

    duplicate_exists = any(
        normalize_text(
            hold.get("userid")
        )
        == normalize_text(userid)
        and normalize_text(
            hold.get("book_title")
        )
        == normalize_text(clean_title)
        and hold.get("status")
        == "Pending"
        for hold in holds
    )

    if duplicate_exists:
        return False

    holds.append(
        {
            "hold_id": get_next_hold_id(
                holds
            ),
            "username": username,
            "userid": userid,
            "book_title": clean_title,
            "request_date": datetime.now().strftime(
                DATETIME_FORMAT
            ),
            "status": "Pending",
        }
    )

    save_json(
        HOLDS_FILE,
        holds,
    )

    return True


def fulfill_next_hold(book_title):
    holds = load_holds()

    clean_title = text_value(
        book_title
    ).strip()

    for hold in holds:
        hold_title = text_value(
            hold.get("book_title")
        ).strip()

        if (
            normalize_text(hold_title)
            == normalize_text(clean_title)
            and hold.get("status")
            == "Pending"
        ):
            hold["status"] = "Fulfilled"

            save_json(
                HOLDS_FILE,
                holds,
            )

            send_notification(
                hold.get("userid", ""),
                hold.get("username", ""),
                (
                    f"Good news! '{clean_title}' "
                    "is now back in stock and reserved "
                    "for you."
                ),
            )

            break


# ============================================================
# REVIEWS
# ============================================================

def load_reviews():
    return load_json(
        REVIEWS_FILE,
        [],
    )


def add_review(
    username,
    userid,
    book_title,
    rating,
    review_text,
):
    reviews = load_reviews()

    reviews.append(
        {
            "username": username,
            "userid": userid,
            "book_title": text_value(
                book_title
            ).strip(),
            "rating": int(rating),
            "review": text_value(
                review_text
            ).strip(),
            "timestamp": datetime.now().strftime(
                DISPLAY_DATETIME_FORMAT
            ),
        }
    )

    save_json(
        REVIEWS_FILE,
        reviews,
    )


def get_book_reviews(book_title):
    clean_title = normalize_text(
        book_title
    )

    return [
        review
        for review in load_reviews()
        if normalize_text(
            review.get("book_title")
        )
        == clean_title
    ]


# ============================================================
# NOTIFICATIONS
# ============================================================

def load_notifications():
    return load_json(
        NOTIFICATIONS_FILE,
        [],
    )


def send_notification(
    userid,
    username,
    message,
):
    notifications = load_notifications()

    notifications.append(
        {
            "userid": userid,
            "username": username,
            "message": message,
            "timestamp": datetime.now().strftime(
                DISPLAY_DATETIME_FORMAT
            ),
            "status": "Unread",
        }
    )

    save_json(
        NOTIFICATIONS_FILE,
        notifications,
    )


def get_user_notifications(userid):
    return [
        notification
        for notification in load_notifications()
        if notification.get("userid")
        == userid
    ]


def mark_user_notifications_as_read(userid):
    notifications = load_notifications()

    for notification in notifications:
        if notification.get("userid") == userid:
            notification["status"] = "Read"

    save_json(
        NOTIFICATIONS_FILE,
        notifications,
    )


# ============================================================
# BOOK CATALOG
# ============================================================

def create_fallback_books():
    return pd.DataFrame(
        {
            "Title": [
                "Designing Data-Intensive Applications",
                "Clean Code",
                "Artificial Intelligence: A Modern Approach",
                "The Pragmatic Programmer",
                "Deep Learning",
                "Java: The Complete Reference",
            ],
            "Author": [
                "Martin Kleppmann",
                "Robert C. Martin",
                "Stuart Russell",
                "Andrew Hunt",
                "Ian Goodfellow",
                "Herbert Schildt",
            ],
            "Genre": [
                "Database Systems",
                "Software Design",
                "Artificial Intelligence",
                "Software Engineering",
                "Artificial Intelligence",
                "Java Programming",
            ],
            "Count": [
                3,
                0,
                0,
                4,
                1,
                2,
            ],
        }
    )


def normalize_and_load_books():
    if DATA_FILE.exists():
        try:
            try:
                books_df = pd.read_csv(
                    DATA_FILE,
                    encoding="utf-8",
                )
            except UnicodeDecodeError:
                books_df = pd.read_csv(
                    DATA_FILE,
                    encoding="latin-1",
                )

            books_df.columns = [
                str(column)
                .strip()
                .lower()
                .replace("-", "_")
                .replace(" ", "_")
                for column in books_df.columns
            ]

            title_column = next(
                (
                    column
                    for column in [
                        "title",
                        "book_title",
                        "name",
                    ]
                    if column in books_df.columns
                ),
                None,
            )

            author_column = next(
                (
                    column
                    for column in [
                        "author",
                        "authors",
                        "book_author",
                    ]
                    if column in books_df.columns
                ),
                None,
            )

            genre_column = next(
                (
                    column
                    for column in [
                        "genre",
                        "category",
                        "topic",
                    ]
                    if column in books_df.columns
                ),
                None,
            )

            count_column = next(
                (
                    column
                    for column in [
                        "count",
                        "stock_count",
                        "stock",
                        "quantity",
                    ]
                    if column in books_df.columns
                ),
                None,
            )

            if title_column:
                books_df["Title"] = (
                    books_df[title_column]
                    .fillna("Unknown Title")
                    .astype(str)
                    .str.strip()
                )
            else:
                books_df["Title"] = "Unknown Title"

            if author_column:
                books_df["Author"] = (
                    books_df[author_column]
                    .fillna("Unknown Author")
                    .astype(str)
                    .str.strip()
                )
            else:
                books_df["Author"] = "Unknown Author"

            if genre_column:
                books_df["Genre"] = (
                    books_df[genre_column]
                    .fillna(
                        "General Software & AI"
                    )
                    .astype(str)
                    .str.strip()
                )
            else:
                books_df["Genre"] = (
                    "General Software & AI"
                )

            if count_column:
                books_df["Count"] = (
                    pd.to_numeric(
                        books_df[count_column],
                        errors="coerce",
                    )
                    .fillna(0)
                )
            else:
                books_df["Count"] = 0

            books_df["Count"] = (
                books_df["Count"]
                .clip(lower=0)
                .astype(int)
            )

            books_df = books_df[
                [
                    "Title",
                    "Author",
                    "Genre",
                    "Count",
                ]
            ].drop_duplicates(
                subset=["Title"],
                keep="first",
            )

            books_df = books_df[
                books_df["Title"].str.strip()
                != ""
            ]

            if not books_df.empty:
                return books_df.reset_index(
                    drop=True
                )

        except Exception as error:
            st.warning(
                "Could not load books.csv. "
                "Using sample books instead. "
                f"Details: {error}"
            )

    fallback_df = create_fallback_books()

    fallback_df.to_csv(
        DATA_FILE,
        index=False,
    )

    return fallback_df


def save_books_data(books_df):
    books_df.to_csv(
        DATA_FILE,
        index=False,
    )


def add_restock_request(
    book_title,
    author,
):
    requests = load_json(
        RESTOCK_FILE,
        [],
    )

    clean_title = text_value(
        book_title
    ).strip()

    already_requested = any(
        normalize_text(
            request.get("title")
        )
        == normalize_text(clean_title)
        for request in requests
    )

    if already_requested:
        return False

    requests.append(
        {
            "title": clean_title,
            "author": text_value(
                author
            ).strip(),
            "status": "Pending Restock",
            "request_date": datetime.now().strftime(
                DISPLAY_DATETIME_FORMAT
            ),
        }
    )

    save_json(
        RESTOCK_FILE,
        requests,
    )

    return True


def resolve_restock_request(book_title):
    requests = load_json(
        RESTOCK_FILE,
        [],
    )

    clean_title = text_value(
        book_title
    ).strip()

    remaining_requests = [
        request
        for request in requests
        if normalize_text(
            request.get("title")
        )
        != normalize_text(clean_title)
    ]

    save_json(
        RESTOCK_FILE,
        remaining_requests,
    )

    fulfill_next_hold(clean_title)


# ============================================================
# SEARCH AND RECOMMENDATIONS
# ============================================================

class SmartLibraryAgent:
    @staticmethod
    def natural_language_search(
        books_df,
        query,
    ):
        query_tokens = [
            token.lower()
            for token in text_value(
                query
            )
            .strip()
            .split()
            if len(token) > 2
        ]

        if not query_tokens:
            return books_df.copy()

        def score_row(row):
            row_text = (
                f"{row['Title']} "
                f"{row['Author']} "
                f"{row['Genre']}"
            ).lower()

            return sum(
                2
                for token in query_tokens
                if token in row_text
            )

        result_df = books_df.copy()

        result_df["relevance"] = (
            result_df.apply(
                score_row,
                axis=1,
            )
        )

        result_df = result_df[
            result_df["relevance"] > 0
        ].sort_values(
            by="relevance",
            ascending=False,
        )

        return result_df.drop(
            columns=["relevance"],
            errors="ignore",
        )

    @staticmethod
    def generate_ai_recommendations(
        books_df,
        userid,
    ):
        records = load_borrow_records()

        borrowed_titles = [
            record.get("book_title")
            for record in records
            if record.get("userid") == userid
        ]

        reviews = load_reviews()

        highly_rated_titles = [
            review.get("book_title")
            for review in reviews
            if (
                review.get("userid") == userid
                and int(
                    review.get("rating", 0)
                )
                >= 4
            )
        ]

        interests = list(
            set(
                borrowed_titles
                + highly_rated_titles
            )
        )

        if not interests:
            available_books = books_df[
                books_df["Count"] > 0
            ]

            if available_books.empty:
                return books_df.head(3)

            return available_books.sample(
                min(
                    3,
                    len(available_books),
                ),
                random_state=42,
            )

        interest_books = books_df[
            books_df["Title"].isin(interests)
        ]

        favorite_genres = interest_books[
            "Genre"
        ].tolist()

        favorite_authors = interest_books[
            "Author"
        ].tolist()

        recommendations = books_df[
            (
                ~books_df["Title"].isin(
                    borrowed_titles
                )
            )
            & (
                books_df["Genre"].isin(
                    favorite_genres
                )
                | books_df["Author"].isin(
                    favorite_authors
                )
            )
        ]

        if recommendations.empty:
            recommendations = books_df[
                ~books_df["Title"].isin(
                    borrowed_titles
                )
            ]

        return recommendations.head(4)

    @staticmethod
    def get_external_links(
        book_title,
        author,
    ):
        query = urllib.parse.quote(
            f"{book_title} {author}"
        )

        return {
            "Amazon": (
                "https://www.amazon.com/s?k="
                f"{query}"
            ),
            "Flipkart": (
                "https://www.flipkart.com/search?q="
                f"{query}"
            ),
            "Google Books": (
                "https://www.google.com/search?"
                f"tbm=bks&q={query}"
            ),
            "Open Library": (
                "https://openlibrary.org/search?q="
                f"{query}"
            ),
            "WorldCat": (
                "https://www.worldcat.org/search?q="
                f"{query}"
            ),
        }


agent = SmartLibraryAgent()


# ============================================================
# GEMINI CHATBOT
# ============================================================

def get_gemini_client():
    if genai is None:
        return None

    try:
        api_key = st.secrets.get(
            "GEMINI_API_KEY"
        )

        if not api_key:
            return None

        return genai.Client(
            api_key=api_key
        )

    except Exception:
        return None


def get_gemini_model():
    try:
        return st.secrets.get(
            "GEMINI_MODEL",
            "gemini-3.6-flash",
        )
    except Exception:
        return "gemini-3.6-flash"


def build_library_context(
    books_df,
    username,
    userid,
):
    books_context = []

    for _, book in books_df.iterrows():
        books_context.append(
            {
                "title": text_value(
                    book.get("Title"),
                    "Unknown",
                ),
                "author": text_value(
                    book.get("Author"),
                    "Unknown",
                ),
                "genre": text_value(
                    book.get("Genre"),
                    "Unknown",
                ),
                "available_copies": int(
                    book.get("Count", 0)
                ),
            }
        )

    all_borrow_records = load_borrow_records()

    user_borrow_records = [
        record
        for record in all_borrow_records
        if record.get("userid") == userid
    ]

    return {
        "current_user": {
            "username": username,
            "userid": userid,
        },
        "books": books_context,
        "user_active_loans": [
            record
            for record in user_borrow_records
            if record.get("status")
            == "Active"
        ],
        "user_borrowing_history": user_borrow_records,
        "user_holds": [
            hold
            for hold in load_holds()
            if hold.get("userid") == userid
        ],
        "user_notifications": [
            notification
            for notification in load_notifications()
            if notification.get("userid")
            == userid
        ],
        "book_reviews": load_reviews(),
        "available_digital_textbooks": [
            {
                "book_title": info.get(
                    "book_title",
                    "Unknown",
                ),
                "filename": info.get(
                    "original_filename",
                    "Unknown",
                ),
            }
            for info in load_textbook_metadata().values()
        ],
        "library_rules": {
            "standard_loan_days": STANDARD_LOAN_DAYS,
            "daily_fine_rate": DAILY_FINE_RATE,
        },
    }


def create_chatbot_system_prompt(
    library_context,
):
    return f"""
You are SmartLibrary Assistant inside a library
management application.

You help users with:

- Finding books
- Searching by title, author, or genre
- Checking available copies
- Checking active loans
- Checking borrowing history
- Checking due dates
- Explaining fines
- Checking holds
- Finding digital textbooks
- Suggesting books from the catalog
- Explaining library rules

Rules:

1. Use only the supplied library data.
2. Never invent book names, stock counts, dates,
   fines, reviews, or notifications.
3. If information is unavailable, say so clearly.
4. Never reveal another user's private information.
5. Keep answers friendly and concise.
6. Borrowing and returning books are administrator actions.
7. Do not claim that you performed an action.
8. Recommend books only from the supplied catalog.
9. The standard loan period is
   {STANDARD_LOAN_DAYS} days.
10. The daily fine rate is
    {DAILY_FINE_RATE} per overdue day.

Library data:

{json.dumps(
    library_context,
    indent=2,
    ensure_ascii=False,
    default=str,
)}
"""


def local_library_answer(
    user_message,
    books_df,
    userid,
):
    message = normalize_text(
        user_message
    )

    user_records = [
        record
        for record in load_borrow_records()
        if record.get("userid") == userid
    ]

    active_loans = [
        record
        for record in user_records
        if record.get("status") == "Active"
    ]

    total_borrowed = len(user_records)
    total_active = len(active_loans)

    if (
        "how many books" in message
        or "books i borrowed" in message
        or "books have i borrowed" in message
        or "borrowed books" in message
    ):
        return (
            f"You have borrowed {total_borrowed} "
            f"book(s) in total. "
            f"You currently have {total_active} "
            f"active book(s)."
        )

    if (
        "active loan" in message
        or "currently borrowed" in message
        or "books with me" in message
        or "current books" in message
    ):
        if not active_loans:
            return (
                "You do not have any active borrowed books."
            )

        titles = [
            text_value(
                record.get(
                    "book_title",
                    "Unknown Book",
                )
            )
            for record in active_loans
        ]

        return (
            f"You currently have {len(titles)} "
            "active book(s):\n\n"
            + "\n".join(
                f"- {title}"
                for title in titles
            )
        )

    if (
        "overdue" in message
        or "fine" in message
    ):
        if not active_loans:
            return (
                "You do not have any active loans, "
                "so your current fine is 0."
            )

        total_fine = 0.0
        overdue_books = []

        for record in active_loans:
            fine_amount, overdue_days = (
                calculate_current_fine(
                    record.get("due_date")
                )
            )

            total_fine += fine_amount

            if overdue_days > 0:
                overdue_books.append(
                    {
                        "title": record.get(
                            "book_title",
                            "Unknown Book",
                        ),
                        "days": overdue_days,
                        "fine": fine_amount,
                    }
                )

        if not overdue_books:
            return (
                "You have no overdue books. "
                "Your current fine is 0."
            )

        details = "\n".join(
            (
                f"- {item['title']}: "
                f"{item['days']} overdue day(s), "
                f"fine {item['fine']:.2f}"
            )
            for item in overdue_books
        )

        return (
            f"Your total current fine is "
            f"{total_fine:.2f}.\n\n"
            f"Overdue books:\n{details}"
        )

    if (
        "available" in message
        or "in stock" in message
        or "which books" in message
        or "what books" in message
        or "book is there" in message
    ):
        ignored_words = {
            "which",
            "what",
            "book",
            "books",
            "there",
            "library",
            "available",
            "stock",
            "are",
            "is",
            "in",
            "the",
            "for",
            "show",
            "tell",
            "me",
        }

        search_words = [
            word
            for word in message.split()
            if len(word) > 2
            and word not in ignored_words
        ]

        if search_words:
            matching_books = books_df[
                books_df.apply(
                    lambda row: all(
                        word in (
                            f"{row['Title']} "
                            f"{row['Author']} "
                            f"{row['Genre']}"
                        ).lower()
                        for word in search_words
                    ),
                    axis=1,
                )
            ]
        else:
            matching_books = books_df

        if matching_books.empty:
            return (
                "I could not find a matching book "
                "in the library catalog."
            )

        details = "\n".join(
            (
                f"- {row['Title']} by "
                f"{row['Author']} "
                f"({int(row['Count'])} available)"
            )
            for _, row in matching_books.iterrows()
        )

        return (
            "Matching books in the library:\n\n"
            f"{details}"
        )

    if (
        "digital textbook" in message
        or "pdf" in message
        or "soft copy" in message
    ):
        metadata = load_textbook_metadata()

        if not metadata:
            return (
                "No digital textbooks are currently "
                "available."
            )

        titles = [
            text_value(
                info.get(
                    "book_title",
                    "Unknown Book",
                )
            )
            for info in metadata.values()
        ]

        return (
            "Available digital textbooks:\n\n"
            + "\n".join(
                f"- {title}"
                for title in titles
            )
        )

    return None


def ask_gemini_chatbot(
    user_message,
    books_df,
    username,
    userid,
):
    local_answer = local_library_answer(
        user_message,
        books_df,
        userid,
    )

    if local_answer:
        return local_answer

    client = get_gemini_client()

    if client is None:
        return (
            "Gemini is not configured. Add "
            "GEMINI_API_KEY to "
            ".streamlit/secrets.toml."
        )

    library_context = build_library_context(
        books_df,
        username,
        userid,
    )

    system_prompt = create_chatbot_system_prompt(
        library_context
    )

    previous_messages = st.session_state.get(
        "chat_messages",
        [],
    )

    recent_messages = previous_messages[-10:]

    conversation_parts = [
        system_prompt
    ]

    for message in recent_messages:
        conversation_parts.append(
            (
                f"{message['role'].upper()}: "
                f"{message['content']}"
            )
        )

    conversation_parts.append(
        f"USER: {user_message}"
    )

    full_prompt = "\n\n".join(
        conversation_parts
    )

    try:
        response = client.models.generate_content(
            model=get_gemini_model(),
            contents=full_prompt,
        )

        answer = response.text

        if not answer:
            return (
                "Gemini returned an empty response. "
                "Please try again."
            )

        return answer.strip()

    except Exception as error:
        error_text = str(error).lower()

        if (
            "429" in error_text
            or "quota" in error_text
            or "resource exhausted" in error_text
        ):
            return (
                "The Gemini free-tier limit has been "
                "reached temporarily. Basic library "
                "questions still work locally."
            )

        if (
            "404" in error_text
            or "not found" in error_text
            or "no longer available" in error_text
        ):
            return (
                "The selected Gemini model is unavailable. "
                "Check GEMINI_MODEL in "
                ".streamlit/secrets.toml."
            )

        if (
            "401" in error_text
            or "403" in error_text
            or "permission" in error_text
            or "api key" in error_text
        ):
            return (
                "The Gemini API key was rejected. "
                "Check GEMINI_API_KEY in "
                ".streamlit/secrets.toml."
            )

        return (
            "Gemini could not process the request.\n\n"
            f"Technical details: {error}"
        )


def render_library_chatbot(books_df):
    render_hero(
        "SmartLibrary AI Assistant",
        (
            "Ask about books, availability, loans, "
            "due dates, fines, holds, reviews, "
            "or digital textbooks."
        ),
        "🤖",
    )

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your SmartLibrary "
                    "Assistant.\n\n"
                    "Try asking:\n"
                    "- Which Java books are available?\n"
                    "- How many books have I borrowed?\n"
                    "- Do I have overdue books?\n"
                    "- What is my current fine?\n"
                    "- Which digital textbooks are available?"
                ),
            }
        ]

    if st.button(
        "🗑️ Clear Chat",
        key="clear_library_chat",
    ):
        st.session_state.chat_messages = []
        st.rerun()

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input(
        "Ask SmartLibrary Assistant...",
        key="library_chat_input",
    )

    if user_message:
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):
            with st.spinner(
                "Checking the library..."
            ):
                assistant_answer = (
                    ask_gemini_chatbot(
                        user_message,
                        books_df,
                        st.session_state.username,
                        st.session_state.userid,
                    )
                )

            st.markdown(assistant_answer)

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": assistant_answer,
            }
        )


# ============================================================
# SESSION STATE
# ============================================================

default_session_state = {
    "authenticated": False,
    "username": None,
    "userid": None,
    "role": None,
}

for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# LOGIN SCREEN
# ============================================================

users_db = load_users()

if not st.session_state.authenticated:
    st.markdown(
        """
        <div class="login-shell">
            <div class="login-icon">📚</div>
            <h1>SmartLibrary AI Portal</h1>
            <p>
                Discover knowledge. Manage books.
                Learn smarter.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    portal_type = st.radio(
        "Select Access Portal",
        [
            "👤 User Portal",
            "⚙️ Admin Portal",
        ],
        horizontal=True,
    )

    if portal_type == "👤 User Portal":
        st.header(
            "👤 Member Access Portal"
        )

        login_tab, register_tab = st.tabs(
            [
                "🔒 User Login",
                "📝 User Registration",
            ]
        )

        with login_tab:
            login_input = st.text_input(
                "Username or User ID",
                key="user_login_input",
            )

            login_password = st.text_input(
                "Password",
                type="password",
                key="user_login_password",
            )

            if st.button(
                "Login to User Portal",
                use_container_width=True,
            ):
                target_username = None
                target_data = None

                login_value = (
                    login_input.strip().lower()
                )

                for username, user_data in users_db.items():
                    if (
                        username.lower()
                        == login_value
                        or normalize_text(
                            user_data.get("userid")
                        )
                        == login_value
                    ):
                        target_username = username
                        target_data = user_data
                        break

                if not target_data:
                    st.error(
                        "Account not found. "
                        "Please register first."
                    )

                elif target_data.get("role") != "User":
                    st.error(
                        "This is an Admin account. "
                        "Use the Admin Portal."
                    )

                elif target_data.get(
                    "password"
                ) != login_password:
                    st.error(
                        "Incorrect password."
                    )

                else:
                    st.session_state.authenticated = True
                    st.session_state.username = (
                        target_username
                    )
                    st.session_state.userid = (
                        target_data.get(
                            "userid",
                            "N/A",
                        )
                    )
                    st.session_state.role = "User"

                    st.rerun()

        with register_tab:
            registration_username = st.text_input(
                "Choose Username",
                key="user_registration_username",
            )

            registration_password = st.text_input(
                "Choose Password",
                type="password",
                key="user_registration_password",
            )

            if st.button(
                "Create User Account",
                use_container_width=True,
            ):
                clean_username = (
                    registration_username.strip()
                )

                username_exists = any(
                    username.lower()
                    == clean_username.lower()
                    for username in users_db
                )

                if (
                    not clean_username
                    or not registration_password
                ):
                    st.error(
                        "Please fill in both fields."
                    )

                elif username_exists:
                    st.error(
                        "Username already exists."
                    )

                else:
                    assigned_userid = (
                        generate_next_userid(
                            users_db
                        )
                    )

                    users_db[clean_username] = {
                        "password": registration_password,
                        "role": "User",
                        "userid": assigned_userid,
                    }

                    save_users(users_db)

                    st.success(
                        "Account registered successfully. "
                        f"Your User ID is {assigned_userid}."
                    )

    else:
        st.header(
            "⚙️ Administrator Control Portal"
        )

        login_tab, register_tab = st.tabs(
            [
                "🔒 Admin Login",
                "📝 Admin Registration",
            ]
        )

        with login_tab:
            admin_username = st.text_input(
                "Admin Username",
                key="admin_login_username",
            )

            admin_password = st.text_input(
                "Admin Password",
                type="password",
                key="admin_login_password",
            )

            if st.button(
                "Login to Admin Dashboard",
                use_container_width=True,
            ):
                admin_data = users_db.get(
                    admin_username
                )

                if not admin_data:
                    st.error(
                        "Admin account not found."
                    )

                elif admin_data.get(
                    "role"
                ) != "Admin":
                    st.error(
                        "This is a User account. "
                        "Use the User Portal."
                    )

                elif admin_data.get(
                    "password"
                ) != admin_password:
                    st.error(
                        "Incorrect password."
                    )

                else:
                    st.session_state.authenticated = True
                    st.session_state.username = (
                        admin_username
                    )
                    st.session_state.userid = (
                        admin_data.get(
                            "userid",
                            "admin",
                        )
                    )
                    st.session_state.role = "Admin"

                    st.rerun()

        with register_tab:
            admin_registration_username = st.text_input(
                "Choose Admin Username",
                key="admin_registration_username",
            )

            admin_registration_password = st.text_input(
                "Choose Admin Password",
                type="password",
                key="admin_registration_password",
            )

            if st.button(
                "Create Admin Account",
                use_container_width=True,
            ):
                clean_admin_username = (
                    admin_registration_username.strip()
                )

                username_exists = any(
                    username.lower()
                    == clean_admin_username.lower()
                    for username in users_db
                )

                if (
                    not clean_admin_username
                    or not admin_registration_password
                ):
                    st.error(
                        "Please fill in both fields."
                    )

                elif username_exists:
                    st.error(
                        "Username already exists."
                    )

                else:
                    users_db[
                        clean_admin_username
                    ] = {
                        "password": (
                            admin_registration_password
                        ),
                        "role": "Admin",
                        "userid": "admin",
                    }

                    save_users(users_db)

                    st.success(
                        "Admin account created "
                        "successfully."
                    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    f"👤 {st.session_state.username}"
)

st.sidebar.write(
    f"**Role:** {st.session_state.role}"
)

if st.session_state.role == "User":
    st.sidebar.info(
        f"🆔 **User ID:** "
        f"`{st.session_state.userid}`"
    )

    unread_notifications = [
        notification
        for notification in get_user_notifications(
            st.session_state.userid
        )
        if notification.get("status")
        == "Unread"
    ]

    if unread_notifications:
        st.sidebar.warning(
            f"🔔 You have "
            f"{len(unread_notifications)} "
            "new notification(s)."
        )

if st.sidebar.button(
    "Logout",
    use_container_width=True,
):
    for key, value in default_session_state.items():
        st.session_state[key] = value

    st.session_state.pop(
        "chat_messages",
        None,
    )

    st.rerun()


# ============================================================
# LOAD BOOKS AND NAVIGATION
# ============================================================

books_df = normalize_and_load_books()

if st.session_state.role == "Admin":
    app_mode = st.sidebar.radio(
        "Navigation",
        [
            "User Discovery Portal",
            "Admin Control Center",
        ],
    )
else:
    app_mode = "User Discovery Portal"


# ============================================================
# USER DISCOVERY PORTAL
# ============================================================

if app_mode == "User Discovery Portal":
    render_hero(
        "Smart Library Discovery",
        (
            "Explore your digital library, discover "
            "personalized recommendations, manage loans, "
            "and chat with your AI-powered assistant."
        ),
        "📚",
    )

    user_records = load_borrow_records()

    user_active_loans = [
        record
        for record in user_records
        if (
            record.get("userid")
            == st.session_state.userid
            and record.get("status")
            == "Active"
        )
    ]

    user_total_loans = [
        record
        for record in user_records
        if record.get("userid")
        == st.session_state.userid
    ]

    user_holds = [
        hold
        for hold in load_holds()
        if hold.get("userid")
        == st.session_state.userid
    ]

    unread_count = sum(
        1
        for notification in get_user_notifications(
            st.session_state.userid
        )
        if notification.get("status")
        == "Unread"
    )

    metric_columns = st.columns(4)

    with metric_columns[0]:
        render_stat_card(
            "Books borrowed",
            len(user_total_loans),
            "📚",
        )

    with metric_columns[1]:
        render_stat_card(
            "Active loans",
            len(user_active_loans),
            "📖",
        )

    with metric_columns[2]:
        render_stat_card(
            "Book holds",
            len(user_holds),
            "📌",
        )

    with metric_columns[3]:
        render_stat_card(
            "Unread alerts",
            unread_count,
            "🔔",
        )

    (
        user_catalog_tab,
        user_loans_tab,
        user_account_tab,
        user_chatbot_tab,
    ) = st.tabs(
        [
            "🔍 Smart Catalog & Search",
            "📖 My Borrowing",
            "🔔 Notifications & Account",
            "🤖 AI Chatbot",
        ]
    )

    with user_catalog_tab:
        st.subheader(
            "✨ Recommended For You"
        )

        recommendations = (
            agent.generate_ai_recommendations(
                books_df,
                st.session_state.userid,
            )
        )

        if recommendations.empty:
            st.info(
                "No recommendations are available yet."
            )

        else:
            recommendation_columns = st.columns(
                len(recommendations)
            )

            for index, (
                _,
                recommendation,
            ) in enumerate(
                recommendations.iterrows()
            ):
                with recommendation_columns[index]:
                    render_recommendation_card(
                        text_value(
                            recommendation["Title"],
                            "Unknown Title",
                        ),
                        text_value(
                            recommendation["Author"],
                            "Unknown Author",
                        ),
                        text_value(
                            recommendation["Genre"],
                            "General",
                        ),
                    )

        st.markdown("---")

        st.subheader(
            "🔍 Natural Language Search"
        )

        search_query = st.text_input(
            "Search by title, author, or genre",
            placeholder=(
                "Example: Java programming"
            ),
        )

        if search_query:
            search_results = (
                agent.natural_language_search(
                    books_df,
                    search_query,
                )
            )

            if search_results.empty:
                st.error(
                    "No matching books found."
                )

            else:
                for index, (
                    _,
                    book,
                ) in enumerate(
                    search_results.iterrows()
                ):
                    book_title = text_value(
                        book["Title"],
                        "Unknown Title",
                    ).strip()

                    book_author = text_value(
                        book["Author"],
                        "Unknown Author",
                    ).strip()

                    book_genre = text_value(
                        book["Genre"],
                        "General Software & AI",
                    ).strip()

                    book_count = int(
                        book["Count"]
                    )

                    is_available = book_count > 0

                    book_reviews = get_book_reviews(
                        book_title
                    )

                    ratings = []

                    for review in book_reviews:
                        try:
                            ratings.append(
                                int(
                                    review.get(
                                        "rating",
                                        0,
                                    )
                                )
                            )
                        except (
                            TypeError,
                            ValueError,
                        ):
                            pass

                    average_rating = (
                        sum(ratings)
                        / len(ratings)
                        if ratings
                        else 0.0
                    )

                    st.markdown(
                        '<div class="book-container">',
                        unsafe_allow_html=True,
                    )

                    st.subheader(
                        book_title
                    )

                    st.write(
                        f"**Author:** "
                        f"{book_author}"
                    )

                    st.write(
                        f"**Genre:** "
                        f"{book_genre}"
                    )

                    if ratings:
                        star_count = int(
                            round(
                                average_rating
                            )
                        )

                        st.write(
                            f"**Community Rating:** "
                            f"{'⭐' * star_count} "
                            f"({average_rating:.1f}/5 "
                            f"based on {len(ratings)} "
                            "reviews)"
                        )
                    else:
                        st.write(
                            "**Community Rating:** "
                            "No ratings yet "
                            "(0 reviews)"
                        )

                    if is_available:
                        render_status_badge(
                            (
                                f"● In Stock · "
                                f"{book_count} available"
                            ),
                            "success",
                        )
                    else:
                        render_status_badge(
                            "● Out of Stock",
                            "danger",
                        )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    external_links = (
                        agent.get_external_links(
                            book_title,
                            book_author,
                        )
                    )

                    link_columns = st.columns(
                        len(external_links)
                    )

                    for link_index, (
                        platform,
                        link,
                    ) in enumerate(
                        external_links.items()
                    ):
                        link_columns[
                            link_index
                        ].link_button(
                            f"🔗 {platform}",
                            link,
                        )

                    textbook_bytes, textbook_info = (
                        read_textbook_pdf(
                            book_title
                        )
                    )

                    if (
                        textbook_bytes
                        and textbook_info
                    ):
                        st.subheader(
                            "📘 Digital Textbook"
                        )

                        original_filename = text_value(
                            textbook_info.get(
                                "original_filename"
                            ),
                            "textbook.pdf",
                        )

                        render_status_badge(
                            "● Digital textbook available",
                            "success",
                        )

                        st.write(
                            f"**File:** "
                            f"{original_filename}"
                        )

                        st.download_button(
                            "⬇️ Download Textbook PDF",
                            data=textbook_bytes,
                            file_name=clean_file_name(
                                original_filename
                            ),
                            mime="application/pdf",
                            key=(
                                f"download_pdf_"
                                f"{index}_"
                                f"{book_title}"
                            ),
                            use_container_width=True,
                        )

                        with st.expander(
                            "👁️ Preview Textbook"
                        ):
                            try:
                                st.pdf(textbook_bytes)
                            except AttributeError:
                                st.info(
                                    "PDF preview is not "
                                    "supported by your "
                                    "Streamlit version."
                                )
                    else:
                        st.info(
                            "No digital textbook has been "
                            "uploaded for this book."
                        )

                    if not is_available:
                        st.warning(
                            "⚠️ This book is currently "
                            "out of stock."
                        )

                        if st.button(
                            (
                                "📌 Place Hold / Reservation "
                                f"for '{book_title}'"
                            ),
                            key=(
                                f"hold_{index}_"
                                f"{book_title}"
                            ),
                            use_container_width=True,
                        ):
                            hold_added = (
                                add_hold_request(
                                    st.session_state.username,
                                    st.session_state.userid,
                                    book_title,
                                )
                            )

                            if hold_added:
                                st.success(
                                    "Hold request registered."
                                )
                            else:
                                st.info(
                                    "You already have an active "
                                    "hold on this book."
                                )

                        add_restock_request(
                            book_title,
                            book_author,
                        )

                    with st.expander(
                        (
                            "⭐ Ratings & Reviews "
                            f"({len(book_reviews)})"
                        )
                    ):
                        if not book_reviews:
                            st.info(
                                "No reviews yet."
                            )

                        for review in book_reviews:
                            review_username = text_value(
                                review.get(
                                    "username",
                                    "Unknown User",
                                )
                            )

                            review_content = text_value(
                                review.get(
                                    "review",
                                    "",
                                )
                            )

                            review_timestamp = text_value(
                                review.get(
                                    "timestamp",
                                    "",
                                )
                            )

                            try:
                                review_rating = int(
                                    review.get(
                                        "rating",
                                        0,
                                    )
                                )
                            except (
                                TypeError,
                                ValueError,
                            ):
                                review_rating = 0

                            st.write(
                                f"**{review_username}**"
                            )

                            if review_rating > 0:
                                st.write(
                                    "⭐"
                                    * review_rating
                                )

                            st.write(
                                review_content
                            )

                            st.caption(
                                review_timestamp
                            )

                            st.markdown("---")

                        rating = st.slider(
                            "Rating",
                            min_value=1,
                            max_value=5,
                            value=5,
                            key=(
                                f"rating_{index}_"
                                f"{book_title}"
                            ),
                        )

                        review_text = st.text_area(
                            "Your Review",
                            key=(
                                f"review_text_{index}_"
                                f"{book_title}"
                            ),
                        )

                        if st.button(
                            "Submit Review",
                            key=(
                                f"submit_review_{index}_"
                                f"{book_title}"
                            ),
                        ):
                            if not review_text.strip():
                                st.warning(
                                    "Please write a review first."
                                )
                            else:
                                add_review(
                                    st.session_state.username,
                                    st.session_state.userid,
                                    book_title,
                                    rating,
                                    review_text,
                                )

                                st.success(
                                    "Review submitted "
                                    "successfully."
                                )

                                st.rerun()

    with user_loans_tab:
        st.subheader(
            "📖 Active Loans & Due Date Tracker"
        )

        borrow_records = load_borrow_records()

        active_loans = [
            record
            for record in borrow_records
            if (
                record.get("userid")
                == st.session_state.userid
                and record.get("status")
                == "Active"
            )
        ]

        if active_loans:
            for record in active_loans:
                loan_title = text_value(
                    record.get(
                        "book_title"
                    ),
                    "Unknown Book",
                )

                fine_amount, overdue_days = (
                    calculate_current_fine(
                        record.get(
                            "due_date"
                        )
                    )
                )

                st.markdown(
                    '<div class="book-container">',
                    unsafe_allow_html=True,
                )

                st.subheader(
                    loan_title
                )

                st.write(
                    f"📅 **Borrow Date:** "
                    f"{record.get('borrow_date', 'N/A')}"
                )

                st.write(
                    f"⏳ **Due Date:** "
                    f"{record.get('due_date', 'N/A')}"
                )

                if overdue_days > 0:
                    render_status_badge(
                        (
                            f"⚠️ Overdue by "
                            f"{overdue_days} day(s) · "
                            f"Fine: ${fine_amount:.2f}"
                        ),
                        "danger",
                    )
                else:
                    render_status_badge(
                        "✓ On time · No fines accrued",
                        "success",
                    )

                st.markdown(
                    "</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info(
                "You have no active borrowed books."
            )

        st.subheader(
            "📜 Borrowing History"
        )

        user_history = [
            record
            for record in borrow_records
            if record.get("userid")
            == st.session_state.userid
        ]

        if user_history:
            st.dataframe(
                pd.DataFrame(user_history),
                use_container_width=True,
            )
        else:
            st.info(
                "No borrowing history is available."
            )

        st.markdown("---")

        st.subheader(
            "📌 Your Book Holds"
        )

        current_holds = [
            hold
            for hold in load_holds()
            if hold.get("userid")
            == st.session_state.userid
        ]

        if current_holds:
            st.dataframe(
                pd.DataFrame(current_holds),
                use_container_width=True,
            )
        else:
            st.info(
                "You do not have any holds."
            )

    with user_account_tab:
        st.subheader(
            "🔔 Notification Inbox"
        )

        notifications = get_user_notifications(
            st.session_state.userid
        )

        if notifications:
            for notification in reversed(
                notifications
            ):
                timestamp = notification.get(
                    "timestamp",
                    "",
                )

                notification_message = notification.get(
                    "message",
                    "",
                )

                st.info(
                    f"[{timestamp}] "
                    f"{notification_message}"
                )

            mark_user_notifications_as_read(
                st.session_state.userid
            )
        else:
            st.info(
                "No notifications yet."
            )

    with user_chatbot_tab:
        render_library_chatbot(
            books_df
        )


# ============================================================
# ADMIN CONTROL CENTER
# ============================================================

elif app_mode == "Admin Control Center":
    render_hero(
        "Admin Management Center",
        (
            "Manage circulation, monitor inventory, "
            "upload textbooks, review reservations, "
            "and analyze library activity."
        ),
        "⚙️",
    )

    (
        admin_borrow_tab,
        admin_analytics_tab,
        admin_inventory_tab,
        admin_textbook_tab,
        admin_holds_tab,
    ) = st.tabs(
        [
            "🔄 Borrow & Return",
            "📊 Analytics",
            "📦 Inventory",
            "📚 Textbook PDFs",
            "📌 Holds & Alerts",
        ]
    )

    with admin_borrow_tab:
        st.subheader(
            "📖 Manage User Checkout & Returns"
        )

        registered_users = {
            (
                f"{user_data.get('userid', 'N/A')} "
                f"- {username}"
            ): (
                username,
                user_data.get(
                    "userid",
                    "N/A",
                ),
            )
            for username, user_data in users_db.items()
            if user_data.get("role") == "User"
        }

        if registered_users:
            selected_user_label = st.selectbox(
                "Select User",
                list(
                    registered_users.keys()
                ),
            )

            (
                borrow_username,
                borrow_userid,
            ) = registered_users[
                selected_user_label
            ]
        else:
            st.warning(
                "No registered users found."
            )

            borrow_username = st.text_input(
                "Username",
                value="user1",
            )

            borrow_userid = st.text_input(
                "User ID",
                value="user1",
            )

        book_titles = books_df[
            "Title"
        ].tolist()

        selected_book_title = st.selectbox(
            "Select Book",
            book_titles,
            key="admin_selected_book",
        )

        selected_rows = books_df[
            books_df["Title"]
            == selected_book_title
        ]

        current_stock = (
            int(
                selected_rows[
                    "Count"
                ].iloc[0]
            )
            if not selected_rows.empty
            else 0
        )

        st.info(
            f"Selected Book: "
            f"**{selected_book_title}** | "
            f"Current Stock: **{current_stock}**"
        )

        issue_column, return_column = st.columns(
            2
        )

        with issue_column:
            if st.button(
                "📉 Issue Book",
                use_container_width=True,
            ):
                if current_stock <= 0:
                    st.error(
                        "Stock is zero."
                    )
                else:
                    books_df.loc[
                        books_df["Title"]
                        == selected_book_title,
                        "Count",
                    ] -= 1

                    save_books_data(
                        books_df
                    )

                    save_borrow_record(
                        borrow_username,
                        borrow_userid,
                        selected_book_title,
                        "Borrowed",
                    )

                    st.success(
                        "Book issued successfully."
                    )

                    st.rerun()

        with return_column:
            if st.button(
                "📈 Return Book",
                use_container_width=True,
            ):
                records = load_borrow_records()

                active_loans = [
                    record
                    for record in records
                    if (
                        record.get("userid")
                        == borrow_userid
                        and record.get(
                            "book_title"
                        )
                        == selected_book_title
                        and record.get("status")
                        == "Active"
                    )
                ]

                if not active_loans:
                    st.warning(
                        "No active loan found."
                    )
                else:
                    books_df.loc[
                        books_df["Title"]
                        == selected_book_title,
                        "Count",
                    ] += 1

                    save_books_data(
                        books_df
                    )

                    save_borrow_record(
                        borrow_username,
                        borrow_userid,
                        selected_book_title,
                        "Returned",
                        active_loans[0][
                            "record_id"
                        ],
                    )

                    resolve_restock_request(
                        selected_book_title
                    )

                    st.success(
                        "Book returned successfully."
                    )

                    st.rerun()

    with admin_analytics_tab:
        st.subheader(
            "📊 Analytics & Insights"
        )

        records = load_borrow_records()

        total_books = int(
            books_df["Count"].sum()
        )

        total_titles = len(
            books_df
        )

        active_count = sum(
            1
            for record in records
            if record.get("status")
            == "Active"
        )

        overdue_count = sum(
            1
            for record in records
            if (
                record.get("status")
                == "Active"
                and get_overdue_days(
                    record.get("due_date")
                )
                > 0
            )
        )

        metric_columns = st.columns(4)

        with metric_columns[0]:
            render_stat_card(
                "Catalog titles",
                total_titles,
                "📚",
            )

        with metric_columns[1]:
            render_stat_card(
                "Available copies",
                total_books,
                "📦",
            )

        with metric_columns[2]:
            render_stat_card(
                "Active loans",
                active_count,
                "🔄",
            )

        with metric_columns[3]:
            render_stat_card(
                "Overdue loans",
                overdue_count,
                "⚠️",
            )

        if not records:
            st.info(
                "No transaction data is available yet."
            )
        else:
            records_df = pd.DataFrame(
                records
            )

            chart_one, chart_two = st.columns(
                2
            )

            with chart_one:
                st.write(
                    "##### 🏆 Most Borrowed Books"
                )

                most_borrowed = (
                    records_df["book_title"]
                    .value_counts()
                    .rename("Borrow Count")
                )

                st.bar_chart(
                    most_borrowed
                )

            with chart_two:
                st.write(
                    "##### 👥 Most Active Members"
                )

                most_active = (
                    records_df["username"]
                    .value_counts()
                    .rename("Loan Count")
                )

                st.bar_chart(
                    most_active
                )

            chart_three, chart_four = st.columns(
                2
            )

            with chart_three:
                st.write(
                    "##### 📈 Loan Status"
                )

                status_counts = (
                    records_df["status"]
                    .value_counts()
                    .rename("Count")
                )

                st.bar_chart(
                    status_counts
                )

            with chart_four:
                st.write(
                    "##### ⚠️ Low Stock Books"
                )

                low_stock = books_df[
                    books_df["Count"] < 2
                ]

                st.dataframe(
                    low_stock,
                    use_container_width=True,
                )

    with admin_inventory_tab:
        st.subheader(
            "📦 Catalog Inventory"
        )

        st.dataframe(
            books_df,
            use_container_width=True,
        )

        with st.expander(
            "Update Book Stock"
        ):
            inventory_book = st.selectbox(
                "Book",
                books_df["Title"].tolist(),
                key="inventory_book",
            )

            quantity_to_add = st.number_input(
                "Quantity to Add",
                min_value=1,
                value=1,
                step=1,
                key="quantity_to_add",
            )

            if st.button(
                "Update Inventory",
                use_container_width=True,
            ):
                books_df.loc[
                    books_df["Title"]
                    == inventory_book,
                    "Count",
                ] += int(
                    quantity_to_add
                )

                save_books_data(
                    books_df
                )

                resolve_restock_request(
                    inventory_book
                )

                st.success(
                    "Inventory updated."
                )

                st.rerun()

    with admin_textbook_tab:
        st.subheader(
            "📚 Upload Textbook Soft Copies"
        )

        st.write(
            "Upload a PDF and connect it to "
            "a book in the catalog."
        )

        selected_textbook = st.selectbox(
            "Select Book",
            books_df["Title"].tolist(),
            key="selected_textbook",
        )

        current_pdf_info = get_book_file_info(
            selected_textbook
        )

        if current_pdf_info:
            render_status_badge(
                "● PDF linked to this book",
                "success",
            )

            current_filename = current_pdf_info.get(
                "original_filename",
                "Unknown PDF",
            )

            st.write(
                f"**Current file:** "
                f"{current_filename}"
            )

            if st.button(
                "🗑️ Delete Current PDF",
                key=(
                    f"delete_current_pdf_"
                    f"{selected_textbook}"
                ),
            ):
                deleted, message = (
                    delete_uploaded_textbook(
                        selected_textbook
                    )
                )

                if deleted:
                    st.success(
                        message
                    )
                    st.rerun()
                else:
                    st.error(
                        message
                    )

        uploaded_pdf = st.file_uploader(
            "Choose PDF textbook",
            type=["pdf"],
            key=(
                f"upload_textbook_pdf_"
                f"{selected_textbook}"
            ),
        )

        if uploaded_pdf is not None:
            st.info(
                f"Selected file: "
                f"{uploaded_pdf.name}"
            )

            if st.button(
                "⬆️ Upload / Replace PDF",
                key=(
                    f"save_textbook_pdf_"
                    f"{selected_textbook}"
                ),
            ):
                uploaded, message = (
                    save_uploaded_textbook(
                        selected_textbook,
                        uploaded_pdf,
                        st.session_state.username,
                    )
                )

                if uploaded:
                    st.success(
                        message
                    )
                    st.rerun()
                else:
                    st.error(
                        message
                    )

        st.markdown("---")

        st.subheader(
            "📄 Uploaded Textbook Files"
        )

        metadata = load_textbook_metadata()

        if metadata:
            textbook_rows = []

            for file_info in metadata.values():
                textbook_rows.append(
                    {
                        "Book Title": file_info.get(
                            "book_title",
                            "Unknown",
                        ),
                        "PDF File": file_info.get(
                            "original_filename",
                            "Unknown",
                        ),
                        "Uploaded By": file_info.get(
                            "uploaded_by",
                            "Unknown",
                        ),
                        "Uploaded At": file_info.get(
                            "uploaded_at",
                            "Unknown",
                        ),
                    }
                )

            st.dataframe(
                pd.DataFrame(textbook_rows),
                use_container_width=True,
            )
        else:
            st.info(
                "No textbook PDFs have been uploaded."
            )

    with admin_holds_tab:
        st.subheader(
            "📌 Reservation Holds"
        )

        holds = load_holds()

        if holds:
            st.dataframe(
                pd.DataFrame(holds),
                use_container_width=True,
            )
        else:
            st.success(
                "No holds are currently recorded."
            )

        st.markdown("---")

        st.subheader(
            "🚨 Restock Requests"
        )

        restock_requests = load_json(
            RESTOCK_FILE,
            [],
        )

        if restock_requests:
            st.dataframe(
                pd.DataFrame(restock_requests),
                use_container_width=True,
            )
        else:
            st.success(
                "No active restock requests."
            )