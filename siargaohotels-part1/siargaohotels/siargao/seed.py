"""Seed the database with the content of the live siargaohotels.ph.

    flask --app wsgi seed             # first load (skips anything that already exists)
    flask --app wsgi seed --refresh   # also overwrite existing listings/posts with this content
    flask --app wsgi import-wp        # then pull the original WordPress text for posts, pages and listings
"""
from . import content as C
from .db import execute, insert, query, update

UP = C.UP

ISLA_LINAW_REVIEWS = [
    ("michael meshulam", "Best Host in Siargao – Above and Beyond Hospitality!", "2026-02-18",
     "Best host in siargao , made sure i have everything and helped with my lost baggage until found . Also invited me to lovely "
     "dinner with all the family . Such a pleasant experience , recommend", (5, 5, 5, 5, 5, 5)),
    ("Alex Bompoil", "Cozy, Peaceful Stay with a Helpful Owner", "2026-02-15",
     "We stayed here for 6 nights. It was a pleasant surprise; prices are very competitive. The owner helps you with everything "
     "(laundry, airport transfer). The place is cozy and very peaceful, not too close to the road, which made it a quiet place. "
     "There were a few roosters, but nothing inconvenient. Free refills of fresh water!\nThe room was neither small nor big, with "
     "AC inside. The bathroom was a bit too small, with no hot water. There were a few things that needed repairing inside the "
     "bathroom, but everything was fine (for example, the toilet flush worked only every other time, and the showerhead was "
     "broken).\nI recommend this place to stay !", (4, 4, 5, 4, 5, 4)),
    ("Marton", "We felt very looked after", "2026-02-14",
     "Highly recommended! Great location, close to restaurants and beach. The room has everything you need. Large bed, air "
     "conditioning and bathroom. Amazing host, helped us with all our errands and organization", (5, 5, 5, 5, 5, 5)),
]

FAQS = [
    ("Where is Siargao located in the Philippines?",
     "<p>Siargao is a tear-shaped island in Surigao del Norte, Mindanao, Philippines, located on the edge of the Pacific Ocean. Known as the <strong>“Surfing Capital of the Philippines,”</strong> Siargao is famous for its perfect waves, white-sand beaches, and lush tropical landscapes. Visitors often stay in <strong>General Luna Siargao hotels</strong>, <strong>Cloud 9 Siargao hotels</strong>, or <strong>affordable hotels in Siargao</strong> to experience the best of the island.</p>"),
    ("What is Siargao famous for?",
     "<p>Siargao is best known for <strong>Cloud 9</strong>, one of the world’s top surf breaks, attracting surfers from around the globe. The island also offers breathtaking lagoons, tidal pools, island hopping adventures, and vibrant nightlife in General Luna. Travelers can choose from <strong>top hotels in Siargao Island, Philippines</strong>, <strong>cheap hotels in Siargao Island</strong>, or <strong>Siargao homestays in General Luna</strong> to suit all budgets while enjoying local attractions.</p>"),
    ("When is the best time to visit Siargao?",
     "<p>The best time to visit is from <strong>March to October</strong> for sunny days, calm seas, and ideal island-hopping weather. Surf enthusiasts should plan their trip between <strong>September and November</strong>, the peak surf season at Cloud 9 Siargao hotels. Booking early during these months is recommended for <strong>General Luna Siargao hotels</strong> or <strong>affordable hotels in Siargao</strong>.</p>"),
    ("How do you get to Siargao?",
     "<p>Most travelers fly to <strong>Sayak Airport (IAO) via Manila or Cebu</strong>. From the airport, it’s a 40–45 minute drive to General Luna Siargao hotels and popular surf spots like Cloud 9. Ferry services from Surigao City are also available. Once on the island, visitors can rent scooters, tricycles, or vans to reach cheap hotels in Siargao Island and other attractions.</p>"),
    ("Is Siargao beginner-friendly for surfing?",
     "<p>Yes. While <strong>Cloud 9</strong> is ideal for advanced surfers, beginner-friendly spots like Jacking Horse, Guiwan, and Daku Reef are perfect for learning. Many surf schools in General Luna provide lessons and board rentals. Staying in <strong>Cloud 9 Siargao hotels</strong>, <strong>General Luna Siargao hotels</strong>, or <strong>Siargao homestays in General Luna</strong> ensures easy access to surf lessons and rental shops.</p>"),
    ("What are the must-visit attractions in Siargao?",
     "<p>Top attractions include:</p><ul><li><strong>Cloud 9 boardwalk</strong> for iconic surf views and sunsets.</li><li><strong>Sugba Lagoon</strong> for paddleboarding and swimming.</li><li><strong>Magpupungko Rock Pools</strong>, a natural tidal pool attraction.</li><li><strong>Sohoton Cove</strong>, a spectacular area in Bucas Grande with caves, jellyfish lagoons, and limestone formations.</li><li>Island hopping to <strong>Naked Island, Daku Island, and Guyam Island</strong>.</li><li>Scenic drives along <strong>Maasin Coconut Road</strong> lined with coconut palms.</li></ul>"),
    ("Is Siargao safe for tourists?",
     "<p>Yes. Siargao is definitely very safe, especially in areas like General Luna, which is well-lit and tourist-friendly. Standard safety practices, such as securing valuables and checking weather conditions during monsoon season, are recommended. Travelers staying in <strong>General Luna Siargao hotels</strong> or <strong>affordable hotels in Siargao</strong> can explore the island with peace of mind.</p>"),
    ("How early should I book my hotel in Siargao?",
     "<p>Booking early is highly recommended, especially during <strong>peak surf season (September to November)</strong> and holidays. Ideally, reserve your accommodation <strong>2–4 months in advance</strong>. Options include <strong>Cloud 9 Siargao hotels</strong>, <strong>General Luna Siargao hotels</strong>, <strong>affordable hotels in Siargao</strong>, <strong>cheap hotels in Siargao Island</strong>, <strong>top hotels in Siargao Island, Philippines</strong>, and <strong>Siargao homestays in General Luna</strong>. Early booking ensures proximity to surf schools, restaurants, and attractions like Cloud 9, Sugba Lagoon, and Sohoton Cove.</p>"),
]


CARS_PAGE = """
<h2>Motorcycle &amp; Car Rentals in Siargao</h2>
<p>Looking to explore Siargao Island at your own pace? Whether you prefer the comfort of a car or the freedom of a motorcycle, we offer <strong>motorcycle and car rental in Siargao</strong> to suit your travel style. Rent a vehicle with us and discover the beauty of this tropical paradise on your terms.</p>
<h3>Why Choose Our Car &amp; Motorcycle Rental Service?</h3>
<ul>
<li><strong>Affordable Rates:</strong> Enjoy competitive prices for both <strong>car rental in Siargao</strong> and <strong>motorbike rental Siargao</strong>, so you can make the most of your trip without exceeding your budget.</li>
<li><strong>Variety of Options:</strong> Choose from a range of <strong>cars for rent in Siargao Island</strong>, including spacious SUVs, reliable sedans, or versatile vans. We also offer a selection of motorcycles for rent, including scooters, mopeds, and dirt bikes, perfect for any adventure.</li>
<li><strong>Easy Booking Process:</strong> Booking a vehicle is quick and simple. Whether you need to <strong>rent a car in Siargao</strong> or opt for <strong>Siargao motorcycle rental</strong>, our online booking system ensures a smooth experience, letting you focus on your travels.</li>
<li><strong>Reliable &amp; Well-Maintained Fleet:</strong> We maintain our fleet of <strong>cars for rent in Siargao Island</strong> and motorcycles to the highest standards, ensuring your safety and comfort as you explore the island’s attractions.</li>
<li><strong>Flexible Rental Terms:</strong> We offer flexible rental periods, from daily to weekly or monthly options, to suit your schedule.</li>
</ul>
<img src="https://siargaohotels.ph/wp-content/uploads/2026/02/Car-For-Rent-in-Siargao-Island-768x678.jpg" alt="Car For Rent in Siargao Island" loading="lazy">
<h3>Our Vehicles for Rent in Siargao</h3>
<h4>Car Rentals:</h4>
<ul><li><strong>SUVs &amp; 4x4s:</strong> Perfect for off-road adventures, these vehicles are ideal for exploring Siargao’s rugged terrain and hidden spots.</li>
<li><strong>Sedans &amp; Hatchbacks:</strong> Fuel-efficient and comfortable, these cars are great for leisurely island drives and scenic coastal routes.</li>
<li><strong>Vans &amp; Minivans:</strong> Whether you're traveling with a group or family, our spacious vans ensure a comfortable ride for everyone.</li></ul>
<h4>Motorcycle Rentals:</h4>
<ul><li><strong>Scooters &amp; Mopeds:</strong> Perfect for solo travelers or couples, these easy-to-ride bikes give you the freedom to cruise around Siargao with ease.</li>
<li><strong>Dirt Bikes:</strong> For the more adventurous at heart, our dirt bikes are great for off-road exploration and taking on Siargao's hidden trails.</li></ul>
<h3>Convenient Delivery &amp; Pickup Service</h3>
<p>We know your time is valuable, so we offer <strong>car delivery</strong> and <strong>pickup services</strong> directly to your hotel, airport, or any location on the island. Whether you need a car for rent in Siargao Island or a Siargao motorcycle rental, we’ll bring the vehicle to you for added convenience.</p>
<h3>How to Rent a Car or Motorcycle in Siargao</h3>
<ol><li><strong>Choose Your Vehicle:</strong> Browse our selection of <strong>cars for rent in Siargao</strong> or <strong>motorcycles for rent in Siargao</strong>.</li>
<li><strong>Book Online or Call:</strong> Reserve your vehicle online or give us a call to confirm your rental.</li>
<li><strong>Pick-Up &amp; Go:</strong> We’ll arrange a convenient pick-up time and location.</li></ol>
<img src="https://siargaohotels.ph/wp-content/uploads/2026/02/Car-Rental-Siargao-768x307.jpg" alt="Car Rental Siargao" loading="lazy">
<h3>Explore Siargao Your Way</h3>
<p><strong>Siargao</strong> is best experienced at your own pace. From the surf capital of Cloud 9 to the stunning lagoons and hidden beaches, there’s so much to discover. With our <strong>motorcycle</strong> or <strong>car rental in Siargao</strong>, you can easily visit all the must-see spots and uncover some off-the-beaten-path treasures.</p>
"""


ABOUT = f"""
<img src="{UP}2025/11/About-Siargao-Hotels.jpg" alt="About Siargao Hotels" loading="lazy">
<h2>We Live Here, We Stay Here</h2>
<p><strong>SiargaoHotels.ph</strong> is a Siargao travel assistant built by locals and travelers who live, work and explore on the island.
We bring hotels, homestays, house rentals, island tours and car and motorbike rentals together in one place, so you can plan your
whole trip without juggling a dozen websites and chats.</p>
<h3>What we do</h3>
<ul>
<li><strong>Curated stays</strong> — from simple homestays in General Luna to lagoon-side cottages in Socorro, every property is checked by our team.</li>
<li><strong>Trusted local tours</strong> — island hopping, land tours, Sohoton Cove and surf trips run by vetted local operators.</li>
<li><strong>Getting around</strong> — cars, vans and scooters with delivery to your hotel, the airport or Dapa Port.</li>
<li><strong>Honest advice</strong> — practical, up-to-date tips from people who are on the island every day.</li>
</ul>
<img src="{UP}2025/11/Siargao-Hotels-San-Isidro.jpg" alt="Siargao Hotels San Isidro" loading="lazy">
<h3>Book directly with locals</h3>
<p>When you book through us you deal directly with Siargao-based partners, and our team is a message away before and during your trip.
SiargaoHotels.ph is operated by IAO Booking Services.</p>
<img src="{UP}2025/11/Siargao-Hotels-Club-Tara.jpg" alt="Siargao Hotels Club Tara" loading="lazy">
"""

PENDING = ("<p>We're updating this page. For any questions, please contact us at "
           "<a href=\"mailto:info@siargaohotels.ph\">info@siargaohotels.ph</a> or +639458259355.</p>")

PAGES = [
    ("car-and-motorcycle-rentals", "Affordable Car For Rent In Siargao Island - Car Rental Siargao", CARS_PAGE,
     "Looking for reliable car rental in Siargao? Explore Siargao Island with ease by renting a car. Choose from a variety of "
     "vehicles available for rent, perfect for your island adventure. Book your car for rent in Siargao today!"),
    ("about-us", "About Us", ABOUT, "SiargaoHotels.ph — your Siargao travel assistant for hotels, tours, rentals and cars."),
    ("privacy-policy", "Privacy Policy", PENDING, ""),       # replaced by `flask import-wp`
    ("terms-and-conditions", "Terms & Conditions", PENDING, ""),
    ("partner-policy", "Partner Policy", PENDING, ""),
]


def _row(table, slug, kind=None):
    if kind:
        return query(f"SELECT id FROM {table} WHERE slug = ? AND kind = ?", (slug, kind), one=True)
    return query(f"SELECT id FROM {table} WHERE slug = ?", (slug,), one=True)


def _upsert(table, data, refresh, kind=None):
    row = _row(table, data["slug"], kind)
    if row:
        if refresh:
            update(table, row["id"], data)
        return row["id"], False
    return insert(table, data), True


def _post_body(slug, teaser):
    links = [v for k, v in C.POST_LINKS.items() if k in slug] or [C.POST_LINKS["hotel"]]
    cta = " ".join(f'<a class="btn btn-brand me-2 mb-2" href="{u}">{t}</a>' for u, t in links)
    return f"<p class=\"lead\">{teaser}</p><p>{cta}</p>"


def run_seed(refresh=False):
    loc = {}
    for L in C.LOCATIONS:
        gallery = "".join(f'<img src="{UP}{p}" alt="{L["name"]}, Siargao" loading="lazy">' for p in L["gallery"])
        data = {"slug": L["slug"], "name": L["name"], "zipcode": L["zipcode"], "position": L["position"],
                "image_url": L["image_url"], "description": L["description"] + f'<div class="loc-gallery">{gallery}</div>'}
        loc[L["slug"]], _ = _upsert("locations", data, refresh)

    # reversed: the live site lists newest first, and our "New" sort is by id
    for h in reversed(C.HOTELS):
        h = dict(h)
        rooms = h.pop("rooms", [])
        data = {"kind": "hotel", "price_unit": "night", "location_id": loc[h.pop("location")],
                "map_query": f"{h['title']}, {h['address']}", **h}
        lid, created = _upsert("listings", data, refresh, "hotel")
        if created or refresh:
            execute("DELETE FROM rooms WHERE listing_id = ?", (lid,))
            for r in rooms:
                insert("rooms", {"listing_id": lid, "price": 0, **r})
        if created and h["slug"] == "isla-linaw-siargao":
            for name, title, date, body, s in ISLA_LINAW_REVIEWS:
                insert("reviews", {"listing_id": lid, "name": name, "title": title, "body": body, "approved": 1,
                                   "created_at": date + " 12:00:00", "cleanliness": s[0], "comfort": s[1],
                                   "location": s[2], "facilities": s[3], "staff": s[4], "value": s[5]})

    for t in reversed(C.TOURS):
        t = dict(t)
        data = {"kind": "tour", "price_unit": "person", "location_id": loc[t.pop("location")], **t}
        _upsert("listings", data, refresh, "tour")

    for c in reversed(C.CARS):
        c = dict(c)
        airport = c.pop("airport", False)
        data = {
            "kind": "car", "price_unit": "day", "slug": c["slug"], "title": c["title"], "category": c["category"],
            "seats": c["seats"], "transmission": c["transmission"], "price": c["price"],
            "location_id": loc[c["location"]], "image_url": UP + c["image"],
            "gallery": "\n".join(UP + p for p in c["gallery"]),
            "address": "Sayak Airport, Del Carmen, Siargao" if airport else "General Luna, Siargao",
            "summary": c["about"], "description": f"<p>{c['about']}</p>",
            "features": C.CAR_FEATURES, "start_time": C.CAR_HOURS, "rate_tiers": c.get("rate_tiers", ""),
            "reminders": "\n".join(C.CAR_REQUIREMENTS), "policies": c["policies"],
        }
        _upsert("listings", data, refresh, "car")

    if not query("SELECT id FROM faqs LIMIT 1"):
        for pos, (q, a) in enumerate(FAQS):
            insert("faqs", {"question": q, "answer": a, "position": pos})

    cats = {}
    for slug, name in C.CATEGORIES:
        cats[slug], _ = _upsert("categories", {"slug": slug, "name": name}, refresh)
    for slug, title, cat, img, date, teaser in reversed(C.POSTS):
        data = {"slug": slug, "title": title, "category_id": cats[cat], "image_url": UP + img, "excerpt": teaser,
                "published_at": f"{date} 09:00:00", "body": _post_body(slug, teaser), "seo_description": teaser}
        _upsert("posts", data, refresh)

    for slug, title, body, seo in PAGES:
        _upsert("pages", {"slug": slug, "title": title, "body": body.strip(), "seo_description": seo}, refresh)
