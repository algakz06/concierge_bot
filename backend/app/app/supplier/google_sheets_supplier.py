from gspread import service_account, Client, Spreadsheet, Worksheet  # type: ignore
from typing import List
import json
import datetime

from app.models.app_models import User, Request
from app.configs.settings import settings
from app.supplier.redis_supplier import RedisSupplier


class GoogleSheetSupplier:
    CREDENTIALS_FILE: str
    TABLE_URL: str

    gs: Client
    spreadsheet: Spreadsheet
    services_worksheet_ru: Worksheet
    services_worksheet_eng: Worksheet
    prices_worksheet: Worksheet
    user_stats_worksheet: Worksheet
    request_stats_worksheet: Worksheet
    metadata_worksheet: Worksheet
    env_worksheet: Worksheet

    services_ru_raw: List[dict]
    services_eng_raw: List[dict]
    prices_raw: List[dict]

    redis_supplier: RedisSupplier

    def __init__(self, redis: RedisSupplier) -> None:
        self.CREDENTIALS_FILE = settings.GS_CREDENTIALS_FILE
        self.TABLE_URL = settings.GS_SPREADSHEET_URL
        self.gs = service_account(self.CREDENTIALS_FILE)
        self.spreadsheet = self.get_table()
        self.services_worksheet_eng = self.spreadsheet.worksheet("eng")
        self.services_worksheet_ru = self.spreadsheet.worksheet("ru")
        self.user_stats_worksheet = self.spreadsheet.worksheet("user_stats")
        self.request_stats_worksheet = self.spreadsheet.worksheet("request_stats")
        self.prices_worksheet = self.spreadsheet.worksheet("prices")
        self.metadata_worksheet = self.spreadsheet.worksheet("metadata")

        self.redis_supplier = redis
        self.get_rows()
        self.get_services()
        self.get_prices()
        self.get_metadata()
        self._set_env()

    def _set_env(self) -> None:
        self.env_worksheet = self.spreadsheet.worksheet("env")
        env_data = self.env_worksheet.get_all_records()
        env = dict()
        for row in env_data:
            env[row["key"]] = row["value"]
        settings.TG_TOKEN = env.get("TG_TOKEN")
        settings.YOUMONEY_APP_ID = env.get("YOUMONEY_APP_ID")
        settings.YOUMONEY_SECRET_KEY = env.get("YOUMONEY_SECRET_KEY")
        settings.ADMIN_TG_ID = env.get("ADMIN_TG_ID")
        settings.ADMIN_CHAT_ID = env.get("ADMIN_CHAT_ID")
        settings.ADMIN_USERNAME = env.get("ADMIN_USERNAME")
        settings.TERMS_URL = env.get("TERMS_URL")

    def get_table(self) -> Spreadsheet:
        return self.gs.open_by_url(self.TABLE_URL)

    def get_rows(self):
        self.services_eng_raw = self.services_worksheet_eng.get_all_records()
        self.services_ru_raw = self.services_worksheet_ru.get_all_records()
        self.prices_raw = self.prices_worksheet.get_all_records()
        self.metadata_raw = self.metadata_worksheet.get_all_records()

    def get_services(self) -> None:
        eng_services = {}
        eng_services["services"] = [
            (row["text"], str(row["id"]))
            for row in self.services_eng_raw
            if not row["is_reply"]
        ]
        eng_services["replies"] = {
            str(row["id"]): row["text"]
            for row in self.services_eng_raw
            if row["is_reply"]
        }

        ru_services = {}
        ru_services["services"] = [
            (row["text"], str(row["id"]))
            for row in self.services_ru_raw
            if not row["is_reply"]
        ]
        ru_services["replies"] = {
            str(row["id"]): row["text"]
            for row in self.services_ru_raw
            if row["is_reply"]
        }

        self.redis_supplier.store_data("eng", json.dumps(eng_services))
        self.redis_supplier.store_data("ru", json.dumps(ru_services))

    def get_prices(self):
        self.redis_supplier.store_data("prices", json.dumps(self.prices_raw))

    def get_metadata(self):
        d = {"metadata": {}}
        for row in self.metadata_raw:
            d["metadata"][row["name"]] = {
                "ru": row["ru"],
                "eng": row["eng"],
            }
        self.redis_supplier.store_data("metadata", json.dumps(d))

    def upload_users_statistic(self, users: List[User]) -> None:
        self.user_stats_worksheet.update(
            sorted(
                [
                    [
                        user.telegram_username,
                        user.telegram_id,
                        user.phone_number,
                        user.name,
                        user.localization,
                        user.balance,
                        f"До {user.subscription.end_at}"
                        if user.subscription
                        else "Нет",
                    ]
                    for user in users
                ],
                key=lambda x: x[3],  # type: ignore
            ),
            "A2",
        )

    def upload_request_statistic(self, requests: List[Request]) -> None:
        self.request_stats_worksheet.update(
            sorted(
                [
                    [
                        request.id,
                        request.telegram_username,
                        request.theme,
                        request.created_at.strftime("%d.%m.%Y %H:%M"),
                        str(request.conversation),
                        request.status,
                        request.details,
                        "",
                        request.item.category if request.item else "",
                        request.item.description if request.item else "",
                        request.item.price if request.item else "",
                    ]
                    for request in requests
                ],
                key=lambda x: datetime.datetime.strptime(x[3], "%d.%m.%Y %H:%M"),  # type: ignore
                reverse=True,
            ),
            "A2",
        )


gs = GoogleSheetSupplier(RedisSupplier())
