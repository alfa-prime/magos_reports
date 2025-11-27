from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core import check_api_key, get_gateway_service
from app.service import GatewayService
from app.service.report.invitro_list import process_invitro_list
from app.service.report.patient_with_service import get_list_patients_with_services, generate_excel_from_models

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
    file_stream = generate_excel_from_models(patients_list)
    filename = f"report_32430_{start_date}-{end_date}.xlsx"

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get(
    path="/invitro",
    description="Список анализов ИНВИТРО",
    summary="Формирует отчет по анализам ИНВИТРО с указанием источника оплаты"
)
async def get_invitro_report(
        gateway: Annotated[GatewayService, Depends(get_gateway_service)],
        start_date: str = "13.11.2025",
        end_date: str = "13.11.2025"
) -> StreamingResponse:
    # Вызываем сервис, он вернет BytesIO
    file_stream = await process_invitro_list(start_date, end_date, gateway)

    filename = f"invitro_{start_date}-{end_date}.xlsx"

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
