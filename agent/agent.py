import os
import json
from dotenv import load_dotenv
#from groq import Groq
from google import genai
import requests
import re

API_URL = "http://127.0.0.1:8000"

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY tidak ditemukan")

#client = Groq(api_key=api_key)
client = genai.Client(api_key=api_key)


def understand_question(question):
    prompt = f"""
    Kamu adalah AI Agent untuk mencari informasi restoran dari dataset bisnis.
    Tugas kamu adalah memahami pertanyaan pengguna dan mengubahnya menjadi JSON.
    Gunakan format berikut:
    {{
        "intent": "search",
        "keyword": null,
        "rating": null,
        "rating_operator": null,
        "kelurahan": null,
        "kecamatan": null,
        "jumlah_review": null,
        "harga": null
    }}

    Jenis intent yang tersedia:

    1. "search"
        Digunakan ketika pengguna ingin mencari restoran berdasarkan kriteria tertentu.
    2. "open_until"
        Digunakan ketika pengguna menanyakan restoran yang buka sampai waktu tertentu.
    3. "max_reviews"
        Digunakan ketika pengguna ingin mengetahui restoran dengan jumlah review paling banyak.
    4. "count"
        Digunakan ketika pengguna menanyakan jumlah restoran yang sesuai dengan kriteria tertentu.

    Aturan:
    - Gunakan intent "search" jika pengguna ingin mencari atau mendapatkan daftar restoran.
    - Gunakan intent "count" jika pengguna menanyakan "berapa", "ada berapa", atau jumlah restoran.
    - Gunakan intent "max_reviews" jika pengguna mencari restoran dengan jumlah review paling banyak.
    - Gunakan intent "open_until" jika pengguna menanyakan restoran yang buka sampai waktu tertentu.
    - keyword berisi jenis atau nama bisnis yang dicari
    - rating berisi nilai rating jika disebutkan
    - rating_operator berisi ">" jika pengguna mengatakan "di atas", "lebih dari", atau "diatas"
    - rating_operator berisi ">=" jika pengguna mengatakan "minimal", "setidaknya", atau "rating 4.7 ke atas"
    - Jika tidak ada rating, rating dan rating_operator diisi null
    - kelurahan diisi jika disebutkan
    - kecamatan diisi jika disebutkan
    - jumlah_review berisi batas minimum jumlah review jika disebutkan
    - harga diisi jika disebutkan
    - Jika informasi tidak disebutkan, isi dengan null
    - Hanya keluarkan JSON, tanpa penjelasan tambahan.

    Contoh:

    Pertanyaan:
    "Cari ramen dengan rating di atas 4.7"

    Output:
    {{
        "intent": "search",
        "keyword": "ramen",
        "rating": 4.7,
        "rating_operator": ">",
        "kelurahan": null,
        "kecamatan": null,
        "jumlah_review": null,
        "harga": null,
        "jam": null
    }}

    Pertanyaan:
    "Bakmi mana yang buka sampai jam 22.00?"

    Output:
    {{
        "intent": "open_until",
        "keyword": "bakmi",
        "rating": null,
        "rating_operator": null,
        "kelurahan": null,
        "kecamatan": null,
        "jumlah_review": null,
        "harga": null,
        "jam": "22:00"
    }}

    Pertanyaan:
    "Mana restoran yang reviewnya paling banyak?"

    Output:
    {{
        "intent": "max_reviews",
        "keyword": null,
        "rating": null,
        "rating_operator": null,
        "kelurahan": null,
        "kecamatan": null,
        "jumlah_review": null,
        "harga": null,
        "jam": null
    }}

    Pertanyaan:
    "Ada berapa restoran ramen di Kelurahan Bulusan?"

    Output:
    {{
        "intent": "count",
        "keyword": "ramen",
        "rating": null,
        "rating_operator": null,
        "kelurahan": "Bulusan",
        "kecamatan": null,
        "jumlah_review": null,
        "harga": null,
        "jam": null
    }}

    Pertanyaan pengguna:
    {question}
    """

    #response = client.chat.completions.create(
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents = prompt
    )

    #result = response.choices[0].message.content
    result = response.text

    return json.loads(result)

def search_businesses(filters):
    params = {
        "keyword": filters.get("keyword"),
        "kelurahan": filters.get("kelurahan"),
        "kecamatan": filters.get("kecamatan"),
        "rating": filters.get("rating"),
        "jumlah_review": filters.get("jumlah_review"),
        "harga": filters.get("harga")
    }

    # Remove None values from params
    params = {
        key : value
        for key, value in params.items() if value is not None
    }

    response = requests.get(
        f"{API_URL}/businesses/search", params=params
    )

    response.raise_for_status()
    return response.json()

def count_businesses(filters):
    results = search_businesses(filters)
    if filters.get("rating") is not None:
        if filters.get("rating_operator") == ">":
            results = [
                r for r in results
                if r.get("rating") is not None
                and r.get("rating") > filters["rating"]
            ]
    return len(results)

def filter_open_until(results, target_time):
    target_minutes = int(target_time[:2]) * 60 + int(target_time[3:])

    filtered = []

    for restaurant in results:
        jam = restaurant.get("jam_operasional")

        if not jam or "Tidak ada info" in str(jam):
            continue

        # Cari semua pola jam seperti 09.00–21.00
        matches = re.findall(
            r"(\d{1,2})[.:](\d{2})\s*[–-]\s*(\d{1,2})[.:](\d{2})",
            str(jam)
        )

        for h1, m1, h2, m2 in matches:
            opening_minutes = int(h1) * 60 + int(m1)
            closing_minutes = int(h2) * 60 + int(m2)

            # Jika jam tutup melewati tengah malam
            if closing_minutes < opening_minutes:
                closing_minutes += 24 * 60

            # 00.00 dianggap tutup pukul 24.00
            elif closing_minutes == 0:
                closing_minutes = 24 * 60

            if closing_minutes >= target_minutes:
                filtered.append(restaurant)
                break

    return filtered

def format_results(results):
    if not results:
        return "Tidak ditemukan restoran yang sesuai."

    lines = [f"Ditemukan {len(results)} restoran:"]

    for i, restaurant in enumerate(results, start=1):
        nama = restaurant.get("nama_tempat", "Nama tidak tersedia")
        rating = restaurant.get("rating")
        review = restaurant.get("jumlah_review")

        lines.append(
            f"{i}. {nama} | Rating: {rating} | Review: {review}"
        )

    return "\n".join(lines)

def run_agent(question):
    filters = understand_question(question)

    if filters["intent"] == "count":
        total = count_businesses(filters)
        return f"Ada {total} restoran yang sesuai dengan kriteria tersebut."

    elif filters["intent"] == "search":
        results = search_businesses(filters)

        if filters.get("rating") is not None:
            if filters.get("rating_operator") == ">":
                results = [
                    r for r in results
                    if r.get("rating") is not None
                    and r.get("rating") > filters["rating"]
                ]
        return format_results(results)

    elif filters["intent"] == "max_reviews":
        results = search_businesses(filters)

        if not results:
            return "Tidak ditemukan data restoran."

        max_restaurant = max(
            results,
            key=lambda x: x.get("jumlah_review") or 0
        )
        return (
            f"Restoran dengan jumlah review terbanyak adalah "
            f"{max_restaurant.get('nama_tempat')}, "
            f"dengan {max_restaurant.get('jumlah_review')} review "
            f"dan rating {max_restaurant.get('rating')}."
        )

    elif filters["intent"] == "open_until":
        results = search_businesses(filters)

        results = filter_open_until(
            results,
            filters["jam"]
        )

        if not results:
            return "Tidak ditemukan restoran yang buka sampai waktu tersebut."

        return format_results(results)

    return "Intent belum didukung."

def generate_answer(question, results):
    prompt = f"""
    Kamu adalah AI Agent untuk mencari informasi restoran.

    pertanyaan pengguna:
    {question}

    Data restoran yang diperoleh dari API:
    {json.dumps(results, ensure_ascii=False, indent=2)}

    Jawablah pertanyaan pengguna berdasarkan DATA REStoran di atas.

    Aturan:
    - Jangan mengarang informasi.
    - Jangan menggunakan pengetahuan di luar data yang diberikan.
    - Jika data kosong, katakan bahwa tidak ditemukan data yang sesuai.
    - Jawab dalam Bahasa Indonesia.
    - Jawab dengan singkat dan jelas.

    Jawaban:
    """
    #response = client.chat.completions.create(
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents = prompt
    )

    return response.text

#if __name__ == "__main__":
#    questions = [
#        "Cari ramen dengan rating di atas 4.7",
#        "Bakmi mana yang buka sampai jam 22.00?",
#        "Mana restoran yang reviewnya paling banyak?",
#        "Ada berapa restoran ramen di Kelurahan Bulusan?"
#    ]

#    for question in questions:
#        result = understand_question(question)

#        print("\nPertanyaan:", question)
#        print("Hasil pemahaman AI:")
#        print(result)

if __name__ == "__main__":
    questions = [
        "Cari ramen dengan rating di atas 4.7",
        "Bakmi mana yang buka sampai jam 22.00?",
        "Mana restoran yang reviewnya paling banyak?",
        "Ada berapa restoran ramen di Kelurahan Bulusan?"
    ]

    for question in questions:
        answer = run_agent(question)

        print("\n" + "=" * 60)
        print("Pertanyaan:", question)
        print("Jawaban:")
        print(answer)