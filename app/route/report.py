from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import io
from openpyxl import Workbook
from datetime import date, datetime

from app.core import check_api_key, get_gateway_service
from app.service import GatewayService
from app.service.report.patient_with_service import get_list_patients_with_services

router = APIRouter(
    prefix="/report", tags=["Отчеты"], dependencies=[Depends(check_api_key)]
)


@router.get(
    path="/32430",
    description="Список пациентов с услугами по стационару",
    summary="Формирует отчет по услугам оказанным пациентам в стационаре с указанием источника оплаты")
async def list_patients_with_services(
        gateway: Annotated[GatewayService, Depends(get_gateway_service)],
        start_date: str = "13.11.2025",
        end_date: str = "13.11.2025"
)-> StreamingResponse:
    patients_list = await get_list_patients_with_services(start_date, end_date, gateway)

    output_stream = io.BytesIO()
    work_book = Workbook()
    sheet = work_book.active

    for row in patients_list:
        # Превращаем модель в словарь
        row_dict = row.model_dump() # noqa
        # Берем только значения и превращаем в список
        row_values = list(row_dict.values())
        sheet.append(row_values)

        # в excel приводит дату к виду ДД.ММ.ГГГГ
        current_row = sheet[sheet.max_row]
        # Проходим по всем ячейкам в этой строке
        for cell in current_row:
            # Если в ячейке дата — меняем формат отображения
            if isinstance(cell.value, (date, datetime)):
                cell.number_format = 'DD.MM.YYYY'

    # Сохраняем книгу в поток
    work_book.save(output_stream)
    output_stream.seek(0)

    filename = f"report_32430_{start_date}-{end_date}.xlsx"

    return StreamingResponse(
        output_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
