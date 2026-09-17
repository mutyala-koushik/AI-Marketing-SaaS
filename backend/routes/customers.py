import csv
from io import StringIO
from services.segment_interpreter import interpret_segments

from fastapi import APIRouter, File, HTTPException, UploadFile

from ml.segmentation import segment_customers


router = APIRouter(
    prefix="/customers",
    tags=["Customer Intelligence"]
)


@router.post("/segment")
async def segment_customer_data(
    file: UploadFile = File(...)
):
    """
    Upload a CSV file and perform customer segmentation.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    try:
        content = await file.read()

        text = content.decode("utf-8")

        reader = csv.DictReader(
            StringIO(text)
        )

        rows = list(reader)

        if not rows:
            raise HTTPException(
                status_code=400,
                detail="The CSV file is empty."
            )

        segmented_customers, segment_summaries = (
            segment_customers(
                rows,
                n_clusters=3
            )
        )
        interpreted_segments = interpret_segments(
    segment_summaries
)

        return {
            "status": "success",
            "message": "Customer segmentation completed.",
            "total_customers": len(segmented_customers),
            "segments": interpreted_segments,
            "customers": segmented_customers
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV file must use UTF-8 encoding."
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Segmentation failed: {str(error)}"
        )