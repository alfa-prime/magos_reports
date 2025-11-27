import io
import json
from openpyxl import Workbook
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception
from async_lru import alru_cache

from app.core import logger, PAY_TYPE_MAPPER
from app.service.gateway.gateway import GatewayService
from app.service.tool.tool import is_retryable_exception


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(2),
    retry=retry_if_exception(is_retryable_exception), # noqa
)
@alru_cache(maxsize=1000)
async def _fetch_usluga_gost_code(usluga_complex_id, gateway_service: GatewayService):
    payload = {
        "params": {
            "c": "UslugaComplex",
            "m": "loadLinkedUslugaGrid"
        },
        "data": {
            "UslugaComplex_id": usluga_complex_id,
            "object": "UslugaComplex",
        }
    }
    response_json = await gateway_service.make_request(method="post", json=payload)
    return response_json[0].get("UslugaComplex_Code", "")


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(2),
    retry=retry_if_exception(is_retryable_exception)  # noqa
)
@alru_cache(maxsize=1000)
async def _fetch_usluga_codes(usluga_complex_code_name: str, gateway_service: GatewayService) -> dict:
    payload = {
        "params": {
            "c": "UslugaComplex",
            "m": "loadUslugaContentsGrid"
        },
        "data": {
            "UslugaComplex_CodeName": usluga_complex_code_name,
            "object": "UslugaComplex",
            "UslugaComplex_pid": "3010101000029801",
            "contents": 2
        }
    }
    response_json = await gateway_service.make_request(method="post", json=payload)

    usluga_complex_id = response_json[0].get("UslugaComplex_id")
    invitro_code = response_json[0].get("UslugaComplex_Code")
    gost_code = await _fetch_usluga_gost_code(usluga_complex_id, gateway_service)

    return {"gost": gost_code, "invitro": invitro_code}


@retry(
    stop=stop_after_attempt(5),
    wait=wait_fixed(2),
    retry=retry_if_exception(is_retryable_exception),  # noqa
)
@alru_cache(maxsize=1000)
async def _fetch_pay_type(evn_direction_id: str, gateway_service: GatewayService):
    payload = {
        "params": {
            "c": "EvnLabRequest",
            "m": "load"
        },
        "data": {
            "EvnDirection_id": evn_direction_id,
            "delDocsView": 0,
        }
    }
    response_json = await gateway_service.make_request(method="post", json=payload)
    pay_type_id = response_json[0].get("PayType_id", "")
    return PAY_TYPE_MAPPER.get(pay_type_id, "")


async def _fetch_source_data(start_date: str, end_date: str, gateway_service: GatewayService):
    payload = {
        "params": {
            "c": "EvnLabRequest",
            "m": "loadEvnLabRequestList"
        },
        "data": {
            "EvnStatus_id": 2,
            "MedServiceType_SysNick": "reglab",
            "MedService_id": "3010101000015552",
            "fit": 1,
            "begDate": start_date,
            "endDate": end_date,
            "filterWorkELRByDate": 1,
            "filterDoneELRByDate": 1,
            "formMode": "false",
        }
    }
    response = await gateway_service.make_request(method="post", json=payload)
    return response.get("data", "") # noqa


async def process_invitro_list(start_date: str, end_date: str, gateway_service: GatewayService):
    source_data = await _fetch_source_data(start_date, end_date, gateway_service)

    book = Workbook()
    sheet = book.active
    titles = ["Фамилия", "Имя", "Отчество", "ДР", "Дата", "Код ГОСТ", "Код Инвитро", "Оплата", "Услуга", "Пункт забора",
              "Лаборатория"]
    sheet.append(titles)
    data_to_save = []

    for item in source_data:
        services_list = json.loads(item.get("EvnLabRequest_UslugaName", ""))

        evn_direction_id = item.get("EvnDirection_id")
        pay_type = await _fetch_pay_type(evn_direction_id, gateway_service)

        surname = item.get("Person_Surname", "").title()
        first_name = item.get("Person_Firname", "").title()
        middle_name = item.get("Person_Secname", "").title()
        birthday = item.get("Person_Birthday", "")
        service_date = item.get("TimetableMedService_Date", "")
        service_point = item.get("MedServiceDid_Nick", "")
        service_lab = item.get("MedService_Nick", "")

        record = {
            "surname": surname,
            "first_name": first_name,
            "middle_name": middle_name,
            "birthday": birthday,
            "service_date": service_date,
            "service": services_list,
        }

        data_to_save.append(record)

        for service in services_list:
            service_name = service.get("UslugaComplex_Name")
            service_code = await _fetch_usluga_codes(service_name, gateway_service)
            row_data = [
                surname,
                first_name,
                middle_name,
                birthday,
                service_date,
                service_code.get("gost", ""),
                service_code.get("invitro", ""),
                pay_type,
                service_name,
                service_point,
                service_lab,
            ]

            sheet.append(row_data)

    output_stream = io.BytesIO()
    book.save(output_stream)
    output_stream.seek(0)

    return output_stream
