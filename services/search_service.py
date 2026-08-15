import re
import time
import hashlib
from urllib.parse import urlparse

from config import Config
from tavily import TavilyClient

_search_cache = {}

ALLOWED_REGULATIONS = set(Config.REGULATIONS)

EDU_DOMAIN_BONUS = (
    '.edu',
    '.ac.in',
    '.ac.uk',
    '.gov',
    'university',
    'college'
)

LOW_PRIORITY_DOMAINS = (
    'amazon.',
    'ebay.',
    'facebook.',
    'twitter.',
    'instagram.',
    'youtube.com/watch'
)


# =========================================================
# SUBJECT SANITIZATION
# =========================================================

def sanitize_subject_name(subject):
    if not subject:
        raise ValueError('Subject name is required.')

    subject = str(subject).strip()

    subject = re.sub(
        r'[<>"\';\\]',
        '',
        subject
    )

    subject = re.sub(
        r'\s+',
        ' ',
        subject
    )

    if len(subject) < 2:
        raise ValueError(
            'Subject name must be at least 2 characters.'
        )

    if len(subject) > 120:
        subject = subject[:120]

    return subject


# =========================================================
# REGULATION SANITIZATION
# =========================================================

def sanitize_regulation(regulation):
    if not regulation:
        raise ValueError('Regulation is required.')

    regulation = str(regulation).strip().upper()

    regulation = re.sub(
        r'[^A-Z0-9]',
        '',
        regulation
    )

    if regulation not in ALLOWED_REGULATIONS:
        raise ValueError(
            f'Invalid regulation. Choose from: '
            f'{", ".join(Config.REGULATIONS)}'
        )

    return regulation


# =========================================================
# TEXT SANITIZATION
# =========================================================

def sanitize_text(text, max_len=500):
    if not text:
        return ''

    text = str(text).strip()

    text = re.sub(
        r'[<>"\']',
        '',
        text
    )

    if len(text) > max_len:
        text = text[:max_len] + '...'

    return text


# =========================================================
# URL SAFETY
# =========================================================

def is_safe_url(url):
    if not url or not isinstance(url, str):
        return False

    url = url.strip()
    lower = url.lower()

    if lower.startswith('javascript:'):
        return False

    if lower.startswith('data:'):
        return False

    if lower.startswith('vbscript:'):
        return False

    if not (
        lower.startswith('http://')
        or lower.startswith('https://')
    ):
        return False

    try:
        parsed = urlparse(url)

        if not parsed.netloc:
            return False

    except Exception:
        return False

    return True


# =========================================================
# CACHE
# =========================================================

def _cache_key(regulation, subject):
    raw = (
        f'{regulation}|'
        f'{subject.lower().strip()}'
    )

    return hashlib.sha256(
        raw.encode()
    ).hexdigest()


def _get_cached(key):
    entry = _search_cache.get(key)

    if entry and (
        time.time() - entry['time']
    ) < Config.SEARCH_CACHE_TTL:

        return entry['data']

    return None


def _set_cache(key, data):
    _search_cache[key] = {
        'time': time.time(),
        'data': data
    }


# =========================================================
# SEARCH QUERIES
# =========================================================

def build_search_queries(regulation, subject):
    """
    Build multiple educational search queries.
    """

    sub = subject.strip()
    reg = regulation.strip()

    return [
        f'"{sub}" "{reg}" notes PDF',
        f'"{sub}" "{reg}" study material PDF',
        f'"{sub}" "{reg}" syllabus PDF',
        f'"{sub}" "{reg}" question paper',
        f'"{sub}" "{reg}" previous question papers',
        f'"{sub}" "{reg}" important questions',
        f'"{sub}" "{reg}" lecture notes PDF',
        f'"{sub}" "{reg}" engineering notes',
        f'"{reg} {sub}" PDF',
        f'"{reg}" "{sub}" university',
        f'"{reg}" "{sub}" engineering college notes',
        f'"{sub}" "{reg}" unit notes PDF',
    ]


# =========================================================
# RESOURCE TYPE
# =========================================================

def detect_resource_type(
    title,
    url,
    snippet=''
):
    combined = (
        f'{title} '
        f'{url} '
        f'{snippet}'
    ).lower()

    if (
        '.pdf' in url.lower()
        or ' filetype:pdf' in combined
        or '[pdf]' in combined
    ):
        return 'PDF Notes'

    if any(
        k in combined
        for k in (
            'question paper',
            'question bank',
            'previous paper',
            'exam paper'
        )
    ):
        return 'Question Paper'

    if 'syllabus' in combined:
        return 'Syllabus'

    if any(
        k in combined
        for k in (
            'lecture notes',
            'unit notes',
            'study notes',
            ' notes'
        )
    ):
        return 'Notes'

    if 'assignment' in combined:
        return 'Assignment'

    return 'Study Material'


# =========================================================
# DOMAIN SCORE
# =========================================================

def _domain_score(url):
    lower = url.lower()

    score = 0

    for hint in EDU_DOMAIN_BONUS:
        if hint in lower:
            score += 25

    if '.pdf' in lower:
        score += 15

    for bad in LOW_PRIORITY_DOMAINS:
        if bad in lower:
            score -= 30

    return score


# =========================================================
# TEXT MATCH
# =========================================================

def _text_contains(text, needle):
    return needle.lower() in text.lower()


# =========================================================
# RELEVANCE SCORE
# =========================================================

def _compute_relevance_score(
    item,
    subject,
    regulation
):
    combined = (
        f'{item.get("title", "")} '
        f'{item.get("url", "")} '
        f'{item.get("description", "")}'
    )

    combined_lower = combined.lower()

    sub_lower = subject.lower()
    reg_lower = regulation.lower()

    score = _domain_score(
        item.get('url', '')
    )

    has_subject = (
        _text_contains(
            combined,
            sub_lower
        )
        or any(
            w in combined_lower
            for w in sub_lower.split()
            if len(w) > 3
        )
    )

    has_reg = _text_contains(
        combined,
        reg_lower
    )

    title_lower = item.get(
        'title',
        ''
    ).lower()

    if 'notes' in title_lower:
        score += 8

    if 'lecture' in title_lower:
        score += 6

    if 'question' in title_lower:
        score += 5

    if has_subject and has_reg:
        score += 80

    elif has_subject:
        score += 25

    if has_reg:
        score += 20

    item['regulation_match'] = has_reg
    item['score'] = score

    return score


# =========================================================
# RANK RESULTS
# =========================================================

def _rank_results(
    results,
    subject,
    regulation
):
    for item in results:
        _compute_relevance_score(
            item,
            subject,
            regulation
        )

    results.sort(
        key=lambda x: x.get(
            'score',
            0
        ),
        reverse=True
    )

    return results


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def _dedupe_results(results):
    seen = set()
    unique = []

    for item in results:

        url = item.get(
            'url',
            ''
        )

        norm = url.lower().rstrip('/')

        if (
            norm
            and norm not in seen
            and is_safe_url(url)
        ):
            seen.add(norm)
            unique.append(item)

    return unique


# =========================================================
# TAVILY SEARCH
# =========================================================

def _tavily_search(query, num=8):
    """
    Search Tavily and return normalized results.
    """

    api_key = Config.TAVILY_API_KEY

    if not api_key:
        print('TAVILY_API_KEY is missing.')
        return []

    try:

        client = TavilyClient(
            api_key=api_key
        )

        response = client.search(
            query=query,
            search_depth='basic',
            max_results=min(num, 10),
            include_answer=False,
            include_raw_content=False,
        )

        parsed = []

        for item in response.get(
            'results',
            []
        ):

            url = item.get(
                'url',
                ''
            )

            if not is_safe_url(url):
                continue

            title = sanitize_text(
                item.get(
                    'title',
                    'Untitled'
                ),
                200
            )

            snippet = sanitize_text(
                item.get(
                    'content',
                    ''
                ),
                300
            )

            source = urlparse(
                url
            ).netloc

            parsed.append({
                'title': title,
                'url': url,
                'description': snippet,
                'source': sanitize_text(
                    source,
                    80
                ),
                'type': detect_resource_type(
                    title,
                    url,
                    snippet
                ),
                'is_pdf': (
                    '.pdf'
                    in url.lower()
                ),
            })

        return parsed

    except Exception as e:

        print(
            f'TAVILY SEARCH ERROR: {e}'
        )

        return []


# =========================================================
# LOCAL UPLOADED MATERIALS
# =========================================================

def get_local_uploaded_materials(
    db_session,
    subject_name,
    regulation=None
):
    """
    Include admin-uploaded PDFs that
    match the subject name.
    """

    if not db_session:
        return []

    try:

        from database.models import (
            StudyMaterial,
            Subject
        )

        pattern = (
            f'%{subject_name}%'
        )

        materials = (
            db_session.query(
                StudyMaterial
            )
            .join(Subject)
            .filter(
                StudyMaterial.title.ilike(
                    pattern
                )
                |
                Subject.name.ilike(
                    pattern
                )
            )
            .order_by(
                StudyMaterial.upload_date.desc()
            )
            .limit(5)
            .all()
        )

        results = []

        reg_label = (
            regulation or ''
        )

        for m in materials:

            title = sanitize_text(
                m.title,
                200
            )

            if (
                reg_label
                and reg_label not in title
            ):
                title = (
                    f'{subject_name} '
                    f'{reg_label} - '
                    f'{title}'
                )

            results.append({
                'title': title,
                'url': f'/view/{m.id}',
                'description': sanitize_text(
                    m.description
                    or (
                        f'{m.material_type} - '
                        'uploaded study material'
                    ),
                    300
                ),
                'source': (
                    'SmartNotes AI '
                    '(Uploaded)'
                ),
                'type': (
                    m.material_type
                    or 'PDF Notes'
                ),
                'is_pdf': True,
                'is_local': True,
                'score': 55,
                'regulation_match': bool(
                    reg_label
                ),
            })

        return results

    except Exception as e:

        print(
            f'LOCAL MATERIAL SEARCH ERROR: {e}'
        )

        return []


# =========================================================
# MAIN SEARCH FUNCTION
# =========================================================

def search_study_materials(
    regulation,
    subject_name,
    db_session=None,
    use_cache=True
):
    """
    Main study material search function.

    Searches Tavily using regulation + subject
    and also checks locally uploaded materials.
    """

    regulation = sanitize_regulation(
        regulation
    )

    subject_name = sanitize_subject_name(
        subject_name
    )

    cache_key = _cache_key(
        regulation,
        subject_name
    )

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    if use_cache:

        cached = _get_cached(
            cache_key
        )

        if cached is not None:
            return cached

    # -----------------------------------------------------
    # TAVILY API CHECK
    # -----------------------------------------------------

    if not Config.TAVILY_API_KEY:

        local = get_local_uploaded_materials(
            db_session,
            subject_name,
            regulation
        )

        if local:

            _set_cache(
                cache_key,
                local
            )

            return local

        raise ValueError(
            'Web search is not configured. '
            'Set TAVILY_API_KEY in your .env file.'
        )

    # -----------------------------------------------------
    # WEB SEARCH
    # -----------------------------------------------------

    all_results = []

    queries = build_search_queries(
        regulation,
        subject_name
    )

    for query in queries:

        print(
            f'Searching Tavily: {query}'
        )

        results = _tavily_search(
            query,
            num=6
        )

        all_results.extend(
            results
        )

        if len(all_results) >= 36:
            break

    # -----------------------------------------------------
    # PROCESS RESULTS
    # -----------------------------------------------------

    all_results = _dedupe_results(
        all_results
    )

    all_results = _rank_results(
        all_results,
        subject_name,
        regulation
    )

    # -----------------------------------------------------
    # LOCAL MATERIALS
    # -----------------------------------------------------

    local = get_local_uploaded_materials(
        db_session,
        subject_name,
        regulation
    )

    for loc in local:

        if not any(
            r.get('url')
            == loc.get('url')
            for r in all_results
        ):
            all_results.insert(
                0,
                loc
            )

    # -----------------------------------------------------
    # FINAL RESULTS
    # -----------------------------------------------------

    final = all_results[:25]

    _set_cache(
        cache_key,
        final
    )

    return final


# =========================================================
# AI WEB CONTEXT
# =========================================================

def build_web_context_for_ai(
    results,
    max_items=6
):
    if not results:
        return ''

    parts = []

    for i, r in enumerate(
        results[:max_items],
        1
    ):

        parts.append(
            f'[Resource {i}: '
            f'{r.get("title", "")} | '
            f'{r.get("source", "")} | '
            f'Type: {r.get("type", "")}]\n'
            f'{r.get("description", "")}'
        )

    return '\n\n'.join(parts)