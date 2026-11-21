from fastapi import APIRouter, HTTPException, status, Depends
from app.api.auth import reject_customer_edit
from app.services.restaurant_service import (
    restaurant_service_create,
    restaurant_service_list,
    restaurant_service_get_by_cuisine,
    restaurant_service_get_by_id,
    restaurant_service_delete,
    restaurant_service_update,
    require_unique_restaurant_name,
)
from app.errors import ResourceInUseError, RestaurantNotFoundError, DuplicateRestaurantError

from app.schemas.restaurant import RestaurantCreate, RestaurantRead, RestaurantUpdate, RestaurantPreview

router = APIRouter(prefix="/restaurants")


@router.post(
    "/validate",
    response_model=RestaurantCreate,
    summary="Validate a demo restaurant",
    description="Check submitted fields and names from the demo list without reading or saving restaurant records.",
    responses={409: {"description": "Another restaurant in the submitted list already uses this name"}},
)
def restaurant_route_validate_preview(payload: RestaurantPreview) -> RestaurantCreate:
    try:
        require_unique_restaurant_name(payload.restaurant.name, payload.other_names)
    except DuplicateRestaurantError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return payload.restaurant

@router.get(
    "",
    response_model=list[RestaurantRead],
    status_code=status.HTTP_200_OK,
    summary="List restaurants",
    description="Return all restaurants. Returns an empty list if no restaurants exist."
)
def restaurant_route_get_list() -> list[RestaurantRead]:
    return restaurant_service_list()


@router.post( 
        "", 
        response_model=RestaurantRead,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(reject_customer_edit)],
        responses={
            401: {"description": "Sign-in required"},
            403: {"description": "Customers cannot edit restaurant or menu information"},
        })
def restaurant_route_create(new_restaurant: RestaurantCreate) -> RestaurantRead:
    try:
        return restaurant_service_create(new_restaurant)

    except DuplicateRestaurantError as e:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = str(e)
        )


@router.patch(
    "/{restaurant_id}",
    response_model=RestaurantRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(reject_customer_edit)],
    responses={
        401: {"description": "Sign-in required"},
        403: {"description": "Customers cannot edit restaurant or menu information"},
    }
)
def restaurant_route_update(restaurant_id: int, updates: RestaurantUpdate) -> RestaurantRead:
    try:
        return restaurant_service_update(restaurant_id, updates)
    except RestaurantNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DuplicateRestaurantError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.get(
    "/filtered-by-{cuisine}-type",
    response_model=list[RestaurantRead],
    status_code=status.HTTP_200_OK,
    summary="Filter restaurants by cuisine",
    description="Return restaurants matching the requested cuisine.",
    responses={
        404: {"description": "No restaurants found for the requested cuisine"}
    }
)
def restaurant_route_get_by_cuisine(cuisine: str) -> list[RestaurantRead]:
    try:
        if cuisine is None:
            return restaurant_service_list()
        return restaurant_service_get_by_cuisine(cuisine)
    except RestaurantNotFoundError as e:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = str(e)
        )
#order matters here, has to be above {restaurant_id}

@router.get(
    "/{restaurant_id}",
    response_model=RestaurantRead,
    status_code=status.HTTP_200_OK,
    summary="Get restaurant details",
    description="Return the details of a restaurant by its ID.",
    responses={
        404: {"description": "Restaurant not found"}
    }
)
def restaurant_route_get_by_id(restaurant_id: int) -> RestaurantRead:
    try: 
        return restaurant_service_get_by_id(restaurant_id)

    except RestaurantNotFoundError as e:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = str(e)
        )



@router.delete(
        "/{restaurant_id}",
        status_code = status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(reject_customer_edit)],
        responses={
            401: {"description": "Sign-in required"},
            403: {"description": "Customers cannot edit restaurant or menu information"},
            409: {"description": "Restaurant is still in use and cannot be deleted"},
        }
        )
def restaurant_route_delete(restaurant_id: int) -> None:
    try:
        return restaurant_service_delete(restaurant_id)

    except RestaurantNotFoundError as e:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = str(e)
        )
    except ResourceInUseError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
