import pandas as pd
import re
from playwright.sync_api import sync_playwright

def extract_coordinates(url):
    match = re.search(r'!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)', url)
    if not match:
        return None, None
    latitude = float(match.group(1))
    longitude = float(match.group(2))
    return latitude, longitude

def clean_text(text):
    if not text:
        return None

    # Ganti newline/tab menjadi spasi
    text = re.sub(r"[\n\t]+", " ", text)

    # Hapus karakter non-alfanumerik yang muncul di awal
    text = re.sub(r"^[^\w]+", "", text)

    # Rapikan spasi dan baris baru
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def scrape_business_detail(page, business):

    # BUKA HALAMAN DETAIL BISNIS
    page.goto(business["url"], wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    #CEK BUTTON YANG ADA DI HALAMAN DETAIL BISNIS
    #buttons = page.get_by_role("button")

    #print("\n=== SEMUA BUTTON ===")

    #for i in range(buttons.count()):
    #    text = clean_text(buttons.nth(i).inner_text())

    #    if text:
    #        print(i, repr(text))

    # =========================
    # NAMA
    # =========================
    nama = page.get_by_role("heading").first.inner_text().strip()

    # =========================
    # RATING
    # =========================
    rating_element = page.locator("span").filter(
        has_text=re.compile(r"^\d,\d$")
    ).first

    rating_text = rating_element.inner_text().strip()
    rating = float(rating_text.replace(",", "."))

    # =========================
    # ALAMAT
    # =========================
    alamat_element = page.get_by_role(
        "button",
        name=re.compile("^Alamat:")
    ).first

    alamat = clean_text(alamat_element.inner_text())

    # =========================
    # JUMLAH REVIEW
    # =========================
    review_element = page.get_by_role(
        "img",
        name=re.compile(r"^\d[\d.]* ulasan$")
    )

    if review_element.count() > 0:
        review_text = review_element.first.get_attribute("aria-label")

        review_match = re.search(
            r"(\d[\d.]*)",
            review_text or ""
        )

        if review_match:
            jumlah_review = int(
            review_match.group(1).replace(".", "")
        )
        else:
            jumlah_review = None
    else:
        jumlah_review = None

    # =========================
    # JENIS BISNIS
    # =========================
    jenis_element = page.get_by_role("button")

    jenis_bisnis = None

    for i in range(jenis_element.count()):
        text = clean_text(jenis_element.nth(i).inner_text())

        if text == "Lihat foto":
            # Mulai mencari setelah "Lihat foto"
            for j in range(i + 1, jenis_element.count()):
                kandidat = clean_text(jenis_element.nth(j).inner_text())

                # Berhenti ketika sudah masuk tombol Rute
                if kandidat == "Rute":
                    break

                # Cari kandidat kategori
                if kandidat:
                    jenis_bisnis = kandidat
                    break

            break

    # =========================
    # JAM OPERASIONAL
    # =========================
    jam_element = page.get_by_role(
        "button",
        name=re.compile("Jam")
    ).first

    jam_operasional = None

    if jam_element.count() > 0:

        # Klik bagian jam agar tabel jadwal muncul
        jam_element.click()

        page.wait_for_timeout(1000)

        jam_rows = page.get_by_role("row")

        jam_data = []

        for i in range(jam_rows.count()):

            row = jam_rows.nth(i)

            text = clean_text(
                row.inner_text()
            )

            if text:
                jam_data.append(text)

        jam_operasional = " | ".join(jam_data)

    else:
        jam_operasional = None

    # =========================
    # TELEPON
    # =========================
    telepon_element = page.get_by_role(
        "button",
        name=re.compile("^Telepon:")
    ).first

    if telepon_element.count() > 0:
        telepon = clean_text(
            telepon_element.inner_text()
        )
    else:
        telepon = None

    # =========================
    # HARGA
    # =========================
    harga_element = page.get_by_role(
        "button",
        name=re.compile(r"Rentang harga|Rp")
    ).first

    if harga_element.count() > 0:

        harga = harga_element.get_attribute(
            "aria-label"
        )

        if harga:
            harga_match = re.search(
            r"Rp\s*[\d.]+(?:–|-)[\d.]+",
            harga
        )

            if harga_match:
                harga = harga_match.group(0).replace("\xa0", " ").strip()
            else :
                harga = None
        else:
            harga = None

    else:
        harga = None

    # =========================
    # WEBSITE
    # =========================
    website = None

    website_link = page.locator(
        'a[href^="http"]'
    ).filter(
        has_text=re.compile(
            "Situs|Website",
            re.IGNORECASE
        )
    ).first

    if website_link.count() > 0:
        website = website_link.get_attribute("href")

    # =========================
    # HASIL
    # =========================
    return {

        "nama_tempat": nama,

        "alamat": alamat,

        "jenis_bisnis": jenis_bisnis,

        "rating": rating,

        "jumlah_bintang": 5,

        "jumlah_review": jumlah_review,

        "jam_operasional": jam_operasional,

        "harga": harga,

        "latitude": business["latitude"],

        "longitude": business["longitude"],

        "telepon": telepon,

        "website": website
    }
    

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) #headless artinya browser berjalan di latar belakang tanpa menampilkan jendela isual/grafis di layar laptop
    page = browser.new_page()
    page.goto("https://www.google.com/maps")
    
    print("Google Maps sudah terbuka di browser.")
    
    #Menampung semua bisnis dari bakmi + Ramen
    businesses = []

    #COLLECTOR BAKMI + RAMEN
    for keyword in ["bakmi", "ramen"]:
        print("\n" + "="*50)
        print(f"Mencari bisnis dengan keyword: {keyword} kecamatan tembalang")
        print("="*50)

        search_url = (
            "https://www.google.com/maps/search/" 
            + keyword + " kecamatan tembalang"
        )

        page.goto(
            search_url,
            wait_until="domcontentloaded"
        )

        page.wait_for_timeout(5000)  # Tunggu 5 detik agar halaman sepenuhnya dimuat

        input(
            f"Silakan scroll hasil {keyword} "
            "sebanyak yang kamu mau, lalu tekan Enter..." 
        )

        # Ambil semua link bisnis yang sudah dimuat
        page_links = page.locator(
            'a[href*="/maps/place"]'
        )

        print(
            f"Jumlah bisnis yang ditemukan untuk {keyword}:",
            page_links.count()
        )

        #TAMBAHKAN BISNIS =================================================
        for i in range(page_links.count()):
            link = page_links.nth(i)

            name = link.inner_text().strip()
            href = link.get_attribute("href")

            if not href:
                continue

            lat, lon = extract_coordinates(href)

            businesses.append({
                    "name": name,
                    "url": href,
                    "latitude": lat,
                    "longitude": lon
                })

        print(f"Total bisnis unik sementara: {len(businesses)}")
    # =========================
    # HASIL COLLECTOR
    # =========================

    print("\n" + "=" * 50)
    print("HASIL COLLECTOR")
    print("=" * 50)

    print(
        "Total bisnis unik Bakmi + Ramen:",
        len(businesses)
    )

    for i, business in enumerate(businesses[:10]):
        print(
            i + 1,
            business["name"]
    )
    #Melihat semua link yang ada di halaman
    #links = page.get_by_role("link")
    #page_links = page.locator('a[href*="/maps/place"]')
    #print("Jumlah link:", links.count())
    #print("jumlah bisnis:", page_links.count())
    
    #for i in range(min(20, links.count())): 20 batas maksimal data yang ingin di proses/ambil sedangkan fungsi min untuk mencari nilai terkecil dari 2 parameter yaitu 20 dan jumlah link yang ada di halaman
    #for i in range (links.count()):    
    #    link = links.nth(i)
    #    href= link.get_attribute("href")
    #    if href and "/maps/place" in href: #untuk memfilter link yang mengandung "/maps/place"
    #        print("Link ke-", i+1, ":", href)
    #businesses = []
    #for i in range(page_links.count()):
    #    link = page_links.nth(i)

    #    name = link.inner_text().strip()
    #    href = link.get_attribute("href")

    #    lat, lon = extract_coordinates(href)

    #    businesses.append({
    #        "name": name, 
    #        "url": href,
    #        "latitude": lat,
    #        "longitude": lon
    #    })

    #melihat strukturnya untuk memastikan data yang diambil sudah benar
    #for business in businesses:
    #    lat, lon = extract_coordinates(business["url"])

    #    business["latitude"] = lat
    #   business["longitude"] = lon

    #print("Total bisnis:", len(businesses))
    #print("Data Awal:", businesses[:3])

    #test_business = businesses[0] 
    #page.goto(test_business["url"], wait_until="domcontentloaded")

    #nama = page.locator("h1").first
    #print("Nama:", nama.inner_text())

    #rating = page.locator('[aria-label*="4,4"]')
    #print("Jumlah elemen rating:", rating.count())

    #page.wait_for_timeout(5000)  # Tunggu 5 detik agar halaman sepenuhnya dimuat
    #print("Nama bisnis:", test_business["name"])
    #print("URL halaman:", page.url)

    #print("=== ISI HALAMAN ===")
    #print(page.locator("body").inner_text()[:5000])

    #UJI BISNIS ==================================================
    print(f"\nMengambil detail {len(businesses)} bisnis...")

    all_data = []

    for i, business in enumerate(businesses):
        print(f"\n{'='*50}")
        print(f"TEST BISNIS KE-{i+1}")
        print(f"{'='*50}")

        try :
            detail = scrape_business_detail(
                page,
                business
            )

            print(detail)
            all_data.append(detail)

        except Exception as e:
            print(f"❌ GAGAL: {business['name']}")
            print(f"Error: {e}")

    #SIMPAN CSV
    df = pd.DataFrame(all_data)
    df.to_csv(
        "data/raw_data_tanpa_duplikat.csv",
        index=False,
        encoding="utf-8"
    )

    print("\nData berhasil disimpan ke data/raw_data.csv")
    print("Jumlah data berhasil:", len(df))

    #    print("\n=== HASIL DETAIL ===")

    #    for key, value in detail.items():
    #        print(f"{key}: {value}")


    #input("Tekan Enter untuk menutup browser...")

    browser.close()
