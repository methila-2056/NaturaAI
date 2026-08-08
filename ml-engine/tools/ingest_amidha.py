"""Ingest the Amidha Ayurveda Herb Database (CC-BY-4.0) into plants.csv.

Source: https://github.com/sciencewithsaucee-sudo/herb-database
Raw data file: data/herbs_amidha.json

The dataset provides the Sanskrit indication terms (main_indications) and
specific actions (prabhav) for each herb. Those terms are translated to
readable English benefit phrases with the curated maps below. Known-toxic
herbs (Aconite, Datura, Cannabis, Castor, etc.) are given explicit toxicity /
usage / side-effect overrides so they are never presented as safe.

Usage:
    python tools/ingest_amidha.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SOURCE_FILE = DATA_DIR / "herbs_amidha.json"
PLANTS_FILE = DATA_DIR / "plants.csv"

HEADER = [
    "name",
    "scientific_name",
    "family",
    "region",
    "benefits",
    "side_effects",
    "toxicity",
    "usage",
    "english_name",
]

DEFAULT_REGION = ""
DEFAULT_TOXICITY = "low"
DEFAULT_USAGE = "internal"

# main_indications: Ayurvedic condition -> English benefit phrase.
INDICATION_MAP = {
    "Jwara": "Helps reduce fever",
    "Vishamajwara": "Helps manage recurring fever",
    "Sannipata Jwara": "Helps manage severe fever",
    "Kasa": "Eases cough",
    "Shwasa": "Eases breathing and respiratory discomfort",
    "Hikka": "Relieves hiccups",
    "Hikkaroga": "Relieves hiccups",
    "Pratishyaya": "Relieves nasal congestion and cold",
    "Pinasa": "Relieves nasal congestion and cold",
    "Peenasa": "Relieves nasal congestion and cold",
    "Raktapitta": "Cools and soothes heat-related bleeding",
    "Prameha": "Supports urinary health (including diabetes care)",
    "Meha": "Supports urinary health",
    "Somaroga": "Supports urinary health",
    "Pandu": "Supports healthy blood levels",
    "Kamala": "Supports liver health",
    "Yakrit Roga": "Supports liver and spleen health",
    "Yakrit Vikara": "Supports liver health",
    "Yakrit-pliha Roga": "Supports liver and spleen health",
    "Pliharoga": "Supports spleen health",
    "Atisara": "Helps manage diarrhea",
    "Pravahika": "Helps manage dysentery",
    "Grahani": "Supports healthy digestion and nutrient absorption",
    "Grahi Roga": "Supports healthy digestion and nutrient absorption",
    "Ajeerna": "Aids digestion",
    "Ajirna": "Aids digestion",
    "Agnimandya": "Stimulates weak digestion",
    "Anaha": "Relieves bloating",
    "Adhmana": "Relieves flatulence and bloating",
    "Aruchi": "Improves taste and appetite",
    "Arochak": "Improves taste and appetite",
    "Vibandha": "Relieves constipation",
    "Vibhandha": "Relieves constipation",
    "Malabaddhata": "Relieves constipation",
    "Udavarta": "Supports healthy elimination",
    "Arsha": "Helps manage hemorrhoids",
    "Raktarsha": "Helps manage bleeding hemorrhoids",
    "Krimi": "Supports intestinal parasite management",
    "Krimi Vyadhi": "Supports intestinal parasite management",
    "Krimiroga": "Supports intestinal parasite management",
    "Amavata": "Supports joints in inflammatory conditions",
    "Vatarakta": "Supports joints in gout-like conditions",
    "Sandhi Vata": "Supports joint health",
    "Sandhigata Vata": "Supports joint health",
    "Sandhivata": "Supports joint health",
    "Kati Shoola": "Eases lower-back pain",
    "Katishoola": "Eases lower-back pain",
    "Gridhrasi": "Eases sciatic pain",
    "Avabahuka": "Eases shoulder pain and stiffness",
    "Pakshaghata": "Supports recovery in paralysis (adjunct care)",
    "Ardita": "Supports facial nerve comfort",
    "Dhanurvata": "Eases muscular spasms and rigidity",
    "Kampavata": "Eases tremors",
    "Vata Roga": "Soothes vata-related disorders",
    "Vata Vyadhi": "Soothes vata-related disorders",
    "Vata-vyadhi": "Soothes vata-related disorders",
    "Vatavyadhi": "Soothes vata-related disorders",
    "Vataroga": "Soothes vata-related disorders",
    "Avarana Vata": "Soothes vata-related disorders",
    "Shoola": "Relieves pain",
    "Vedana": "Relieves pain",
    "Vedana Vyadhi": "Relieves pain",
    "Shirashoola": "Relieves headache",
    "Nidranasha": "Promotes sleep",
    "Anidra": "Promotes sleep",
    "Smritidaurbalya": "Supports memory",
    "Smritinasha": "Supports memory",
    "Manasa Roga": "Supports mental calm and wellbeing",
    "Manasa Vikara": "Supports mental calm and wellbeing",
    "Manasavikara": "Supports mental calm and wellbeing",
    "Unmada": "Supports mental calm",
    "Apasmara": "Supports nervous system health",
    "Bhrama": "Relieves dizziness",
    "Mada": "Supports clarity of mind",
    "Shrama": "Relieves fatigue",
    "Daurbalya": "Builds strength",
    "Karshya": "Supports healthy weight gain",
    "Sthoulya": "Supports healthy weight management",
    "Medoroga": "Supports healthy weight management",
    "Ojo Kshaya": "Restores vitality and immunity",
    "Kshaya": "Supports recovery in debility",
    "Kshata": "Supports chest and lung recovery",
    "Kshata Kshaya": "Supports chest and lung recovery",
    "Kshata-kshaya": "Supports chest and lung recovery",
    "Urakshata": "Supports chest and lung recovery",
    "Kandu": "Relieves itching",
    "Kushta": "Supports skin health in chronic conditions",
    "Kustha": "Supports skin health in chronic conditions",
    "Kitibha": "Supports skin health in chronic conditions",
    "Shvitra": "Supports skin health in pigmentary conditions",
    "Shwitra": "Supports skin health in pigmentary conditions",
    "Vrana": "Promotes wound healing",
    "Vrana-shotha": "Promotes wound healing",
    "Vranashotha": "Promotes wound healing",
    "Vidradhi": "Supports resolution of abscesses",
    "Dadru": "Supports skin health in fungal conditions",
    "Pama": "Supports skin health in itchy eruptions",
    "Visarpa": "Supports skin health in spreading rashes",
    "Vyanga": "Supports skin clarity",
    "Amlapitta": "Supports digestion and relieves acidity",
    "Hrillasa": "Relieves nausea",
    "Chardi": "Helps manage vomiting",
    "Chhardi": "Helps manage vomiting",
    "Trishna": "Quenches excessive thirst",
    "Mukhapaka": "Supports oral health (mouth ulcers)",
    "Mukharoga": "Supports oral and throat health",
    "Dantaroga": "Supports dental health and eases toothache",
    "Dantashoola": "Supports dental health and eases toothache",
    "Dantachala": "Supports gum health",
    "Dantaphuyya": "Supports gum health",
    "Kantharoga": "Soothes the throat",
    "Swarabheda": "Supports voice and vocal clarity",
    "Akshiroga": "Supports eye health",
    "Netraroga": "Supports eye health",
    "Naktandhya": "Supports night vision",
    "Drishtiroga": "Supports vision",
    "Dristidaurbalya": "Supports vision",
    "Karna Roga": "Supports ear health",
    "Karnaroga": "Supports ear health",
    "Karnashoola": "Eases earache",
    "Daha": "Relieves burning sensation",
    "Shotha": "Reduces swelling",
    "Amashaya Shotha": "Supports stomach lining comfort",
    "Raktachapa": "Supports healthy blood pressure",
    "Raktachapa Vyadhi": "Supports healthy blood pressure",
    "Hridroga": "Supports heart health",
    "Raktadosha": "Purifies the blood",
    "Raktavikara": "Purifies the blood",
    "Raktabhishandya": "Supports blood health",
    "Ama": "Aids digestion of toxins",
    "Kleda": "Dries up excess moisture",
    "Malaria": "Supports recovery in malarial fever (adjunct care)",
    "Phiranga": "Supports skin health in chronic conditions",
    "Upadamsha": "Supports urogenital health in chronic conditions",
    "Alarka Visha": "Traditionally used in Ayurvedic management of venom exposure",
    "Sarpa-visha": "Traditionally used in Ayurvedic management of venom exposure",
    "Luta Visha": "Traditionally used in Ayurvedic management of venom exposure",
    "Kita-visha": "Traditionally used in Ayurvedic management of venom exposure",
    "Visha": "Traditionally used in Ayurvedic management of toxins",
    "Visha Roga": "Traditionally used in Ayurvedic management of toxins",
    "Visha Vyadhi": "Traditionally used in Ayurvedic management of toxins",
    "Visha-jwara": "Traditionally used in Ayurvedic management of toxins",
    "Graha": "Traditionally used for mental-emotional balance",
    "Bhutavesha": "Traditionally used for mental-emotional balance",
    "Garbhasanga": "Supports labor",
    "Mudhagarbha": "Supports labor",
    "Garbhasraava": "Supports a healthy pregnancy",
    "Garbhasraava Vyadhi": "Supports a healthy pregnancy",
    "Garbhashaya Roga": "Supports uterine health",
    "Garbhashaya Shodhana": "Supports uterine health",
    "Pradara": "Supports menstrual health (heavy bleeding)",
    "Shvetapradara": "Supports menstrual health (leukorrhea)",
    "Artava Vikara": "Supports menstrual health",
    "Kashta-shartava": "Supports menstrual health",
    "Artava Janana": "Supports regular menstruation",
    "Yonidosha": "Supports vaginal health",
    "Sutika Roga": "Supports postpartum recovery",
    "Stanya Alpata": "Supports breast milk production",
    "Stanya-kshaya": "Supports breast milk production",
    "Stanyakshaya": "Supports breast milk production",
    "Vandhyatva": "Supports fertility (traditional use)",
    "Klaibya": "Supports male reproductive health",
    "Shukra Alpata": "Supports reproductive vitality",
    "Shukra Kshaya": "Supports reproductive vitality",
    "Shukra-kshaya": "Supports reproductive vitality",
    "Shukrakshaya": "Supports reproductive vitality",
    "Palitya": "Supports natural hair color",
    "Khalitya": "Supports hair growth",
    "Keshapata": "Helps prevent hair loss",
    "Indralupta": "Supports hair regrowth",
    "Keshya": "Promotes hair health",
    "Keshya Vikara": "Promotes hair health",
    "Abhishyanda": "Supports eye comfort in inflammation",
    "Galaganda": "Supports thyroid health (traditional goiter care)",
    "Gandamala": "Supports lymphatic health",
    "Apachi": "Supports lymphatic health",
    "Shlipada": "Supports lymphatic health",
    "Granthi": "Supports glandular health",
    "Arbuda": "Supports management of growths (traditional use; not a substitute for medical care)",
    "Gulma": "Supports abdominal health",
    "Jalodara": "Supports fluid balance (adjunct care)",
    "Udara Roga": "Supports abdominal health",
    "Udara": "Supports abdominal health",
    "Udararoga": "Supports abdominal health",
    "Udara Shoola": "Eases abdominal pain",
    "Pakwashaya Shoola": "Eases intestinal pain",
    "Parshwashoola": "Eases flank pain",
    "Bhagna": "Supports bone fracture healing",
    "Bhagna-sandhana": "Supports bone fracture healing",
    "Asthi Daurbalya": "Supports bone strength",
    "Sandhishoola": "Eases joint pain",
    "Angamarda": "Relieves body ache",
}

# prabhav: specific actions -> English benefit phrase.
ACTION_MAP = {
    "Agnideepana": "Stimulates digestion and appetite",
    "Agnivardhaka": "Stimulates digestion and appetite",
    "Deepana": "Stimulates digestion and appetite",
    "Amapachana": "Aids digestion of food and toxins",
    "Pachana": "Aids digestion of food and toxins",
    "Arbudahara": "Supports management of growths (traditional use)",
    "Arshoghna": "Relieves hemorrhoids",
    "Ashmaribhedana": "Helps dissolve urinary stones",
    "Asthisandhanakara": "Supports bone healing",
    "Balya": "Builds strength and stamina",
    "Brimhana": "Nourishing and weight-building",
    "Brimhaniya": "Nourishing and weight-building",
    "Chakshushya": "Supports eye health",
    "Dahashamana": "Relieves burning sensation",
    "Dantya": "Supports teeth and gum health",
    "Garbhashaya Sankochaka": "Tones the uterus",
    "Garbhashaya Shodhaka": "Cleanses the uterus",
    "Garbhasthapana": "Supports a healthy pregnancy",
    "Grahi": "Improves nutrient absorption and helps manage diarrhea",
    "Granthihara": "Helps resolve glandular swellings",
    "Hridaya": "Supports heart health",
    "Hrudya": "Supports heart health",
    "Jivaniya": "Rejuvenating and vitalizing",
    "Jwaraghna": "Helps reduce fever",
    "Jwarahara": "Helps reduce fever",
    "Kandughna": "Relieves itching",
    "Kantya": "Supports throat and voice",
    "Kaphahara": "Reduces excess kapha",
    "Kasahara": "Relieves cough",
    "Keshya": "Promotes hair health",
    "Kledanashaka": "Dries up excess moisture",
    "Krimighna": "Antimicrobial and antiparasitic action",
    "Krimigh": "Antimicrobial and antiparasitic action",
    "Kushtaghna": "Supports skin health in chronic conditions",
    "Lekhana": "Helps reduce excess fat",
    "Madakari": "Note: has intoxicating properties - use with care",
    "Madhunashini": "Supports healthy blood sugar",
    "Pramehaghna": "Supports healthy blood sugar",
    "Medhya": "Supports memory and intellect",
    "Medohara": "Reduces excess fat",
    "Mutrala": "Promotes healthy urine flow",
    "Nidrajanaka": "Promotes sleep",
    "Nidrajanana": "Promotes sleep",
    "Pittaghna": "Soothes excess pitta",
    "Raktachapashamaka": "Supports healthy blood pressure",
    "Raktapittaghna": "Cools the blood",
    "Raktapittahara": "Cools the blood",
    "Raktaprasadak": "Purifies and tones the blood",
    "Raktaprasadana": "Purifies and tones the blood",
    "Raktashodhak": "Purifies the blood",
    "Raktashodhana": "Purifies the blood",
    "Raktastambhaka": "Helps control bleeding",
    "Raktastambhana": "Helps control bleeding",
    "Raktavardhak": "Supports healthy blood (hemoglobin)",
    "Rechana": "Mild laxative",
    "Sandhanakaraka": "Supports tissue repair and healing",
    "Sanjnasthapana": "Restores alertness and focus",
    "Sankochana": "Astringent, tones tissues",
    "Shoolaghna": "Relieves pain",
    "Shoolahara": "Relieves pain",
    "Vedanasthapana": "Relieves pain",
    "Shothahara": "Reduces swelling",
    "Shukrala": "Supports reproductive vitality",
    "Vrishya": "Supports reproductive vitality",
    "Shwasahara": "Eases breathing",
    "Stambhana": "Helps control excess discharge or bleeding",
    "Stanyajanana": "Supports breast milk production",
    "Stanyashodhana": "Purifies breast milk",
    "Trishnahara": "Quenches excessive thirst",
    "Vamana": "Emetic (professional use only)",
    "Varnya": "Promotes healthy skin complexion",
    "Vatahara": "Soothes excess vata",
    "Vatanulomana": "Supports healthy elimination of gas",
    "Virechana": "Purgative (professional use only)",
    "Vishaghna": "Supports detoxification from poisons",
    "Vranaropana": "Promotes wound healing",
    "Vranashodhak": "Cleanses wounds",
    "Yakritottejaka": "Stimulates liver function",
    "Yakrituttejaka": "Stimulates liver function",
    "Yonishodhana": "Supports uterine hygiene",
    "Rasayana": "Rejuvenating; promotes vitality and immunity",
    "rasayan": "Rejuvenating; promotes vitality and immunity",
    "Tridoshahara": "Balances all three doshas",
}

# Known-toxic herbs must never be presented as safe.
SAFETY_OVERRIDES = {
    "Vatsanabha": {
        "toxicity": "high",
        "usage": "external",
        "side_effects": [
            "Extremely toxic; only used in processed form under strict professional supervision"
        ],
    },
    "Dhattura": {
        "toxicity": "high",
        "usage": "external",
        "side_effects": ["All parts highly toxic; not for self-use"],
    },
    "Bhanga": {
        "toxicity": "high",
        "usage": "external",
        "side_effects": ["Psychoactive; not for self-medication"],
    },
    "Vacha": {
        "toxicity": "medium",
        "usage": "internal",
        "side_effects": ["Contains beta-asarone; large doses not advised"],
    },
    "Bhallataka": {
        "toxicity": "high",
        "usage": "external",
        "side_effects": ["Caustic; requires careful processing before use"],
    },
    "Ahiphena": {
        "toxicity": "high",
        "usage": "external",
        "side_effects": ["Narcotic; controlled substance; never self-use"],
    },
    "Eranda": {
        "toxicity": "high",
        "usage": "external",
        "side_effects": [
            "Seeds contain ricin (highly toxic); only processed oil should be used"
        ],
    },
    "Danti": {
        "toxicity": "medium",
        "usage": "external",
        "side_effects": ["Strong purgative; not for self-use"],
    },
    "Karanja": {
        "toxicity": "medium",
        "usage": "external",
        "side_effects": ["Seeds are toxic; external use preferred"],
    },
}

_NON_ASCII = re.compile(r"[^\x00-\x7F]")


def _clean_term(term: str) -> str:
    term = re.sub(r"\s+", " ", term).strip()
    if _NON_ASCII.search(term):
        return ""
    return term


def _strip_parenthetical(name: str) -> str:
    return re.sub(r"\s*\(.*?\)\s*", "", name).strip()


def _benefits(record: dict) -> list[str]:
    seen: list[str] = []
    for term in record.get("main_indications", []):
        clean = _clean_term(term)
        phrase = INDICATION_MAP.get(clean)
        if phrase and phrase not in seen:
            seen.append(phrase)
    for term in record.get("prabhav", []):
        clean = _clean_term(term)
        phrase = ACTION_MAP.get(clean)
        if phrase and phrase not in seen:
            seen.append(phrase)
    return seen


def _load_existing() -> list[dict]:
    if not PLANTS_FILE.exists():
        return []
    with PLANTS_FILE.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    if not SOURCE_FILE.exists():
        print(f"Missing source file: {SOURCE_FILE}")
        return 1

    with SOURCE_FILE.open(encoding="utf-8") as handle:
        records = json.load(handle)

    existing = _load_existing()
    existing_names = {row["name"].strip().lower() for row in existing}

    new_rows: list[dict] = []
    seen_names: set[str] = set()
    seen_english: set[str] = set()
    skipped_existing = 0
    skipped_dup = 0
    translated = 0

    for record in records:
        raw_name = record.get("name", "").strip()
        english_name = (record.get("english_name") or "").strip()
        if not raw_name:
            continue

        name = _strip_parenthetical(raw_name)
        if not name:
            name = raw_name

        key = name.lower()
        english_key = english_name.lower()

        if key in existing_names or english_key in existing_names:
            skipped_existing += 1
            continue
        if key in seen_names or (english_key and english_key in seen_english):
            skipped_dup += 1
            continue
        seen_names.add(key)
        if english_key:
            seen_english.add(english_key)

        benefits = _benefits(record)
        if benefits:
            translated += 1
        else:
            preview = (record.get("preview") or "").strip()
            if preview:
                benefits = [preview]
            else:
                benefits = ["Traditional Ayurvedic remedy"]

        safety = SAFETY_OVERRIDES.get(name, {})
        new_rows.append(
            {
                "name": name,
                "scientific_name": (record.get("botanical_name") or "").strip(),
                "family": (record.get("family") or "").strip(),
                "region": DEFAULT_REGION,
                "benefits": "|".join(benefits),
                "side_effects": "|".join(safety.get("side_effects", [])),
                "toxicity": safety.get("toxicity", DEFAULT_TOXICITY),
                "usage": safety.get("usage", DEFAULT_USAGE),
                "english_name": english_name,
            }
        )

    # Merge english_name into existing rows where the dataset has a match.
    by_name = {r.get("name", "").strip().lower(): r for r in records}
    for row in existing:
        source = by_name.get(row["name"].strip().lower())
        if source and not row.get("english_name", "").strip():
            row["english_name"] = (source.get("english_name") or "").strip()

    new_rows.sort(key=lambda r: r["name"].lower())
    rows = existing + new_rows

    with PLANTS_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"existing: {len(existing)} | added: {len(new_rows)} | total: {len(rows)} "
        f"| skipped-existing: {skipped_existing} | skipped-duplicates: {skipped_dup} "
        f"| with translated benefits: {translated}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
