from pathlib import Path
from datetime import timedelta, date
from decimal import Decimal, ROUND_HALF_UP
import random

from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

fake = Faker("fr_FR")
Faker.seed(2023)
random.seed(2023)

BASE_DIR = Path(__file__).resolve().parent / "dataset" / "synthetic"
COUNT_PER_CLASS = 20

ARTICLES = [
    "Prestation de conseil",
    "Développement logiciel",
    "Maintenance informatique",
    "Hébergement web mensuel",
    "Formation professionnelle",
    "Audit de sécurité",
    "Licence logicielle annuelle",
    "Support technique",
    "Installation matériel",
    "Rédaction de rapport",
]

FRENCH_CITIES = [
    "Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg",
    "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre",
    "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes", "Brest",
]

JOB_TITLES = [
    "Développeur informatique", "Comptable", "Assistant administratif",
    "Chef de projet", "Commercial", "Ingénieur logiciel", "Consultant",
    "Responsable marketing", "Technicien de maintenance", "Analyste financier",
]

SERVICE_OBJECTS = [
    "le développement d'une application web sur mesure",
    "la refonte du site internet du Client",
    "la mise en place d'une stratégie de communication digitale",
    "un audit de sécurité informatique complet",
    "la maintenance évolutive du système d'information",
    "la formation du personnel aux outils bureautiques",
    "la rédaction de la documentation technique",
    "le conseil en organisation et transformation numérique",
]

LETTER_OBJECTS = [
    "Demande de renseignements",
    "Réclamation concernant la commande n° {ref}",
    "Demande de rendez-vous",
    "Confirmation de votre inscription",
    "Réponse à votre courrier du {date}",
    "Invitation à notre événement annuel",
]

ATTESTATION_TYPES = [
    "Attestation d'hébergement",
    "Attestation de présence",
    "Attestation sur l'honneur",
    "Attestation de formation",
    "Attestation employeur",
]

NOTE_OBJECTS = [
    "Nouvelles procédures de sécurité informatique",
    "Modification des horaires d'ouverture",
    "Plan de formation pour l'année à venir",
    "Mise à jour du règlement intérieur",
    "Organisation du séminaire annuel",
]

CV_SKILLS = [
    "Python", "SQL", "Excel avancé", "Gestion de projet", "Anglais courant",
    "Communication", "Travail en équipe", "Microsoft Office", "Power BI",
    "Comptabilité", "Marketing digital", "SAP", "JavaScript", "Photoshop",
]

CV_DIPLOMAS = [
    "Master en Informatique",
    "Licence professionnelle en Gestion",
    "BTS Comptabilité et Gestion",
    "Master en Marketing",
    "Diplôme d'Ingénieur",
    "Licence en Économie",
]


def euros(value):
    q = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    integer, _, fraction = f"{q:.2f}".partition(".")
    integer_spaced = " ".join(
        [integer[max(0, i - 3):i] for i in range(len(integer), 0, -3)][::-1]
    )
    return f"{integer_spaced},{fraction} €"


def fr_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _draw_wrapped(c, text, x, y, max_width_mm, line_height_mm=5, font="Helvetica", size=10):
    from reportlab.pdfbase.pdfmetrics import stringWidth

    c.setFont(font, size)
    max_width_pt = max_width_mm * mm 
    words = text.split()
    line = ""

    for w in words:
        candidate = w if not line else f"{line} {w}"
        if stringWidth(candidate, font, size) > max_width_pt:
            c.drawString(x, y, line)
            y -= line_height_mm * mm
            line = w
        else:
            line = candidate

    if line:
        c.drawString(x, y, line)
        y -= line_height_mm * mm
    return y



def generate_invoice(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    company = fake.company()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, height - 25 * mm, company)

    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, height - 32 * mm, fake.street_address())
    c.drawString(20 * mm, height - 37 * mm, f"{fake.postcode()} {fake.city()}")
    c.drawString(20 * mm, height - 42 * mm, f"SIRET : {fake.siret()}")
    c.drawString(20 * mm, height - 47 * mm, f"TVA intracommunautaire : FR{random.randint(10, 99)} {fake.siret()[:9]}")

    c.setFont("Helvetica-Bold", 22)
    c.drawRightString(width - 20 * mm, height - 25 * mm, "FACTURE")

    invoice_number = f"F-{random.randint(2023, 2026)}-{random.randint(1000, 9999)}"
    invoice_date = fake.date_between(start_date="-1y", end_date="today")
    due_date = invoice_date + timedelta(days=30)

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 20 * mm, height - 33 * mm, f"N° {invoice_number}")
    c.drawRightString(width - 20 * mm, height - 39 * mm, f"Date : {fr_date(invoice_date)}")
    c.drawRightString(width - 20 * mm, height - 45 * mm, f"Échéance : {fr_date(due_date)}")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, height - 65 * mm, "Facturé à :")
    c.setFont("Helvetica", 10)
    client_name = fake.company() if random.random() < 0.7 else fake.name()
    c.drawString(20 * mm, height - 71 * mm, client_name)
    c.drawString(20 * mm, height - 76 * mm, fake.street_address())
    c.drawString(20 * mm, height - 81 * mm, f"{fake.postcode()} {fake.city()}")

    y = height - 100 * mm
    c.setFillColor(colors.lightgrey)
    c.rect(20 * mm, y, width - 40 * mm, 8 * mm, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(22 * mm, y + 2.5 * mm, "Désignation")
    c.drawRightString(120 * mm, y + 2.5 * mm, "Qté")
    c.drawRightString(150 * mm, y + 2.5 * mm, "Prix unitaire HT")
    c.drawRightString(width - 22 * mm, y + 2.5 * mm, "Total HT")

    y -= 6 * mm
    c.setFont("Helvetica", 10)
    total_ht = Decimal("0.00")
    nb_lines = random.randint(2, 5)
    for _ in range(nb_lines):
        article = random.choice(ARTICLES)
        qty = random.randint(1, 10)
        unit_price = Decimal(random.randint(50, 800)) + Decimal(random.choice(["0.00", "0.50"]))
        line_total = (unit_price * qty).quantize(Decimal("0.01"))
        total_ht += line_total
        y -= 7 * mm
        c.drawString(22 * mm, y, article)
        c.drawRightString(120 * mm, y, str(qty))
        c.drawRightString(150 * mm, y, euros(unit_price))
        c.drawRightString(width - 22 * mm, y, euros(line_total))

    y -= 15 * mm
    tva_rate = Decimal("0.20")
    tva_amount = (total_ht * tva_rate).quantize(Decimal("0.01"))
    total_ttc = total_ht + tva_amount

    c.setFont("Helvetica", 10)
    c.drawRightString(150 * mm, y, "Total HT :")
    c.drawRightString(width - 22 * mm, y, euros(total_ht))
    y -= 6 * mm
    c.drawRightString(150 * mm, y, "TVA 20% :")
    c.drawRightString(width - 22 * mm, y, euros(tva_amount))
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(150 * mm, y, "Total TTC :")
    c.drawRightString(width - 22 * mm, y, euros(total_ttc))

    c.setFont("Helvetica", 8)
    c.drawString(20 * mm, 25 * mm, "Conditions de paiement : virement bancaire à 30 jours.")
    c.drawString(20 * mm, 21 * mm, f"IBAN : FR76 {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(100, 999)}")
    c.drawString(20 * mm, 17 * mm, "En cas de retard de paiement, des pénalités seront appliquées conformément à la loi.")

    c.save()


def _id_person():
    sex = random.choice(["M", "F"])
    if sex == "M":
        first = fake.first_name_male()
        last = fake.last_name()
    else:
        first = fake.first_name_female()
        last = fake.last_name()
    birth = fake.date_of_birth(minimum_age=18, maximum_age=75)
    return {
        "sex": sex, "first": first, "last": last,
        "birth": birth, "birth_city": random.choice(FRENCH_CITIES),
        "nationality": "FRANÇAISE",
    }


def _draw_id_header(c, width, height, title):
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width / 2, height - 22 * mm, "RÉPUBLIQUE FRANÇAISE")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 32 * mm, title)


def _draw_id_field(c, x, y, label, value):
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(x, y, label)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y - 5 * mm, value)


def generate_cni(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    person = _id_person()
    _draw_id_header(c, width, height, "CARTE NATIONALE D'IDENTITÉ")

    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 40 * mm, f"N° {random.randint(100000000000, 999999999999)}")

    c.setStrokeColor(colors.grey)
    c.rect(20 * mm, height - 95 * mm, 35 * mm, 45 * mm, stroke=1, fill=0)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(20 * mm + 17.5 * mm, height - 73 * mm, "[photo]")
    c.setFillColor(colors.black)

    x = 65 * mm
    y = height - 55 * mm
    _draw_id_field(c, x, y, "Nom", person["last"].upper()); y -= 12 * mm
    _draw_id_field(c, x, y, "Prénom(s)", person["first"]); y -= 12 * mm
    _draw_id_field(c, x, y, "Sexe", person["sex"]); y -= 12 * mm
    _draw_id_field(c, x, y, "Né(e) le", fr_date(person["birth"])); y -= 12 * mm
    _draw_id_field(c, x, y, "Lieu de naissance", person["birth_city"])

    issue = fake.date_between(start_date="-8y", end_date="-1y")
    expiry = date(issue.year + 10, issue.month, issue.day)
    height_cm = random.randint(155, 195)

    y = height - 115 * mm
    _draw_id_field(c, 20 * mm, y, "Nationalité", person["nationality"])
    _draw_id_field(c, 80 * mm, y, "Taille", f"{height_cm} cm")
    _draw_id_field(c, 130 * mm, y, "Date de délivrance", fr_date(issue))
    y -= 12 * mm
    _draw_id_field(c, 20 * mm, y, "Date d'expiration", fr_date(expiry))
    _draw_id_field(c, 80 * mm, y, "Délivrée par", f"Préfecture de {random.choice(FRENCH_CITIES)}")

    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, 50 * mm, "Signature du titulaire :")
    c.line(20 * mm, 40 * mm, 90 * mm, 40 * mm)

    c.setFont("Courier", 10)
    mrz1 = f"IDFRA{person['last'].upper()[:10]:<10}<<{person['first'].upper()[:14]:<14}<<<<<<"
    mrz2 = f"{random.randint(100000000, 999999999)}FRA{person['birth'].strftime('%y%m%d')}{person['sex']}{expiry.strftime('%y%m%d')}<<<<<<"
    c.drawString(20 * mm, 25 * mm, mrz1[:36])
    c.drawString(20 * mm, 20 * mm, mrz2[:36])

    c.save()


def generate_passport(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    person = _id_person()
    _draw_id_header(c, width, height, "PASSEPORT")

    c.setFont("Helvetica", 9)
    passport_no = f"{random.randint(10, 99)}{random.choice(['AB','CD','EF','GH'])}{random.randint(10000, 99999)}"
    c.drawCentredString(width / 2, height - 40 * mm, f"Type : P    Code : FRA    N° : {passport_no}")

    c.setStrokeColor(colors.grey)
    c.rect(20 * mm, height - 95 * mm, 35 * mm, 45 * mm, stroke=1, fill=0)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(20 * mm + 17.5 * mm, height - 73 * mm, "[photo]")
    c.setFillColor(colors.black)

    x = 65 * mm
    y = height - 55 * mm
    _draw_id_field(c, x, y, "Nom / Surname", person["last"].upper()); y -= 12 * mm
    _draw_id_field(c, x, y, "Prénoms / Given names", person["first"]); y -= 12 * mm
    _draw_id_field(c, x, y, "Nationalité / Nationality", person["nationality"]); y -= 12 * mm
    _draw_id_field(c, x, y, "Date de naissance / Date of birth", fr_date(person["birth"])); y -= 12 * mm
    _draw_id_field(c, x, y, "Sexe / Sex", person["sex"])

    issue = fake.date_between(start_date="-7y", end_date="-1y")
    expiry = date(issue.year + 10, issue.month, issue.day)

    y = height - 115 * mm
    _draw_id_field(c, 20 * mm, y, "Lieu de naissance / Place of birth", person["birth_city"])
    _draw_id_field(c, 100 * mm, y, "Autorité / Authority", f"Préfecture de {random.choice(FRENCH_CITIES)}")
    y -= 12 * mm
    _draw_id_field(c, 20 * mm, y, "Date de délivrance / Date of issue", fr_date(issue))
    _draw_id_field(c, 100 * mm, y, "Date d'expiration / Date of expiry", fr_date(expiry))

    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, 50 * mm, "Signature du titulaire / Holder's signature :")
    c.line(20 * mm, 40 * mm, 90 * mm, 40 * mm)

    c.setFont("Courier", 10)
    mrz1 = f"P<FRA{person['last'].upper()[:10]:<10}<<{person['first'].upper()[:14]:<14}<<<<<<"
    mrz2 = f"{passport_no}<<FRA{person['birth'].strftime('%y%m%d')}{person['sex']}{expiry.strftime('%y%m%d')}<<<<<<"
    c.drawString(20 * mm, 25 * mm, mrz1[:44])
    c.drawString(20 * mm, 20 * mm, mrz2[:44])

    c.save()


def generate_permis(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    person = _id_person()
    _draw_id_header(c, width, height, "PERMIS DE CONDUIRE")

    c.setFont("Helvetica", 9)
    permis_no = f"{random.randint(10, 99)}{fake.postcode()[:2]}{random.randint(100000, 999999)}"
    c.drawCentredString(width / 2, height - 40 * mm, f"N° {permis_no}")

    c.setStrokeColor(colors.grey)
    c.rect(20 * mm, height - 95 * mm, 35 * mm, 45 * mm, stroke=1, fill=0)
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawCentredString(20 * mm + 17.5 * mm, height - 73 * mm, "[photo]")
    c.setFillColor(colors.black)

    x = 65 * mm
    y = height - 55 * mm
    _draw_id_field(c, x, y, "Nom", person["last"].upper()); y -= 12 * mm
    _draw_id_field(c, x, y, "Prénom(s)", person["first"]); y -= 12 * mm
    _draw_id_field(c, x, y, "Date de naissance", fr_date(person["birth"])); y -= 12 * mm
    _draw_id_field(c, x, y, "Lieu de naissance", person["birth_city"])

    issue = fake.date_between(start_date="-15y", end_date="-1y")

    y = height - 115 * mm
    _draw_id_field(c, 20 * mm, y, "Date de délivrance", fr_date(issue))
    _draw_id_field(c, 80 * mm, y, "Délivré par", f"Préfecture de {random.choice(FRENCH_CITIES)}")
    _draw_id_field(c, 140 * mm, y, "Nationalité", person["nationality"])

    y -= 18 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "Catégories obtenues :")
    c.setFont("Helvetica", 10)
    y -= 7 * mm

    categories = [("B", "Véhicules légers"), ("AM", "Cyclomoteurs")]
    if random.random() < 0.3:
        categories.append(("A2", "Motocyclettes"))
    if random.random() < 0.2:
        categories.append(("BE", "Véhicule + remorque"))

    for code, label in categories:
        cat_date = fake.date_between(start_date=issue, end_date="today")
        c.drawString(25 * mm, y, f"• {code} — {label}    (obtenue le {fr_date(cat_date)})")
        y -= 6 * mm

    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, 50 * mm, "Signature du titulaire :")
    c.line(20 * mm, 40 * mm, 90 * mm, 40 * mm)

    c.save()


def generate_id(path: Path, subtype: str):
    if subtype == "cni": generate_cni(path)
    elif subtype == "passport": generate_passport(path)
    elif subtype == "permis": generate_permis(path)
    else: raise ValueError(f"Unknown ID subtype: {subtype}")


def generate_contract_travail(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 25 * mm, "CONTRAT DE TRAVAIL")
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 33 * mm, "à durée indéterminée")

    employer = fake.company()
    employer_addr = f"{fake.street_address()}, {fake.postcode()} {fake.city()}"
    employer_siret = fake.siret()
    employee = fake.name()
    employee_addr = f"{fake.street_address()}, {fake.postcode()} {fake.city()}"

    y = height - 50 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "ENTRE LES SOUSSIGNÉS :")
    y -= 10 * mm

    c.setFont("Helvetica", 10)
    y = _draw_wrapped(c,
        f"La société {employer}, dont le siège social est situé au {employer_addr}, "
        f"immatriculée au RCS sous le numéro SIRET {employer_siret}, représentée par "
        f"son gérant {fake.name()}, ci-après dénommée \"l'Employeur\",",
        20 * mm, y, max_width_mm=170)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "D'UNE PART,")
    y -= 8 * mm

    c.setFont("Helvetica", 10)
    y = _draw_wrapped(c,
        f"Et {employee}, demeurant au {employee_addr}, "
        f"ci-après dénommé(e) \"le Salarié\",",
        20 * mm, y, max_width_mm=170)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "D'AUTRE PART,")
    y -= 10 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "IL A ÉTÉ CONVENU CE QUI SUIT :")
    y -= 10 * mm

    job = random.choice(JOB_TITLES)
    start_date = fake.date_between(start_date="-2y", end_date="today")
    salary = random.randint(1800, 4500)

    articles = [
        ("Article 1 — Engagement",
         f"Le Salarié est engagé en qualité de {job}, à compter du {fr_date(start_date)}, pour une durée indéterminée."),
        ("Article 2 — Période d'essai",
         "Le présent contrat est conclu sous réserve d'une période d'essai de deux (2) mois, renouvelable une fois pour la même durée."),
        ("Article 3 — Lieu de travail",
         f"Le Salarié exercera ses fonctions au sein des locaux de l'Employeur situés à {fake.city()}."),
        ("Article 4 — Durée du travail",
         "La durée hebdomadaire de travail est fixée à 35 heures, réparties selon les modalités définies par la convention collective applicable."),
        ("Article 5 — Rémunération",
         f"En contrepartie de ses fonctions, le Salarié percevra une rémunération brute mensuelle de {salary} euros, versée sur douze mois."),
        ("Article 6 — Congés payés",
         "Le Salarié bénéficiera des congés payés conformément aux dispositions légales et conventionnelles en vigueur."),
    ]

    for title, body in articles:
        if y < 60 * mm:
            c.showPage(); y = height - 25 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, title); y -= 6 * mm
        c.setFont("Helvetica", 10)
        y = _draw_wrapped(c, body, 20 * mm, y, max_width_mm=170)
        y -= 3 * mm

    if y < 50 * mm:
        c.showPage(); y = height - 30 * mm

    y -= 5 * mm
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Fait à {fake.city()}, le {fr_date(fake.date_between(start_date='-30d', end_date='today'))}, en deux exemplaires originaux.")
    y -= 20 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(30 * mm, y, "L'Employeur")
    c.drawString(120 * mm, y, "Le Salarié")
    y -= 5 * mm
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(30 * mm, y, "(signature et cachet)")
    c.drawString(120 * mm, y, "(mention \"Bon pour accord\")")

    c.save()


def generate_contract_prestation(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 25 * mm, "CONTRAT DE PRESTATION DE SERVICES")

    client = fake.company()
    client_addr = f"{fake.street_address()}, {fake.postcode()} {fake.city()}"
    provider = fake.company()
    provider_addr = f"{fake.street_address()}, {fake.postcode()} {fake.city()}"

    y = height - 45 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "ENTRE LES SOUSSIGNÉS :")
    y -= 10 * mm

    c.setFont("Helvetica", 10)
    y = _draw_wrapped(c,
        f"La société {client}, dont le siège social est situé au {client_addr}, "
        f"immatriculée sous le numéro SIRET {fake.siret()}, représentée par "
        f"{fake.name()}, ci-après dénommée \"le Client\",",
        20 * mm, y, max_width_mm=170)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "D'UNE PART,")
    y -= 8 * mm

    c.setFont("Helvetica", 10)
    y = _draw_wrapped(c,
        f"Et la société {provider}, dont le siège social est situé au {provider_addr}, "
        f"immatriculée sous le numéro SIRET {fake.siret()}, représentée par "
        f"{fake.name()}, ci-après dénommée \"le Prestataire\",",
        20 * mm, y, max_width_mm=170)

    y -= 3 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "D'AUTRE PART,")
    y -= 10 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "IL A ÉTÉ CONVENU CE QUI SUIT :")
    y -= 10 * mm

    obj = random.choice(SERVICE_OBJECTS)
    honoraires = random.randint(3000, 25000)
    duration_months = random.choice([3, 6, 9, 12])

    articles = [
        ("Article 1 — Objet du contrat",
         f"Le présent contrat a pour objet {obj}. Le Prestataire s'engage à exécuter cette mission avec diligence et conformément aux règles de l'art."),
        ("Article 2 — Durée",
         f"Le présent contrat est conclu pour une durée de {duration_months} mois à compter de sa signature, renouvelable par tacite reconduction."),
        ("Article 3 — Honoraires",
         f"En contrepartie de l'exécution de la prestation, le Client versera au Prestataire des honoraires d'un montant de {honoraires} euros hors taxes, payables à 30 jours fin de mois."),
        ("Article 4 — Obligations du Prestataire",
         "Le Prestataire s'engage à exécuter la prestation conformément aux règles de l'art et dans le respect des délais convenus entre les parties."),
        ("Article 5 — Confidentialité",
         "Les parties s'engagent à conserver strictement confidentielles toutes les informations échangées dans le cadre du présent contrat."),
        ("Article 6 — Résiliation",
         "Le présent contrat pourra être résilié par l'une ou l'autre des parties en cas de manquement grave, moyennant un préavis de trente (30) jours notifié par lettre recommandée avec accusé de réception."),
    ]

    for title, body in articles:
        if y < 60 * mm:
            c.showPage(); y = height - 25 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, title); y -= 6 * mm
        c.setFont("Helvetica", 10)
        y = _draw_wrapped(c, body, 20 * mm, y, max_width_mm=170)
        y -= 3 * mm

    if y < 50 * mm:
        c.showPage(); y = height - 30 * mm

    y -= 5 * mm
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, f"Fait à {fake.city()}, le {fr_date(fake.date_between(start_date='-60d', end_date='today'))}, en deux exemplaires originaux.")
    y -= 20 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(30 * mm, y, "Le Client")
    c.drawString(120 * mm, y, "Le Prestataire")
    y -= 5 * mm
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(30 * mm, y, "(signature et cachet)")
    c.drawString(120 * mm, y, "(mention \"Bon pour accord\")")

    c.save()


def generate_contract(path: Path, subtype: str):
    if subtype == "travail": generate_contract_travail(path)
    elif subtype == "prestation": generate_contract_prestation(path)
    else: raise ValueError(f"Unknown contract subtype: {subtype}")


def generate_lettre(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    sender_name = fake.name()
    sender_addr = fake.street_address()
    sender_city = f"{fake.postcode()} {fake.city()}"

    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, height - 25 * mm, sender_name)
    c.drawString(20 * mm, height - 30 * mm, sender_addr)
    c.drawString(20 * mm, height - 35 * mm, sender_city)

    recipient_name = fake.company()
    recipient_addr = fake.street_address()
    recipient_city = f"{fake.postcode()} {fake.city()}"

    c.drawRightString(width - 20 * mm, height - 50 * mm, recipient_name)
    c.drawRightString(width - 20 * mm, height - 55 * mm, recipient_addr)
    c.drawRightString(width - 20 * mm, height - 60 * mm, recipient_city)

    letter_date = fake.date_between(start_date="-90d", end_date="today")
    c.drawRightString(width - 20 * mm, height - 75 * mm, f"{fake.city()}, le {fr_date(letter_date)}")

    obj_template = random.choice(LETTER_OBJECTS)
    obj = obj_template.format(
        ref=f"{random.randint(10000, 99999)}",
        date=fr_date(fake.date_between(start_date="-1y", end_date="-30d"))
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, height - 90 * mm, f"Objet : {obj}")

    y = height - 105 * mm
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, "Madame, Monsieur,")
    y -= 10 * mm

    body = (
        "Je me permets de vous adresser ce courrier afin de vous faire part de ma demande "
        "concernant le sujet mentionné en objet. Comme convenu lors de notre précédent échange, "
        "je sollicite votre attention sur ce dossier qui revêt une importance particulière "
        "pour moi.")
    y = _draw_wrapped(c, body, 20 * mm, y, max_width_mm=170)
    y -= 5 * mm

    body2 = (
        "Je reste à votre entière disposition pour tout complément d'information que vous "
        "jugeriez utile. Je vous saurais gré de bien vouloir me faire parvenir une réponse "
        "dans les meilleurs délais.")
    y = _draw_wrapped(c, body2, 20 * mm, y, max_width_mm=170)
    y -= 10 * mm

    closing = (
        "Dans cette attente, je vous prie d'agréer, Madame, Monsieur, "
        "l'expression de mes salutations distinguées.")
    y = _draw_wrapped(c, closing, 20 * mm, y, max_width_mm=170)
    y -= 20 * mm

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 30 * mm, y, sender_name)
    c.drawRightString(width - 30 * mm, y - 12 * mm, "(signature)")

    c.save()


def generate_attestation(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    title = random.choice(ATTESTATION_TYPES)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 35 * mm, title.upper())

    issuer = fake.name()
    issuer_role = random.choice(["Directeur des Ressources Humaines", "Gérant", "Président", "Responsable administratif"])
    issuer_company = fake.company()
    subject = fake.name()
    subject_birth = fake.date_of_birth(minimum_age=20, maximum_age=60)
    subject_birth_city = random.choice(FRENCH_CITIES)

    y = height - 65 * mm
    c.setFont("Helvetica", 11)
    intro = (
        f"Je soussigné(e) {issuer}, agissant en qualité de {issuer_role} "
        f"de la société {issuer_company}, atteste sur l'honneur que :")
    y = _draw_wrapped(c, intro, 20 * mm, y, max_width_mm=170, line_height_mm=6, size=11)
    y -= 8 * mm

    declaration_options = [
        f"Monsieur/Madame {subject}, né(e) le {fr_date(subject_birth)} à {subject_birth_city}, "
        f"est effectivement employé(e) au sein de notre établissement depuis le "
        f"{fr_date(fake.date_between(start_date='-5y', end_date='-1y'))}.",
        f"Monsieur/Madame {subject}, né(e) le {fr_date(subject_birth)} à {subject_birth_city}, "
        f"a suivi avec assiduité la formation organisée du "
        f"{fr_date(fake.date_between(start_date='-1y', end_date='-6m'))} au "
        f"{fr_date(fake.date_between(start_date='-6m', end_date='-1m'))}.",
        f"Monsieur/Madame {subject}, né(e) le {fr_date(subject_birth)} à {subject_birth_city}, "
        f"est hébergé(e) à mon domicile situé au {fake.street_address()}, "
        f"{fake.postcode()} {fake.city()}, depuis le "
        f"{fr_date(fake.date_between(start_date='-2y', end_date='-3m'))}.",
    ]
    declaration = random.choice(declaration_options)
    y = _draw_wrapped(c, declaration, 20 * mm, y, max_width_mm=170, line_height_mm=6, size=11)
    y -= 10 * mm

    legal_notice = (
        "La présente attestation est délivrée à l'intéressé(e) pour servir et valoir "
        "ce que de droit. J'ai connaissance que cette attestation sera produite en "
        "justice et que toute fausse déclaration de ma part m'exposerait à des sanctions pénales.")
    y = _draw_wrapped(c, legal_notice, 20 * mm, y, max_width_mm=170, line_height_mm=6, size=11)
    y -= 20 * mm

    c.setFont("Helvetica", 11)
    c.drawString(20 * mm, y, f"Fait à {fake.city()}, le {fr_date(fake.date_between(start_date='-30d', end_date='today'))}.")
    y -= 25 * mm

    c.drawRightString(width - 30 * mm, y, "Signature :")
    c.line(width - 80 * mm, y - 10 * mm, width - 30 * mm, y - 10 * mm)

    c.save()


def generate_note_service(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    company = fake.company()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, height - 25 * mm, company)
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, height - 31 * mm, "Direction Générale")

    c.setStrokeColor(colors.black)
    c.setFillColor(colors.lightgrey)
    c.rect(20 * mm, height - 55 * mm, width - 40 * mm, 15 * mm, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 47 * mm, "NOTE DE SERVICE")

    note_ref = f"N°{random.randint(2024, 2026)}-{random.randint(100, 999)}"
    note_date = fake.date_between(start_date="-90d", end_date="today")
    obj = random.choice(NOTE_OBJECTS)

    y = height - 70 * mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Référence :")
    c.setFont("Helvetica", 10)
    c.drawString(55 * mm, y, note_ref)
    y -= 6 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Date :")
    c.setFont("Helvetica", 10)
    c.drawString(55 * mm, y, fr_date(note_date))
    y -= 6 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Émetteur :")
    c.setFont("Helvetica", 10)
    c.drawString(55 * mm, y, f"{fake.name()}, Direction Générale")
    y -= 6 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Diffusion :")
    c.setFont("Helvetica", 10)
    c.drawString(55 * mm, y, "Tous les collaborateurs")
    y -= 6 * mm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "Objet :")
    c.setFont("Helvetica", 10)
    c.drawString(55 * mm, y, obj)
    y -= 15 * mm

    c.setFont("Helvetica", 10)
    body = (
        "Par la présente note, la Direction souhaite vous informer des changements à venir "
        "concernant le sujet mentionné en objet. Ces modifications entreront en vigueur "
        f"à compter du {fr_date(fake.date_between(start_date='today', end_date='+90d'))}. "
        "Nous comptons sur la pleine collaboration de l'ensemble des équipes pour la bonne "
        "mise en application de ces nouvelles dispositions.")
    y = _draw_wrapped(c, body, 20 * mm, y, max_width_mm=170)
    y -= 8 * mm

    body2 = (
        "Pour toute question ou précision, vous êtes invités à prendre contact avec votre "
        "responsable hiérarchique direct ou avec le service des Ressources Humaines.")
    y = _draw_wrapped(c, body2, 20 * mm, y, max_width_mm=170)
    y -= 8 * mm

    body3 = (
        "Nous vous remercions par avance de votre compréhension et de votre coopération.")
    y = _draw_wrapped(c, body3, 20 * mm, y, max_width_mm=170)
    y -= 20 * mm

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 30 * mm, y, "La Direction")

    c.save()


def generate_cv(path: Path):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4

    name = fake.name()
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, height - 28 * mm, name)

    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, height - 36 * mm, fake.street_address())
    c.drawString(20 * mm, height - 41 * mm, f"{fake.postcode()} {fake.city()}")
    c.drawString(20 * mm, height - 46 * mm, f"Tél : {fake.phone_number()}")
    c.drawString(20 * mm, height - 51 * mm, f"Email : {fake.email()}")

    c.setStrokeColor(colors.black)
    c.line(20 * mm, height - 58 * mm, width - 20 * mm, height - 58 * mm)

    y = height - 70 * mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, "Expérience professionnelle")
    y -= 8 * mm

    nb_jobs = random.randint(2, 3)
    for _ in range(nb_jobs):
        job = random.choice(JOB_TITLES)
        company = fake.company()
        end_year = random.randint(2018, 2026)
        start_year = end_year - random.randint(1, 4)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(20 * mm, y, f"{job} — {company}")
        c.setFont("Helvetica-Oblique", 10)
        c.drawRightString(width - 20 * mm, y, f"{start_year} – {end_year}")
        y -= 5 * mm
        c.setFont("Helvetica", 10)
        c.drawString(25 * mm, y, "• Gestion de projets transverses et coordination des équipes.")
        y -= 5 * mm
        c.drawString(25 * mm, y, "• Suivi des indicateurs de performance et reporting mensuel.")
        y -= 9 * mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, "Formation")
    y -= 8 * mm

    diploma = random.choice(CV_DIPLOMAS)
    grad_year = random.randint(2010, 2020)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, diploma)
    c.setFont("Helvetica-Oblique", 10)
    c.drawRightString(width - 20 * mm, y, str(grad_year))
    y -= 5 * mm
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, y, f"Université de {random.choice(FRENCH_CITIES)}")
    y -= 12 * mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, "Compétences")
    y -= 8 * mm

    skills = random.sample(CV_SKILLS, 6)
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, y, " • ".join(skills))
    y -= 12 * mm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(20 * mm, y, "Langues")
    y -= 8 * mm
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, y, "Français (langue maternelle) • Anglais (courant) • Espagnol (notions)")

    c.save()


def generate_other(path: Path, subtype: str):
    if subtype == "lettre": generate_lettre(path)
    elif subtype == "attestation": generate_attestation(path)
    elif subtype == "note": generate_note_service(path)
    elif subtype == "cv": generate_cv(path)
    else: raise ValueError(f"Unknown other subtype: {subtype}")


def main():
    # Invoices
    out_dir = BASE_DIR / "invoice"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Génération de {COUNT_PER_CLASS} factures dans {out_dir}...")
    for i in range(1, COUNT_PER_CLASS + 1):
        path = out_dir / f"invoice_{i:03d}.pdf"
        generate_invoice(path)
        print(f"  ✓ {path.name}")

    # IDs: 10 CNI + 5 passport + 5 permis
    out_dir = BASE_DIR / "id"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nGénération de {COUNT_PER_CLASS} pièces d'identité dans {out_dir}...")
    subtypes = ["cni"] * 10 + ["passport"] * 5 + ["permis"] * 5
    random.shuffle(subtypes)
    for i, subtype in enumerate(subtypes, start=1):
        path = out_dir / f"id_{i:03d}_{subtype}.pdf"
        generate_id(path, subtype)
        print(f"  ✓ {path.name}")

    # Contracts: 10 travail + 10 prestation
    out_dir = BASE_DIR / "contract"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nGénération de {COUNT_PER_CLASS} contrats dans {out_dir}...")
    subtypes = ["travail"] * 10 + ["prestation"] * 10
    random.shuffle(subtypes)
    for i, subtype in enumerate(subtypes, start=1):
        path = out_dir / f"contract_{i:03d}_{subtype}.pdf"
        generate_contract(path, subtype)
        print(f"  ✓ {path.name}")

    # Others: 5 lettre + 5 attestation + 5 note + 5 cv
    out_dir = BASE_DIR / "other"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nGénération de {COUNT_PER_CLASS} autres documents dans {out_dir}...")
    subtypes = ["lettre"] * 5 + ["attestation"] * 5 + ["note"] * 5 + ["cv"] * 5
    random.shuffle(subtypes)
    for i, subtype in enumerate(subtypes, start=1):
        path = out_dir / f"other_{i:03d}_{subtype}.pdf"
        generate_other(path, subtype)
        print(f"  ✓ {path.name}")

    print(f"\nTerminé. Total : {4 * COUNT_PER_CLASS} PDFs générés.")


if __name__ == "__main__":
    main()