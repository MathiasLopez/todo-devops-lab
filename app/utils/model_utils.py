def update_model_fields(model, update_obj) -> None:
    """
    Update the model attributes according to the non None values of the Pydantic object.
    """
    for field, value in update_obj.model_dump(exclude_unset=True).items():
        setattr(model, field, value)