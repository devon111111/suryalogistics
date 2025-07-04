from fastapi import BackgroundTasks, APIRouter, HTTPException, Header, status,Form
from fastapi.responses import HTMLResponse, FileResponse
from app.services import send_email_background,generate_uuid_header
from app.models import ContactForm
from pathlib import Path


router=APIRouter()

IMAGE_DIR = Path(__file__).parent.parent / "static" / "images"


@router.get("/", include_in_schema=False)
async def read_index():
    html_path = Path(__file__).parent.parent / "static" / "home.html"
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read(), status_code=200, headers=generate_uuid_header())

@router.get("/about", include_in_schema=True)
async def about_page():
    html_path = Path(__file__).parent.parent / "static" / "about.html"
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read(), status_code=200, headers=generate_uuid_header())

@router.get("/services",include_in_schema=True)
async def services_page():
    html_path = Path(__file__).parent.parent / "static" / "service.html"
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read(), status_code=200, headers=generate_uuid_header())

@router.get("/location",include_in_schema=True)
async def location_page():
    html_path = Path(__file__).parent.parent / "static" / "location.html"
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read(), status_code=200, headers=generate_uuid_header())

@router.get("/contact",include_in_schema=True)
async def contact_page():
    html_path = Path(__file__).parent.parent / "static" / "contact.html"
    with open(html_path, "r") as f:
        return HTMLResponse(content=f.read(), status_code=200, headers=generate_uuid_header())


IMAGE_DIRS = Path(__file__).parent.parent / "static" / "image"

@router.get("/images/{image_name}", include_in_schema=True)
async def load_image(image_name: str):
    file_path = IMAGE_DIRS / image_name
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(
        path=file_path,
        media_type="image/jpeg",
        filename=image_name
    )


# Simulated valid_uuids set (should be imported from service.py)
valid_uuids = set()

@router.post("/send-email")
async def send_email(
    background_tasks: BackgroundTasks,
    form_fields_phone: str = Form(..., alias="form_fields[field_1712b6c]"),
    form_fields_pickup_location: str = Form(..., alias="form_fields[field_5e7c41d]"),
    form_fields_shifting_date: str = Form(..., alias="form_fields[field_30c420f]"),
    form_fields_name: str | None = Form(None, alias="form_fields[name]"),
    post_id: str | None = Form(None),
    form_id: str | None = Form(None),
    action: str | None = Form(None),
    referrer: str | None = Form(None),
    x_session_uuid: str | None = Header(default=None)
):
    # # Validate session UUID
    # if x_session_uuid not in valid_uuids:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid session UUID"
    #     )

    # Create ContactForm instance
    try:
        form = ContactForm(
            phone=form_fields_phone,
            pickup_location=form_fields_name,
            drop_location= form_fields_pickup_location,  # No drop_location in form data
            shifting_date=form_fields_shifting_date
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Validation checks from original endpoint
    if form.drop_location and form.pickup_location.strip().lower() == form.drop_location.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pickup and drop-off locations cannot be the same"
        )
    if not form.phone.isdigit() or len(form.phone) != 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must contain exactly 10 digits"
        )
    if "test" in form.pickup_location.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid pickup_location: test pickup_location are not allowed"
        )
    if form.drop_location and "test" in form.drop_location.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid drop_location: test drop_location are not allowed"
        )

    # Queue email task to run in background
    background_tasks.add_task(send_email_background, form)

    return {"message": "Your request has been submitted. We will contact you soon."}