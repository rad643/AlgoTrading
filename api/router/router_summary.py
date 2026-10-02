from fastapi import APIRouter, HTTPException, status

from api.router.dependencies import SummaryServiceDep

router_summary = APIRouter(tags=["summary"])


@router_summary.get("/summary/{id}")
async def get_summary(id: int, summary_service: SummaryServiceDep):

    summary = await summary_service.read(id)
    if summary:
        return summary
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Id number {id} doesn't exist",
    )


@router_summary.delete("/summary/{id}")
async def delete_summary(id: int, summary_service: SummaryServiceDep):

    summary = await summary_service.delete(id)
    if summary:
        return {"message": f"Summary with id number {id} has been deleted"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Id number {id} doesn't exist",
    )
