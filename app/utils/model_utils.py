def update_model_fields(model, update_obj, exclude: set[str] = None) -> None:
    """
    Update the model attributes according to the non None values of the Pydantic object.
    """
    exclude = exclude or set()
    for field, value in update_obj.model_dump(exclude_unset=True).items():
        if field in exclude:
            continue
        setattr(model, field, value)