"""Публичные данные сайта для pet-проекта. Не настоящий бизнес."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SiteInfo:
    brand_name: str = "AlexZhiryakov"
    legal_name: str = "ООО «AlexZhiryakov»"
    project_note: str = (
        "Демонстрационный pet-проект каталога. Не является действующим интернет-магазином "
        "и не принимает реальную оплату."
    )
    # Только для отображения на сайте. На эту почту заявки сами не уходят.
    email: str = "alexzhiryakov17@mail.ru"
    phone_primary: str = "+7(999) 111-22-33"
    phone_primary_tel: str = "+79991112233"
    phone_secondary: str = "+7(999) 444-55-66"
    phone_secondary_tel: str = "+79994445566"
    whatsapp_number: str = "79991112233"
    telegram_username: str = "altay_demo_portfolio"
    office_city: str = "г. Новосибирск"
    office_address: str = "центр города (демо)"
    warehouse_city: str = "г. Новосибирск"
    warehouse_address: str = "центр города (демо)"
    work_hours: str = "Пн.–Пт.: с 9:00 до 18:00"
    # Площадь Ленина / центр Новосибирска
    office_lat: float = 55.030204
    office_lon: float = 82.920430
    warehouse_lat: float = 55.028900
    warehouse_lon: float = 82.922800
    map_center_lat: float = 55.030204
    map_center_lon: float = 82.920430
    copyright_year: str = "2025"
    legal_address: str = "630099, г. Новосибирск, центр города (демо)"
    inn: str = "5400000000"
    kpp: str = "540001001"
    ogrn: str = "1235400000000"
    okpo: str = "00000000"
    bank_name: str = "Демо-банк (вымышленный)"
    checking_account: str = "40702810000000000000"
    correspondent_account: str = "30101810000000000000"
    bik: str = "045000000"
    director: str = "AlexZhiryakov"
    activity: str = (
        "Демонстрация каталога сварочного оборудования и материалов "
        "(учебный/портфолио-проект)"
    )

    @property
    def office_full(self) -> str:
        return f"{self.office_city}, {self.office_address}"

    @property
    def warehouse_full(self) -> str:
        return f"{self.warehouse_city}, {self.warehouse_address}"

    @property
    def whatsapp_url(self) -> str:
        return f"https://wa.me/{self.whatsapp_number}"

    @property
    def telegram_url(self) -> str:
        return f"https://t.me/{self.telegram_username}"

    @property
    def mailto(self) -> str:
        return f"mailto:{self.email}"


SITE = SiteInfo()
