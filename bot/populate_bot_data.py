from bot.models import Menu, PageContent, JobCategory, Location, Position

# 1️⃣ Create Menus
menus = [
    {"key": "about", "title": "Biz haqimizda"},
    {"key": "jobs", "title": "Bo'sh ish o'rinlari"},
    {"key": "contact", "title": "Biz bilan bog'lanish"},
]

for m in menus:
    Menu.objects.update_or_create(key=m["key"], defaults={"title": m["title"]})

# 2️⃣ Page contents
pages = [
    {"key": "about", "text": "Gulnnoza opa beradilar"},
    {"key": "contact", "text": "Gulnnoza opa beradilar"},
]

for p in pages:
    PageContent.objects.update_or_create(key=p["key"], defaults={"text": p["text"]})

# 3️⃣ Job Categories
categories = [
    {"name": "Ofis", "icon": "🏢"},
    {"name": "Zavod", "icon": "🏭"},
    {"name": "Viloyatlar bo'yicha", "icon": "📍"},
]

for c in categories:
    JobCategory.objects.update_or_create(name=c["name"], defaults={"icon": c["icon"]})

# 4️⃣ Locations
locations = [
    # Ofis
    {"category": "Ofis", "name": "Sergeli Cable", "address": "location"},
    {"category": "Ofis", "name": "Sergeli Lampochka zavodi", "address": "location"},
    {"category": "Ofis", "name": "Chilonzor Beton Zavodi", "address": "location"},
    {"category": "Ofis", "name": "Shayxontoxur asosiy zavod", "address": "location"},

    # Zavod
    {"category": "Zavod", "name": "Sergeli Cable zavodi", "address": "location"},
    {"category": "Zavod", "name": "Sergeli Lampochka zavodi", "address": "location"},
    {"category": "Zavod", "name": "Chilonzor Beton Zavodi", "address": "location"},
    {"category": "Zavod", "name": "Shayxontoxur asosiy zavod", "address": "location"},

    # Viloyatlar
    {"category": "Viloyatlar bo'yicha", "name": "Toshkent Sh", "address": "location"},
    {"category": "Viloyatlar bo'yicha", "name": "Toshkent V", "address": "location"},
    {"category": "Viloyatlar bo'yicha", "name": "Sirdaryo", "address": "location"},
]

for loc in locations:
    cat = JobCategory.objects.get(name=loc["category"])
    Location.objects.update_or_create(
        category=cat,
        name=loc["name"],
        defaults={"address": loc["address"]}
    )

# 5️⃣ Positions (example, you can adjust)
positions = [
    {"category": "Ofis", "title": "Manager"},
    {"category": "Ofis", "title": "Engineer"},
    {"category": "Zavod", "title": "Technician"},
    {"category": "Zavod", "title": "Supervisor"},
]

for pos in positions:
    cat = JobCategory.objects.get(name=pos["category"])
    Position.objects.update_or_create(category=cat, title=pos["title"])
