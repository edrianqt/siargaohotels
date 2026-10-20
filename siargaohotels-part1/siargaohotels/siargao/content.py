"""Listing, location and blog content gathered from siargaohotels.ph (October 2026).

Facts (prices, rooms, facilities, rules, inclusions, rates, photos) mirror the live site.
Descriptions are short write-ups of each listing; `flask import-wp` replaces them with the
original WordPress text where the REST API exposes it.
"""

UP = "https://siargaohotels.ph/wp-content/uploads/"


def g(*paths):
    """Gallery helper: relative upload paths -> newline separated full URLs."""
    return "\n".join(UP + p for p in paths)


def lines(*items):
    return "\n".join(items)


# --------------------------------------------------------------------------- locations
LOCATIONS = [
    {"slug": "general-luna-siargao", "name": "General Luna", "zipcode": "8419", "position": 1,
     "image_url": UP + "2025/05/General-Luna-Siargao-Philippines.jpg",
     "gallery": ["2025/05/general-luna-siargao-cloud-9.jpg", "2025/05/hotels-in-General-Luna-Siargao-Island-1.jpg",
                 "2025/05/Cloud-9-Siargao-Island-Philippines.jpg"],
     "description": "<p>General Luna is Siargao's tourism hub and home of the famous <strong>Cloud 9</strong> surf break. "
                    "Most hotels, homestays, cafés, restaurants and nightlife are along Tourism Road, and it is the "
                    "jump-off point for island hopping to Naked, Daku and Guyam Islands.</p>"},
    {"slug": "dapa-siargao", "name": "Dapa", "zipcode": "8417", "position": 2,
     "image_url": UP + "2025/05/Dapa-Siargao-Island.jpg",
     "gallery": ["2025/05/Dapa-Siargao.png", "2025/05/I-Love-Dapa-Siargao-Island.png"],
     "description": "<p>Dapa is Siargao's main port town, where ferries from Surigao City arrive. It is a short ride "
                    "from General Luna and a practical base for travelers arriving by sea.</p>"},
    {"slug": "socorro-siargao", "name": "Socorro", "zipcode": "8416", "position": 3,
     "image_url": UP + "2025/05/Socorro-Bucas-Grande-Island-Philippines.jpg",
     "gallery": ["2025/05/Sohoton-Cove-National-Park.jpg", "2025/05/Sohoton-Jellyfish-Sanctuary.jpg"],
     "description": "<p>Socorro covers Bucas Grande Island, home of <strong>Sohoton Cove National Park</strong> — "
                    "limestone cliffs, hidden lagoons, caves and the stingless jellyfish sanctuary.</p>"},
    {"slug": "del-carmen-siargao", "name": "Del Carmen", "zipcode": "8418", "position": 4,
     "image_url": UP + "2025/06/Sugba-Lagoon-Siargao.jpg",
     "gallery": ["2025/06/Del-Carmen-Mangrove.jpg", "2025/06/del-carmen-siargao-tourist-spots.jpg"],
     "description": "<p>Del Carmen is where Sayak Airport (IAO) is, and it is known for <strong>Sugba Lagoon</strong> "
                    "and one of the largest mangrove forests in the Philippines.</p>"},
    {"slug": "pilar-siargao", "name": "Pilar", "zipcode": "8420", "position": 5,
     "image_url": UP + "2025/11/Magpupungko-Rock-Pools-Pilar-Siargao.jpg",
     "gallery": ["2025/11/Pilar-Siargao-Magpupungko-Rock-Pools.jpg", "2025/11/Magpupungko-Rock-Pools-And-Flats.jpg"],
     "description": "<p>Pilar is a quiet coastal town best known for the <strong>Magpupungko Rock Pools</strong>, "
                    "natural tidal pools that appear at low tide.</p>"},
    {"slug": "san-isidro-siargao", "name": "San Isidro", "zipcode": "8421", "position": 6,
     "image_url": UP + "2025/11/pacifico-beach-siargao.jpg",
     "gallery": ["2025/11/pacifico-siargao-island.jpg", "2025/11/pacifico-beach-resort-siargao.jpg",
                 "2025/11/Pacifico-Surf-Siargao.jpg"],
     "description": "<p>San Isidro, in northern Siargao, is home to <strong>Pacifico Beach</strong> — a long, "
                    "uncrowded stretch of sand with consistent surf and a laid-back pace.</p>"},
]

# --------------------------------------------------------------------------- hotels
NO_REFUND = "<p><strong>Refund</strong> — Payments are non-refundable but can be rebooked once with prior notice (subject to availability).</p>"

HOTELS = [
    {
        "slug": "isla-linaw-siargao", "title": "Isla Linaw Siargao", "location": "general-luna-siargao",
        "address": "Tourism Road, 8419 General Luna, Philippines", "price": 1450,
        "image_url": UP + "2026/02/Isla-Linaw-Siargao-9-900x600.jpg",
        "gallery": g("2026/02/Isla-Linaw-Siargao-931x594.jpg", "2026/02/Isla-Linaw-Siargao-1-931x594.jpg",
                     "2026/02/Isla-Linaw-Siargao-3-931x594.jpg", "2026/02/Isla-Linaw-Siargao-9-900x600.jpg"),
        "imported_rating": 4.8, "imported_reviews": 3, "owner_name": "Isla Linaw Siargao", "min_stay": 2,
        "description": (
            "<p><strong>Isla Linaw Siargao</strong> is a tranquil retreat located in the heart of <strong>General Luna, Siargao "
            "Island</strong>, offering guests a peaceful escape. This boutique resort features comfortable accommodations with views "
            "of the island’s natural beauty, providing a serene atmosphere for relaxation. Ideal for travelers seeking a quiet "
            "getaway, Isla Linaw offers easy access to Siargao’s top attractions, including pristine beaches and world-class surf "
            "spots. With its intimate setting and attentive service, <strong>Isla Linaw Siargao</strong> is the perfect destination "
            "for those looking to experience the island’s charm in a serene and laid-back environment.</p>"),
        "facilities": lines(
            "Accommodation Facilities: Air-Conditioned, Complimentary Toiletries, Free Wi-Fi, Private Bathroom, Room Service",
            "Dining & Food Facilities: Breakfast Service",
            "Recreational Facilities: Garden",
            "Convenience & Guest Services: Laundry / Dry Cleaning",
            "Safety & Accessibility: CCTV / Security"),
        "check_in": "1:00 PM", "check_out": "11:00 AM",
        "policies": ("<p><strong>Children &amp; Beds</strong> — Children not allowed. Cribs and extra beds aren't available at this property.</p>"
                     "<p><strong>Age Restriction</strong> — The minimum age for check-in is 18.</p>"
                     "<p><strong>Pets</strong> — Pets are not allowed.</p><p><strong>Parties</strong> — Parties/events are not allowed.</p>"),
        "rooms": [{"slug": "double-room-with-private-bathroom", "name": "Double Room with Private Bathroom", "size_m2": 12,
                   "beds": 1, "max_adults": 2, "price": 1450, "image_url": UP + "2026/02/Isla-Linaw-Siargao-5-800x600.jpg"}],
    },
    {
        "slug": "cuadro-inn", "title": "Cuadro Inn", "location": "general-luna-siargao",
        "address": "Tourism Road, Poblacion 2, General Luna, Philippines", "price": 1200,
        "image_url": UP + "2026/02/Cuadro-Inn-Homestay-Standard-Room-900x600.jpg",
        "gallery": g("2026/02/Cuadro-Inn-Homestay-Standard-Room-931x594.jpg", "2026/02/Cuadro-Inn-Homestay-3-931x594.jpg",
                     "2026/02/Cuadro-Inn-Homestay-1-931x594.jpg", "2026/02/Cuadro-Inn-Homestay-4-931x594.jpg",
                     "2026/02/Cuadro-Inn-Homestay-6-931x594.jpg"),
        "imported_rating": 5, "imported_reviews": 1, "owner_name": "Cuadro Inn",
        "summary": "Budget-friendly inn on Tourism Road, close to General Luna's beaches and restaurants.",
        "description": ("<p><strong>Cuadro Inn</strong> is a budget-friendly stay on Tourism Road in central General Luna, "
                        "welcoming solo travelers, couples and families alike. Rooms come with air-conditioning, a flat-screen "
                        "TV, a refrigerator and free Wi-Fi, and guests can use the shared kitchen, garden and terrace.</p>"
                        "<p>Beaches, cafés, restaurants and the island's main attractions are an easy ride away, and the inn "
                        "offers Double, Quadruple and Family rooms for groups of every size.</p>"),
        "facilities": lines(
            "Accommodation Facilities: Air-Conditioned, Flat-Screen TV, Free Wi-Fi, Private Bathroom, Refrigerator, Towel",
            "Dining & Food Facilities: Kitchen",
            "Recreational Facilities: Garden, Terrace",
            "Convenience & Guest Services: Parking"),
        "check_in": "2:00 PM", "check_out": "11:59 AM",
        "policies": ("<p><strong>Children</strong> — Children of any age are welcome. Children aged 9 and up are charged as adults.</p>"
                     "<p><strong>Pets</strong> — Pets are allowed at no extra charge.</p>"
                     "<p><strong>Smoking</strong> — Smoking is not allowed.</p>"),
        "rooms": [
            {"slug": "double-room", "name": "Double Room", "size_m2": 18, "beds": 1, "max_adults": 2,
             "image_url": UP + "2026/02/Cuadro-Inn-Homestay-Standard-Room-800x600.jpg"},
            {"slug": "quadruple-room", "name": "Quadruple Room", "size_m2": 20, "beds": 2, "max_adults": 4,
             "image_url": UP + "2026/02/Cuadro-Inn-Homestay-Quadruple-Room-800x600.jpg"},
            {"slug": "family-room-2", "name": "Family Room", "size_m2": 25, "beds": 5, "max_adults": 10,
             "image_url": UP + "2026/02/Cuadro-Inn-Homestay-Family-Room-1-800x600.jpg"},
        ],
    },
    {
        "slug": "jeannine-sunvibes-inn", "title": "Jeannine Sunvibes Inn", "location": "general-luna-siargao",
        "address": "Poblacion 5 General Luna, General Luna, Philippines", "price": 1250,
        "image_url": UP + "2026/02/Jeannine-Sunvibes-Inn-1-900x600.jpg",
        "gallery": g(*[f"2026/02/Jeannine-Sunvibes-Inn-{i}-931x594.jpg" for i in range(1, 6)]),
        "imported_rating": 4.8, "imported_reviews": 2, "owner_name": "Jeannine Sunvibes Inn",
        "summary": "No-frills guesthouse in a quiet part of General Luna; exclusive use for up to 40 guests.",
        "description": ("<p><strong>Jeannine's Sunvibes Inn</strong> is a simple, budget-friendly guesthouse and homestay in "
                        "a quiet coastal part of General Luna. Its private rooms suit couples, friends and families, with "
                        "air-conditioning, towels, Wi-Fi and access to a shared kitchen.</p>"
                        "<p>General Luna's surf breaks, cafés and restaurants are close by, and the whole property can be "
                        "booked for exclusive use by groups of up to 40 guests.</p>"),
        "facilities": lines(
            "Accommodation Facilities: Air-Conditioned, Free Wi-Fi, Private Bathroom, Refrigerator, Towel",
            "Dining & Food Facilities: Kitchen"),
        "check_in": "2:00 PM", "check_out": "11:59 AM", "policies": NO_REFUND,
        "rooms": [{"slug": "standard-room", "name": "Standard Room", "size_m2": 20, "beds": 2, "max_adults": 2,
                   "image_url": UP + "2026/02/Jeannine-Sunvibes-Inn-Room-4-800x600.jpg"}],
    },
    {
        "slug": "lagoon-tiktikan-and-sohoton-gamay-resort", "title": "Lagoon Tiktikan and Sohoton Gamay Resort",
        "location": "socorro-siargao", "address": "Tiktikan Lagoon Cottages, Socorro, Surigao del Norte, Philippines",
        "price": 2750, "phone": "09308727757", "image_url": UP + "2026/02/tiktikan-lagoon-1-900x600.jpg",
        "gallery": g("2026/02/tiktikan-lagoon-1-931x594.jpg", "2026/02/tiktikan-lagoon-2-931x594.jpg",
                     *[f"2026/02/tiktikan-{i}-931x594.jpg" for i in (2, 3, 5, 4, 6, 7, 8)]),
        "owner_name": "Lagoon Tiktikan Resort",
        "summary": "Lagoon-side cottages on Bucas Grande Island, beside Tiktikan Lagoon and Sohoton Gamay.",
        "description": ("<p>Set on <strong>Bucas Grande Island</strong> in Socorro, this resort sits beside Tiktikan Lagoon, "
                        "one of the lagoons of the Sohoton islets. Guests can swim, kayak and paddle right from the "
                        "cottages in calm, clear water.</p>"
                        "<p>The neighbouring <strong>Sohoton Gamay</strong> area adds cliff jumping and boat trips, and the "
                        "resort has a pool, café, meeting rooms and a 24-hour front desk.</p>"),
        "facilities": lines(
            "Accommodation Facilities: Air-Conditioned, Complimentary Toiletries, Free Wi-Fi, Private Bathroom, Room Service",
            "Dining & Food Facilities: 24-Hour Room Service, Breakfast Service, Café / Coffee Shop",
            "Recreational Facilities: Swimming Pool",
            "Business & Event Facilities: Conference / Meeting Rooms, Projector & Audiovisual Equipment",
            "Convenience & Guest Services: 24-Hour Front Desk",
            "Safety & Accessibility: CCTV / Security, Fire Safety Systems"),
        "check_in": "8:00 AM", "check_out": "8:00 AM",
        "rooms": [{"slug": "bangus-room", "name": "Bangus Room", "size_m2": 20, "beds": 10, "max_adults": 10,
                   "image_url": UP + "2026/02/82d2eab3-cb19-4c7e-a884-ae161fe99de9-800x600.jpg"}],
    },
    {
        "slug": "goodlife-siargao-hostel", "title": "Goodlife Siargao Hostel", "location": "general-luna-siargao",
        "address": "Tourism Road, Purok 5, General Luna, Surigao del Norte, Philippines", "price": 1675,
        "image_url": UP + "2026/02/Goodlife-Siargao-Hostel-900x600.jpg",
        "gallery": g("2026/02/Goodlife-Siargao-Hostel-931x594.jpg",
                     *[f"2026/02/Goodlife-Siargao-Hostel-{i}-931x594.jpg" for i in range(1, 6)]),
        "imported_rating": 5, "imported_reviews": 2, "owner_name": "Goodlife Siargao Hostel",
        "summary": "Social hostel on Tourism Road with free breakfast and an on-site restaurant.",
        "description": ("<p><strong>Goodlife Siargao Hostel</strong> is a lively, welcoming base on Tourism Road for solo "
                        "travelers and groups. It offers clean dorms and private rooms, roomy common areas and friendly "
                        "staff, with the beaches and surf spots of General Luna close by.</p>"
                        "<p><strong>Free breakfast</strong> is included, and there is an on-site restaurant.</p>"),
        "facilities": lines(
            "Accommodation Facilities: Air-Conditioned, Free Wi-Fi, Private Bathroom, Towel",
            "Dining & Food Facilities: Breakfast Service, On-Site Restaurant",
            "Safety & Accessibility: CCTV / Security"),
        "check_in": "2:00 PM", "check_out": "11:59 AM", "policies": NO_REFUND,
        "rooms": [
            {"slug": "standard-room-2", "name": "Standard Room", "size_m2": 12, "beds": 1, "max_adults": 2,
             "image_url": UP + "2026/02/Goodlife-Siargao-Hostel-Standard-Room-800x600.jpg"},
            {"slug": "family-room", "name": "Family Room", "size_m2": 14, "beds": 2, "max_adults": 4,
             "image_url": UP + "2026/02/Goodlife-Siargao-Hostel-Family-Room-800x600.jpg"},
        ],
    },
    {
        "slug": "yara-homestay-siargao", "title": "Yara Homestay Siargao", "location": "general-luna-siargao",
        "address": "Macalaya Rd, Purok 5, General Luna, Surigao del Norte, Philippines", "price": 2800,
        "phone": "+639175551233", "image_url": UP + "2026/02/Both2-1920w-900x600.jpeg",
        "gallery": g("2026/02/Over-headRooms-1920w-931x594.jpeg", "2026/02/Reception1-1920w-931x594.jpeg",
                     "2026/02/Lenaimainview-1920w-931x594.jpeg", "2026/02/Yara-Homestay-Pool-931x594.jpg"),
        "imported_rating": 5, "imported_reviews": 3, "owner_name": "Yara Homestay Siargao", "min_stay": 2,
        "summary": "Homestay with a pool in central General Luna, minutes from the surf breaks.",
        "description": ("<p><strong>Yara Homestay Siargao</strong> is in the heart of General Luna, a few minutes from the "
                        "famous surf breaks and white-sand beaches. Its airy rooms, swimming pool and relaxed tropical "
                        "setting come with genuine local hospitality.</p>"
                        "<p>Rooms have air-conditioning, a flat-screen TV and safe, and there is a bar, kitchen, parking and "
                        "a 24-hour front desk.</p>"),
        "facilities": lines(
            "Accommodation Facilities: Air-Conditioned, Flat-Screen TV, Free Wi-Fi, Private Bathroom, Room Service, Safe Deposit Box",
            "Dining & Food Facilities: 24-Hour Room Service, Bar / Lounge, Kitchen",
            "Recreational Facilities: Swimming Pool",
            "Convenience & Guest Services: 24-Hour Front Desk, Parking",
            "Safety & Accessibility: CCTV / Security"),
        "check_in": "11:59 AM", "check_out": "10:00 AM",
        "policies": ("<p><strong>Rebooking</strong> — Must be requested 2 weeks before arrival and can be done once. "
                     "Further date changes cost ₱500.</p>"
                     "<p><strong>Late check-out</strong> — ₱500 per 30 minutes.</p>"
                     "<p><strong>Refund</strong> — Payments are non-refundable.</p>"),
        "rooms": [{"slug": "regular-room-accommodation", "name": "Regular Room Accommodation", "size_m2": 20, "beds": 2,
                   "max_adults": 4, "image_url": UP + "2026/02/Yara-Homestay-Room-Picture-1-800x600.jpg"}],
    },
    {
        "slug": "ambungan-homestay", "title": "Ambungan Homestay", "location": "general-luna-siargao",
        "address": "Poblacion 1, General Luna, Surigao del Norte, Philippines", "price": 2400,
        "image_url": UP + "2026/02/Ambungan-Homestay-Family-Room-900x600.jpg",
        "gallery": g("2026/02/Ambungan-Homestay-931x594.jpg", "2026/02/Ambungan-Homestay-1-931x594.jpg",
                     "2026/02/Ambungan-Homestay-2-931x594.jpg"),
        "imported_rating": 5, "imported_reviews": 2, "owner_name": "Ambungan Homestay",
        "summary": "Cozy family-run homestay in Poblacion 1 with Family and Quadruple rooms.",
        "description": ("<p><strong>Ambungan Homestay</strong> is a cozy, budget-friendly homestay in central General Luna. "
                        "Comfortable rooms, a peaceful setting and a shared kitchen and terrace make it a good fit for both "
                        "short visits and longer stays.</p>"
                        "<p>Local eateries and the town's main attractions are nearby, and parking is available.</p>"),
        "facilities": lines(
            "Accommodation Facilities: Air-Conditioned, Free Wi-Fi, Private Bathroom, Refrigerator, Towel",
            "Dining & Food Facilities: Kitchen",
            "Recreational Facilities: Terrace",
            "Convenience & Guest Services: Parking"),
        "check_in": "3:00 PM", "check_out": "11:00 AM",
        "policies": ("<p><strong>Pets</strong> — Pets are not allowed.</p><p><strong>Smoking</strong> — Smoking is not allowed.</p>"
                     "<p><strong>Parties</strong> — Parties/events are not allowed.</p>"),
        "rooms": [
            {"slug": "quadruple-room-ambungan-homestay", "name": "Quadruple Room", "size_m2": 20, "beds": 2, "max_adults": 4,
             "image_url": UP + "2026/02/Ambungan-Homestay-Quadruple-Room-800x600.jpg"},
            {"slug": "family-room-ambungan-homestay", "name": "Family Room", "size_m2": 22, "beds": 3, "max_adults": 6,
             "image_url": UP + "2026/02/Ambungan-Homestay-Family-Room-800x600.jpg"},
        ],
    },
]

# --------------------------------------------------------------------------- tours
ISLAND_INCLUSIONS = lines(
    "Free drone shots", "Boat transfers", "Licensed local tour guide", "Life vests for all guests",
    "Hotel pickup and drop-off within General Luna", "Boodle fight lunch")
ISLAND_EXCLUSIONS = lines(
    "Personal expenses and optional purchases", "Snacks and drinks beyond the boodle fight lunch",
    "Tips for the boat crew and guide", "Any activity or service not listed under inclusions")
ISLAND_REMINDERS = (
    "Bring sunscreen, swimwear, a towel, extra clothes, slippers and cash for personal expenses",
    "The tour is weather-dependent and may be rescheduled or refunded in bad weather or rough seas",
    "Children 1–2 years join free, 3–5 years pay half rate, 6 and up pay full rate")
LAND_INCLUSIONS = lines(
    "Pick-up and drop-off from your accommodation", "Air-conditioned transport between destinations",
    "Local tour guide", "Entrance fees to included attractions",
    "Life jackets and basic safety gear for swimming spots", "Bottled water", "Free lunch")
LAND_EXCLUSIONS = lines("Personal expenses", "Optional activities (kayaking, paddleboarding, etc.)",
                        "Tips for the guide or driver (optional)")
LAND_HIGHLIGHTS = lines("Sugba Lagoon (swimming)", "Magpupungko Rock Pools", "Maasin River boat cruise",
                        "Coconut View Deck", "Siargao Mountain View", "Secret Beach", "Free lunch with a local guide")
LAND_REMINDERS = ("Bring swimwear, a towel, sunscreen, a hat, comfortable shoes and a camera or phone",
                  "Family-friendly — let us know about any special needs in advance",
                  "Pick-up is from accommodation in General Luna; ask us if you're staying elsewhere")
SOHOTON_INCLUSIONS = lines(
    "Hotel pick-up and drop-off", "Boat transfer from Siargao to Bucas Grande Island", "DOT community tour guide",
    "Boodle fight lunch", "All entrance and environmental fees", "Small boat with local guides for Sohoton Cove",
    "Snorkeling gear", "Van transfer Socorro to Dagatan Bay (land schedule)", "Canter boat (island schedule)")
SOHOTON_REMINDERS = (
    "Leave no trace — no plastics, please", "Bring your own water, snacks, an extra shirt and snorkeling gear",
    "Keep your phone on so the guide can reach you", "Be on time and follow the guide's schedule",
    "No same-day or on-the-spot cancellations — same-day cancellation incurs a 50% fee")
SOHOTON_HIGHLIGHTS = lines(
    "Sohoton Cove, Bucas Grande", "Hagukan Cave (Snoring Cave)", "Diving Cave (cliff diving)",
    "Stingless jellyfish lagoon", "Tiktikan / Nakiauit (island schedule)", "Club Tara Resort viewing (island schedule)",
    "Dagatan Bay Resort & Viewing Lagoon (land schedule)")

TOURS = [
    {
        "slug": "siargao-private-land-tour", "title": "Siargao Private Land Tour", "location": "general-luna-siargao",
        "address": "General Luna, Siargao Island, Philippines", "price": 8000, "duration": "Whole Day",
        "category": "private", "imported_rating": 5, "imported_reviews": 1, "start_time": "8:00 AM (ends 4–5 PM)",
        "image_url": UP + "2026/02/Siargao-Maasin-River-Tour-Done-Shot-900x600.jpg",
        "gallery": g(*[f"2026/02/{n}-870x555.jpg" for n in (
            "Siargao-Maasin-River-Tour", "Siargao-Land-Tour-Magpupungko-Rock-Pools", "Sugba-Lagoon-Siargao-Land-Tour",
            "Siargao-Maasin-River-Tour-Done-Shot", "Siargao-Land-Tour-Mountain-Road", "Siargao-Land-Tour-Guests",
            "Siargao-Island-Coconut-View-Deck")]),
        "summary": "Your own vehicle and guide for Siargao's best land spots in one day.",
        "description": ("<p>See Siargao's best-known inland and coastal sights in one relaxed day with your own vehicle and "
                        "guide: swim in Sugba Lagoon and the Magpupungko Rock Pools, cruise the Maasin River and stop at "
                        "the island's favourite viewpoints.</p><p>It's an easy, good-value option for couples, families and "
                        "small groups who want to set their own pace. The price per person drops as your group grows.</p>"),
        "highlights": LAND_HIGHLIGHTS, "inclusions": LAND_INCLUSIONS, "exclusions": LAND_EXCLUSIONS,
        "reminders": lines("A ₱8,000 downpayment secures the booking; the balance depends on group size", *LAND_REMINDERS),
        "rate_tiers": "2: 5798\n3: 4498\n4: 4098\n5: 3398\n6: 2998\n7: 2698\n8: 2498\n9: 2398\n10: 2298",
    },
    {
        "slug": "3d2n-all-inclusive-package", "title": "3D2N ALL-INCLUSIVE Package", "location": "general-luna-siargao",
        "address": "General Luna, Siargao Island, Philippines", "price": 3998, "duration": "3 Days 2 Nights",
        "category": "", "featured": 1, "imported_rating": 5, "imported_reviews": 2,
        "image_url": UP + "2026/02/Siargao-SALE-900x600.jpg",
        "gallery": g(*[f"2026/02/{n}-870x555.jpg" for n in (
            "Tri-Island-Tour-Package", "Daku-Island-Boddle-Fight", "Boddle-Fight-in-Daku-Island",
            "Tri-Island-Tour-Package-Guests", "Corregidor-Island-Siargao-1", "Corregidor-Island-Siargao")]),
        "summary": "Hotel, island hopping and airport transfers in one package — limited to 200 slots.",
        "description": ("<p>Our all-in Siargao package bundles a private air-conditioned hotel room, a full island-hopping "
                        "tour and round-trip airport transfers from <strong>₱3,998 per person</strong>. The island day "
                        "includes a boodle fight lunch and free drone shots.</p><p>Only the first <strong>200 slots</strong> "
                        "get this rate, with travel dates open through December 2026.</p>"),
        "itinerary": lines("Day 1: Arrival, airport transfer and free time",
                           "Day 2: Island hopping — Naked Island, Daku Island (boodle fight lunch), Guyam Island and Secret Island, with free drone shots",
                           "Day 3: Free time and departure transfer"),
        "highlights": lines("Private air-conditioned hotel room with private CR and strong internet",
                            "Free boodle fight lunch and drone shots on the island tour", "Round-trip airport van transfers",
                            "Entrance, environmental, docking and cottage fees covered"),
        "inclusions": lines("Hotel accommodation (choice of 12 partner properties)", "Complete island-hopping tour",
                            "Round-trip airport van and seaport transfers", "Boodle fight lunch on tour",
                            "Free drone shots on the island tour", "Tourism boat for the day tour",
                            "All entrance, environmental, docking and cottage fees", "Tour guide and boat crew"),
        "exclusions": "Airfare",
        "reminders": lines("Limited to the first 200 slots", "Reserve with a 50% payment upfront",
                           "Travel dates open through December 2026, with rebooking available"),
    },
    {
        "slug": "siargao-tri-island-corregidor-island-private-tour",
        "title": "Siargao Tri-Island + Corregidor Island Private Tour", "location": "general-luna-siargao",
        "address": "General Luna, Siargao Island, Philippines", "price": 8000, "duration": "9-10 Hours",
        "category": "private", "imported_rating": 5, "imported_reviews": 2, "start_time": "7:00 AM (ends 4–5 PM)",
        "image_url": UP + "2026/02/Daku-Island-Siargao-Philippines-900x600.jpg",
        "gallery": g(*[f"2026/02/{n}-870x555.jpg" for n in (
            "Guyam-Island", "Naked-Island-Siargao", "Daku-Island-Boddle-Fight", "Boddle-Fight-in-Daku-Island",
            "Tri-Island-Tour-Package", "Corregidor-Island-Siargao-1", "Corregidor-Island-Siargao",
            "Tri-Island-Tour-Package-Guests")]),
        "summary": "Private boat to Naked, Daku, Guyam and Corregidor Islands with boodle fight lunch.",
        "description": ("<p>Hop between four islands on a private boat: the sandbar of <strong>Naked Island</strong>, coconut-"
                        "lined <strong>Daku Island</strong> for a beach lunch, the reefs around <strong>Guyam Island</strong> "
                        "and the quiet shores of <strong>Corregidor Island</strong>.</p><p>Hotel pick-up in General Luna, "
                        "lunch and all island fees are included.</p>"),
        "highlights": lines("Naked Island sandbar for swimming and sunbathing", "Daku Island beach lunch and cottage",
                            "Snorkeling over Guyam Island's coral reefs", "Quiet beaches on Corregidor Island",
                            "Scenic boat ride between islands"),
        "inclusions": lines(ISLAND_INCLUSIONS, "Cottage use at Daku and Corregidor Islands",
                            "Island entrance and environmental fees", "Docking fees"),
        "exclusions": ISLAND_EXCLUSIONS,
        "reminders": lines("A ₱8,000 downpayment secures the booking; the balance depends on group size", *ISLAND_REMINDERS),
        "rate_tiers": "4: 3998\n5: 3798\n6: 3398\n7: 2998\n8: 2798\n9: 2498\n10: 2398",
    },
    {
        "slug": "sohoton-cove-joiner-tour", "title": "Sohoton Cove Joiner Tour", "location": "socorro-siargao",
        "address": "Socorro, Surigao del Norte, Philippines", "price": 2699, "duration": "Whole Day",
        "category": "joiner", "imported_rating": 5, "imported_reviews": 3, "start_time": "Pick-up 7:00–8:00 AM",
        "image_url": UP + "2026/01/sohoton-cove-26-900x600.jpg",
        "gallery": g("2026/01/sohoton-cove-26-870x555.jpg", "2026/01/sohoton-cove-18-870x555.jpg",
                     "2026/01/sohoton-national-park-2-870x555.jpg", "2026/01/sohoton-cove-44-870x555.jpg",
                     "2026/01/sohoton-cove-42-870x555.jpg"),
        "summary": "Shared day trip to Sohoton Cove's lagoons, caves and stingless jellyfish.",
        "description": ("<p>A full-day eco-adventure to <strong>Bucas Grande Island</strong>, a protected area of clear "
                        "lagoons, limestone cliffs, caves and stingless jellyfish. Join other travelers on a shared boat "
                        "with a DOT community guide.</p><p>Great for nature lovers and anyone who wants an active but "
                        "relaxed day away from General Luna.</p>"),
        "highlights": SOHOTON_HIGHLIGHTS, "inclusions": SOHOTON_INCLUSIONS, "reminders": lines(*SOHOTON_REMINDERS),
    },
    {
        "slug": "siargao-tri-island-corregidor-island-joiner-tour",
        "title": "Siargao Tri-Island + Corregidor Island Joiner Tour", "location": "general-luna-siargao",
        "address": "General Luna, Siargao Island, Philippines", "price": 2198, "duration": "9-10 Hours",
        "category": "joiner", "imported_rating": 5, "imported_reviews": 1, "start_time": "7:00 AM (ends 4–5 PM)",
        "image_url": UP + "2026/02/Guyam-Island-900x600.jpg",
        "gallery": g(*[f"2026/02/{n}-870x555.jpg" for n in (
            "Guyam-Island", "Daku-Island-Siargao-Philippines", "Naked-Island-Siargao", "Daku-Island-Boddle-Fight",
            "Boddle-Fight-in-Daku-Island", "Tri-Island-Tour-Package-Guests", "Tri-Island-Tour-Package",
            "Corregidor-Island-Siargao-1", "Corregidor-Island-Siargao")]),
        "summary": "Shared island hopping to Naked, Daku, Guyam and Corregidor with lunch on Daku.",
        "description": ("<p>A one-day shared island-hopping trip to <strong>Naked, Daku, Guyam and Corregidor Islands</strong>, "
                        "with a boodle fight lunch on Daku. A great way for solo travelers and small groups to see "
                        "Siargao's islands with fellow travelers.</p>"),
        "highlights": lines("Naked Island sandbar with clear water", "Daku Island coconut trees, beach lunch and cottage",
                            "Snorkeling over Guyam Island's coral reefs", "Quiet, untouched Corregidor Island",
                            "Hotel pick-up and drop-off within General Luna"),
        "inclusions": lines(ISLAND_INCLUSIONS, "Cottage use at Daku and Corregidor Islands",
                            "Island entrance and environmental fees", "Docking fees"),
        "exclusions": ISLAND_EXCLUSIONS, "reminders": lines(*ISLAND_REMINDERS),
    },
    {
        "slug": "siargao-joiner-land-tour", "title": "Siargao Joiner Land Tour", "location": "general-luna-siargao",
        "address": "Siargao Island, Philippines", "price": 1998, "duration": "Whole Day", "category": "joiner",
        "imported_rating": 5, "imported_reviews": 3, "start_time": "8:00 AM (ends 4–5 PM)",
        "image_url": UP + "2025/11/Magpupungko-Rock-Pools-And-Flats-900x600.jpg",
        "gallery": g("2025/11/Magpupungko-Rock-Pools-And-Flats-870x555.jpg", "2025/06/Sugba-Lagoon-Siargao-870x555.jpg",
                     "2025/11/Leaning-Palm-Tree-Maasin-Siargao-870x555.jpg",
                     "2026/02/Siargao-Island-Coconut-View-Deck-870x555.jpg",
                     "2026/02/Aerial-View-on-Straight-Road-Siargao-Island-870x555.jpg"),
        "summary": "Shared land tour: Sugba Lagoon, Magpupungko, Maasin River and viewpoints.",
        "description": ("<p>A guided day around Siargao's top land spots — swim at <strong>Sugba Lagoon</strong> and the "
                        "<strong>Magpupungko Rock Pools</strong>, cruise the <strong>Maasin River</strong>, take in the "
                        "Coconut View Deck and Mountain View, and finish at Secret Beach.</p><p>A budget-friendly choice for "
                        "solo travelers, couples and small groups; private customised tours are also available.</p>"),
        "highlights": LAND_HIGHLIGHTS, "inclusions": LAND_INCLUSIONS, "exclusions": LAND_EXCLUSIONS,
        "reminders": lines(*LAND_REMINDERS),
    },
    {
        "slug": "siargao-tri-island-private-tour", "title": "Siargao Tri-Island Private Tour",
        "location": "general-luna-siargao", "address": "General Luna, Siargao Island, Philippines", "price": 8000,
        "duration": "6-7 Hours", "category": "private", "imported_rating": 5, "imported_reviews": 3,
        "start_time": "8:00 AM (ends 2–3 PM)",
        "image_url": UP + "2025/11/stunning-siargao-island-in-the-philippines-900x600.jpg",
        "gallery": g("2025/11/stunning-siargao-island-in-the-philippines-870x555.jpg",
                     *[f"2026/02/{n}-870x555.jpg" for n in (
                         "Daku-Siargao-Island", "Daku-Siargao-Island-Philippines", "Naked-Island-Siargao",
                         "Tri-Island-Tour-Package-Guests", "Tri-Island-Tour-Package", "Daku-Island-Boddle-Fight",
                         "Boddle-Fight-in-Daku-Island")]),
        "summary": "Private boat to Naked, Daku and Guyam Islands on your own schedule.",
        "description": ("<p>Your group's own boat to Siargao's three classic islands: white-sand <strong>Naked Island</strong>, "
                        "<strong>Daku Island</strong> for swimming and a beach lunch, and leafy <strong>Guyam Island</strong> "
                        "for snorkeling. The itinerary can be adjusted, which makes it ideal for families and groups.</p>"),
        "highlights": lines("Naked Island — uninhabited, with white sand and clear water",
                            "Daku Island — swimming, picnics and sunbathing", "Guyam Island — greenery and snorkeling",
                            "Private boat for your group only", "Customisable itinerary",
                            "Local guides who share island stories"),
        "inclusions": lines(ISLAND_INCLUSIONS, "Cottage use at Daku Island", "Island entrance and environmental fees",
                            "Docking fees"),
        "exclusions": ISLAND_EXCLUSIONS,
        "reminders": lines("A ₱8,000 downpayment secures the booking; the balance depends on group size", *ISLAND_REMINDERS),
        "rate_tiers": "2: 4998\n3: 3798\n4: 3398\n5: 2798\n6: 2498\n7: 2198\n8: 1998\n9: 1798\n10: 1698",
    },
    {
        "slug": "sohoton-cove-private-tour", "title": "Sohoton Cove Private Tour", "location": "socorro-siargao",
        "address": "Socorro, Surigao del Norte, Philippines", "price": 10000, "duration": "Whole Day",
        "category": "private", "imported_rating": 5, "imported_reviews": 2, "start_time": "Pick-up 7:00–8:00 AM",
        "image_url": UP + "2026/01/sohoton-cove-18-900x600.jpg",
        "gallery": g("2026/01/sohoton-cove-26-870x555.jpg", "2026/01/sohoton-cove-44-870x555.jpg",
                     "2026/02/481900891_676541264728227_5798880536440822875_n-870x555.jpg",
                     "2026/02/Sohoton-Jellyfish-Sanctuary-870x555.jpg", "2026/02/Hagukan-Cave-870x555.jpg",
                     "2026/02/Sohoton-Cove-Boddle-Fight-Lunch-870x555.jpg",
                     "2026/02/Sohoton-Cove-Boddle-Fight-Lunch-1-870x555.jpg",
                     "2026/02/Sohoton-Cove-Boddle-Fight-Lunch-2-870x555.jpg", "2026/02/Diving-Cave-870x555.jpg",
                     "2026/01/sohoton-cove-42-870x555.jpg", "2026/01/sohoton-cove-15-e1540261567652-870x555.jpg",
                     "2026/01/sohoton-cove-48-870x555.jpg"),
        "summary": "Private guided day in Sohoton Cove — lagoons, caves and the jellyfish sanctuary.",
        "description": ("<p>Explore the limestone cliffs, emerald lagoons and caves of <strong>Sohoton Cove</strong> in Bucas "
                        "Grande with your own boat and guide, including a swim with stingless jellyfish in their natural "
                        "sanctuary.</p><p>Rates below are per person from General Luna; ask us for rates from Hayanggabon "
                        "Port.</p>"),
        "highlights": lines("Sohoton Cove National Park, Bucas Grande", "Emerald lagoons ringed by limestone cliffs",
                            "Hagukan Cave and Magkukuob Cave", "Paddleboarding in calm water",
                            "Jellyfish Sanctuary (stingless jellyfish swim)", "Tiktikan / Nakiauit (island schedule)",
                            "Club Tara Resort viewing (island schedule)",
                            "Dagatan Bay Resort & Viewing Lagoon (land schedule)"),
        "inclusions": SOHOTON_INCLUSIONS,
        "reminders": lines("A ₱10,000 booking deposit secures the date; the balance depends on group size",
                           *SOHOTON_REMINDERS),
        "rate_tiers": "1: 15498\n2: 7998\n3: 5998\n4: 4998\n5: 4098\n6: 3998\n7: 3798\n8: 3598\n9: 3498\n10: 3398\n11: 2998\n12: 2798",
    },
]

# --------------------------------------------------------------------------- cars & motorcycles
CAR_FEATURES = "Free Cancellation, Pay at Pickup, Unlimited Mileage, Shuttle to Car"
CAR_HOURS = "7:30 AM – 5:00 PM"
CAR_REQUIREMENTS = (
    "Present a valid driver's license at pick-up or delivery",
    "All passengers need valid travel documents (passport or ID, plus visas if applicable)",
    "A vehicle registration copy and the key are handed over at delivery and collected at return",
    "Confirm pick-up and drop-off locations at booking or at least 24 hours before delivery",
    "Location changes need at least 2 hours' notice",
    "Return the vehicle only to the agreed location",
    "Follow traffic rules and local regulations — the operator is not liable for accidents, damage or violations",
    "Damage or loss is settled by agreement between the operator and the customer")
GL_DELIVERY = ("<p><strong>Delivery outside General Luna</strong> — ₱500 each for delivery to or pull-out from Sayak "
               "Airport, and ₱500 each for delivery to or pull-out from Dapa Port.</p>")


def deposit(text):
    return f"<p><strong>Security deposit</strong> — {text}</p>"


DEP_2000 = deposit("₱2,000, refunded when the vehicle is returned in good condition. The operator may also hold your ID or passport.")
DEP_ID = deposit("The operator holds your ID or passport and returns it once the rental is settled.")
DEP_MOTO = deposit("₱1,000–₱2,000, refunded when the scooter is returned in good condition. The operator may also hold your ID or passport.")

CARS = [
    {"slug": "ford-ranger-general-luna", "title": "Ford Ranger (General Luna)", "category": "car", "seats": 5,
     "transmission": "Auto", "price": 3800, "location": "general-luna-siargao",
     "image": "2026/02/Ford-Ranger-Car-Rental-Siargao-760x460.jpg",
     "gallery": ["2026/02/Ford-Ranger-Car-Rental-Siargao.jpg"], "policies": DEP_2000 + GL_DELIVERY,
     "about": "An automatic pickup that's at home on adventures and everyday drives, with a smooth ride and room for gear — great for families and friends exploring the island."},
    {"slug": "toyota-vios-general-luna", "title": "Toyota Vios (General Luna)", "category": "car", "seats": 5,
     "transmission": "Auto", "price": 2100, "location": "general-luna-siargao",
     "image": "2026/02/Toyota-Vios-Maroon-760x460.jpg", "gallery": ["2026/02/Toyota-Vios-Maroon.jpg"],
     "policies": DEP_2000 + GL_DELIVERY,
     "about": "A comfortable, fuel-efficient automatic sedan for getting around Siargao, with unlimited mileage and free cancellation."},
    {"slug": "toyota-hilux-general-luna", "title": "Toyota Hilux (General Luna)", "category": "car", "seats": 5,
     "transmission": "Auto", "price": 3800, "location": "general-luna-siargao",
     "image": "2026/02/Toyota-Hilux-For-Rent-in-Siargao-760x460.jpg",
     "gallery": ["2026/02/Toyota-Hilux-For-Rent-in-Siargao.jpg", "2026/02/Toyota-Hilux-Car-Rental-Siargao-900x600.jpg"],
     "policies": DEP_2000 + GL_DELIVERY,
     "about": "A rugged automatic 4x4 pickup with plenty of space for passengers and luggage — built for Siargao's back roads."},
    {"slug": "toyota-vios-general-luna-2", "title": "Toyota Vios (General Luna)", "category": "car", "seats": 5,
     "transmission": "Auto", "price": 2100, "location": "general-luna-siargao",
     "image": "2026/02/Toyota-Vios-Siargao-760x460.jpg", "gallery": ["2026/02/Toyota-Vios-Siargao.jpg"],
     "policies": DEP_2000 + GL_DELIVERY,
     "about": "A comfortable, economical automatic sedan, equally good for town errands and scenic coastal drives."},
    {"slug": "honda-click-sayak-airport", "title": "Honda Click (Sayak Airport)", "category": "motorcycle", "seats": 2,
     "transmission": "Auto", "price": 550, "location": "del-carmen-siargao", "airport": True,
     "image": "2026/02/Honda-Click-Red-760x460.jpg", "gallery": ["2026/02/Honda-Click-Red.jpg"],
     "rate_tiers": "1: 550\n3: 495\n7: 440", "policies": DEP_MOTO,
     "about": "A fuel-efficient automatic scooter, ready for you at Sayak Airport — handy for short hops and longer island rides."},
    {"slug": "yamaha-fazzio-triple-rock-motorcycle-rental", "title": "Yamaha Fazzio (Sayak Airport)",
     "category": "motorcycle", "seats": 2, "transmission": "Manual", "price": 550, "location": "del-carmen-siargao",
     "airport": True, "image": "2026/01/Yamaha-Fazzio-Triple-Rock-760x460.jpg",
     "gallery": ["2026/01/Yamaha-Fazzio-Triple-Rock.jpg", "2026/01/IMG_9142-900x600.jpeg", "2026/01/IMG_9144-900x600.jpeg"],
     "rate_tiers": "1: 550\n3: 495\n7: 440", "policies": DEP_MOTO,
     "about": "A modern, fuel-efficient scooter with pick-up and drop-off at Sayak Airport."},
    {"slug": "toyota-veloz-general-luna", "title": "Toyota Veloz (General Luna)", "category": "car", "seats": 7,
     "transmission": "Auto", "price": 2800, "location": "general-luna-siargao",
     "image": "2026/02/Toyota-Veloz-Car-Rental-Siargao-760x460.jpg",
     "gallery": ["2026/02/Toyota-Veloz-Car-Rental-Siargao.jpg", "2026/02/Toyota-Veloz-Siargao-Car-Rental-900x600.jpg"],
     "policies": DEP_2000 + GL_DELIVERY,
     "about": "A roomy seven-seater for group and family trips around Siargao, balancing comfort, safety and fuel economy."},
    {"slug": "yamaha-fazzio-general-luna", "title": "Yamaha Fazzio (General Luna)", "category": "motorcycle",
     "seats": 2, "transmission": "Manual", "price": 550, "location": "general-luna-siargao",
     "image": "2026/02/Honda-Fazzio-4-760x460.jpg",
     "gallery": ["2026/02/Honda-Fazzio-900x600.jpg", "2026/02/Honda-Fazzio-4-900x600.jpg", "2026/02/Honda-Fazzio-2-900x600.jpg",
                 "2026/02/Honda-Fazzio-1-900x600.jpg", "2026/02/Honda-Fazzio-3-900x600.jpg"],
     "rate_tiers": "1: 550\n3: 495\n7: 450", "policies": DEP_ID,
     "about": "A stylish, comfortable and fuel-efficient scooter, picked up and dropped off in General Luna."},
    {"slug": "honda-beat-general-luna", "title": "Honda Beat (General Luna)", "category": "motorcycle", "seats": 2,
     "transmission": "Manual", "price": 450, "location": "general-luna-siargao",
     "image": "2026/02/Honda-Beat-1-760x460.jpg", "gallery": ["2026/02/Honda-Beat-1.jpg", "2026/02/Honda-Beat-900x600.jpg"],
     "rate_tiers": "1: 450\n3: 420\n7: 375", "policies": DEP_ID,
     "about": "A light, compact and economical scooter that's ideal for General Luna's narrow streets and winding coastal roads."},
    {"slug": "honda-click-general-luna", "title": "Honda Click (General Luna)", "category": "motorcycle", "seats": 2,
     "transmission": "Manual", "price": 500, "location": "general-luna-siargao",
     "image": "2026/02/Honda-Click-760x460.jpg",
     "gallery": ["2026/02/Honda-Click.jpg", "2026/02/Honda-Click-1-900x600.jpg", "2026/02/Honda-Click-2-900x600.jpg",
                 "2026/02/Honda-Click-3-900x600.jpg"],
     "rate_tiers": "1: 500\n3: 475\n7: 440", "policies": DEP_ID,
     "about": "A lightweight, fuel-efficient scooter for zipping around town and along the coast."},
    {"slug": "toyota-gl-grandia-general-luna", "title": "Toyota GL Grandia (General Luna)", "category": "car",
     "seats": 12, "transmission": "Auto", "price": 4300, "location": "general-luna-siargao",
     "image": "2026/02/Grandia-GL-Siargao-760x460.jpg",
     "gallery": ["2026/02/Grandia-GL-Siargao.jpg", "2026/02/Grandia-GL-Car-Rental-Siargao-900x600.jpg"],
     "policies": DEP_2000,
     "about": "A spacious automatic van for big groups, families and corporate trips, with room for everyone's luggage."},
    {"slug": "nissan-navara-sayak-airport", "title": "Nissan Navara (Sayak Airport)", "category": "car", "seats": 5,
     "transmission": "Auto", "price": 3800, "location": "del-carmen-siargao", "airport": True,
     "image": "2026/02/Nissan-Navara-Red-760x460.jpg", "gallery": ["2026/02/Nissan-Navara-Red.jpg"], "policies": DEP_ID,
     "about": "A five-seat pickup with cargo space, as capable off-road as it is comfortable on the highway — collected at Sayak Airport."},
    {"slug": "nissan-livina-general-luna", "title": "Nissan Livina (General Luna)", "category": "car", "seats": 7,
     "transmission": "Auto", "price": 2800, "location": "general-luna-siargao",
     "image": "2026/02/Nissan-Livina-4-900x600.jpg",
     "gallery": [f"2026/02/Nissan-Livina-{i}-900x600.jpg" for i in (4, 6, 1, 2, 5)], "policies": DEP_ID,
     "about": "A comfortable seven-seat automatic MPV for families and groups, whether for road trips or daily errands."},
    {"slug": "nissan-terra-sayak-airport", "title": "Nissan Terra (Sayak Airport)", "category": "car", "seats": 7,
     "transmission": "Auto", "price": 3800, "location": "del-carmen-siargao", "airport": True,
     "image": "2026/02/Nissan-Terra-900x600.jpg", "gallery": ["2026/02/Nissan-Terra.jpg"], "policies": DEP_ID,
     "about": "A seven-seat automatic SUV that handles rough terrain and town roads, with room for passengers and luggage."},
    {"slug": "nissan-navara-general-luna", "title": "Nissan Navara (General Luna)", "category": "car", "seats": 5,
     "transmission": "Auto", "price": 3800, "location": "general-luna-siargao",
     "image": "2026/02/Nissan-Navarra-900x600.jpg", "gallery": ["2026/02/Nissan-Navarra.jpg"], "policies": DEP_ID,
     "about": "A rugged five-seat automatic pickup suited to paved island roads and off-road trips alike."},
]

# --------------------------------------------------------------------------- blog
CATEGORIES = [("travel-guides", "Travel Guides"), ("things-to-do", "Things To Do"),
              ("local-tips-and-culture", "Local Tips & Culture"), ("news-and-updates", "News & Updates")]

# slug, title, category, featured image, date (sitemap last-modified; import-wp sets the real publish date), teaser
POSTS = [
    ("siargao-philippines-airport", "Siargao Philippines Airport: Your Complete Guide to Sayak Airport (IAO)", "travel-guides",
     "2026/08/Siargao-Philippines-Airport.jpg", "2026-08-11", "Flights, arrival tips and getting from Sayak Airport to General Luna."),
    ("magpupungko-rock-pools-siargao", "Magpupungko Rock Pools Siargao: A Complete Guide to One of Siargao’s Best Attractions",
     "travel-guides", "2025/11/Magpupungko-Rock-Pools-Pilar-Siargao.jpg", "2026-08-11",
     "When to go, tide timing and what to expect at Pilar's famous tidal pools."),
    ("cloud-9-siargao", "Cloud 9 Siargao Island Philippines: The Ultimate Guide to Surfing, Sunsets & Island Life",
     "travel-guides", "2026/08/Cloud-9-Siargao-Island-Philippines.jpeg", "2026-08-11",
     "Everything about Siargao's iconic surf break, boardwalk and sunsets."),
    ("sohoton-cove-tour-from-siargao", "Sohoton Cove Tour from Siargao: A Complete Guide to One of Siargao’s Most Beautiful Adventures",
     "travel-guides", "2026/01/sohoton-cove-26.jpg", "2026-08-10",
     "How the Sohoton Cove day trip works — lagoons, caves, jellyfish and what to bring."),
    ("tri-island-tour-siargao-what-to-expect-complete-travel-guide", "Tri-Island Tour Siargao: What to Expect + Complete Travel Guide",
     "travel-guides", "2026/02/Daku-Island-Siargao-Philippines.jpg", "2026-06-28",
     "Naked, Daku and Guyam Islands: the stops, timing and tips for island hopping."),
    ("siargao-vs-other-philippine-islands-why-travelers-choose-siargao-complete-travel-guide",
     "Siargao vs Other Philippine Islands: Why Travelers Choose Siargao (Complete Travel Guide)", "news-and-updates",
     "2026/02/Cloud-9-General-Luna-Siargao.jpg", "2026-06-13",
     "How Siargao compares with Palawan, Boracay, Cebu and Bohol."),
    ("siargao-vs-bali-which-destination-should-you-choose-for-your-next-vacation",
     "Siargao vs Bali — Which Destination Should You Choose for Your Next Vacation?", "travel-guides",
     "2026/02/Siargao-vs-Bali.jpg", "2026-02-09", "A side-by-side look at two of Asia's favourite surf islands."),
    ("the-biggest-mistake-tourists-make-when-booking-a-siargao-hotel-and-how-to-avoid-it",
     "The Biggest Mistake Tourists Make When Booking a Siargao Hotel (And How to Avoid It)", "travel-guides",
     "2026/02/Siargao-Bleu-Resort-Siargao.jpg", "2026-02-04", "Common booking pitfalls and how to choose the right area to stay."),
    ("romantic-escapes-in-siargao-experiences-and-stays-designed-for-couples",
     "Romantic Escapes in Siargao: Experiences and Stays Designed for Couples", "travel-guides",
     "2026/01/Where-Love-Feels-Easy-Romantic-Escapes-and-Intimate-Experiences-in-Siargao-copy.jpg", "2026-01-29",
     "Ideas for couples — sunsets, quiet beaches and stays made for two."),
    ("celebrating-identity-festivals-that-shape-the-culture-of-siargao",
     "Celebrating Identity: Festivals That Shape the Culture of Siargao", "local-tips-and-culture",
     "2025/12/Festivals-That-Shape-the-Culture-of-Siargao.jpg", "2025-12-21",
     "The local festivals and traditions behind Siargao's island culture."),
    ("the-ultimate-surfing-guide-to-siargao-surf-spots-for-beginners-to-pros",
     "The Ultimate Surfing Guide to Siargao: Surf Spots for Beginners to Pros", "travel-guides",
     "2025/12/Cloud-9-Surfing-Area-Siargao.jpg", "2025-12-21", "Siargao's surf breaks by level, season and access."),
    ("the-story-of-afam-bridge-siargaos-sunset-bridge-where-locals-and-travelers-meet",
     "The Story of Afam Bridge: Siargao’s Sunset Bridge Where Locals and Travelers Meet", "things-to-do",
     "2025/12/Afam-Bridge-Siargao.jpg", "2025-12-10", "The story behind one of General Luna's favourite sunset spots."),
    ("how-to-get-to-siargao-from-cagayan-de-oro", "How To Get To Siargao From Cagayan de Oro", "travel-guides",
     "2025/11/Siargao-Hotels-Club-Tara.jpg", "2025-11-22", "Bus, ferry and flight options from Cagayan de Oro."),
    ("budget-travel-in-siargao-how-to-spend-less-and-experience-more",
     "Budget Travel in Siargao: How to Spend Less and Experience More", "local-tips-and-culture",
     "2025/11/Sugba-Lagoon-Siargao-Island.jpg", "2025-11-22", "Practical ways to save on stays, food, tours and transport."),
    ("from-city-to-surf-exploring-the-2go-mini-cruise-from-manila-to-siargao",
     "From City to Surf: Exploring the 2GO Mini Cruise from Manila to Siargao", "travel-guides",
     "2025/11/2Go-St-Franxis-Xavier.jpg", "2025-11-22", "What the overnight 2GO voyage from Manila to Siargao is like."),
    ("siargao-land-tour-the-best-spots-you-shouldnt-miss", "Siargao Land Tour: The Best Spots You Shouldn’t Miss",
     "things-to-do", "2025/10/Siargao-Coconut-Mountain-View.jpg", "2025-11-22",
     "The must-see stops on a Siargao land tour, from lagoons to viewpoints."),
    ("when-is-the-best-time-to-visit-siargao-weather-waves-events",
     "When Is the Best Time to Visit Siargao? Weather, Waves & Events", "travel-guides",
     "2025/11/young-man-enjoying-sunrise-in-Siargao.jpg", "2025-11-22", "Month-by-month weather, surf season and events."),
    ("top-20-things-to-do-in-siargao-besides-surfing", "Top 20 Things to Do in Siargao (Besides Surfing)", "things-to-do",
     "2025/11/Leaning-Palm-Tree-Maasin-Siargao.jpg", "2025-11-21", "Twenty ways to enjoy Siargao when you're out of the water."),
    ("the-siargao-curse-whats-behind-the-islands-spell", "The Siargao Curse: What’s Behind the Island’s Spell?",
     "things-to-do", "2025/11/Siargao-Curse.jpg", "2025-11-15", "Why so many visitors never quite manage to leave Siargao."),
    ("how-to-get-to-siargao-from-davao-city", "How To Get To Siargao From Davao City", "travel-guides",
     "2025/11/stunning-siargao-island-in-the-philippines.jpg", "2025-11-14", "Getting to Siargao from Davao by air, land and sea."),
    ("how-to-get-to-siargao-from-cebu", "How To Get To Siargao From Cebu", "travel-guides",
     "2025/11/Cebu-Port-Philippines.jpg", "2025-11-14", "Direct flights and ferry routes from Cebu to Siargao."),
    ("how-to-get-to-siargao-island-from-manila", "How To Get To Siargao Island From Manila", "travel-guides",
     "2025/11/Maasin-River-Cruise-Siargao-Island.jpg", "2025-11-14", "Flights and sea routes from Manila, with travel times."),
]

# Blog posts related to listings — used for the "plan this trip" links under each teaser
POST_LINKS = {
    "sohoton": ("/st_tour/sohoton-cove-joiner-tour/", "Book the Sohoton Cove tour"),
    "tri-island": ("/st_tour/siargao-tri-island-corregidor-island-joiner-tour/", "Book a Tri-Island tour"),
    "land-tour": ("/st_tour/siargao-joiner-land-tour/", "Book the Siargao Land Tour"),
    "magpupungko": ("/st_tour/siargao-joiner-land-tour/", "Visit Magpupungko on the Land Tour"),
    "airport": ("/car-and-motorcycle-rentals/", "Rent a car or scooter at the airport"),
    "hotel": ("/hotels/", "Browse Siargao hotels"),
}
