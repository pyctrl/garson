def validate_name(name: str) -> None:
    if not (name.isidentifier()
            and (name not in __builtins__)):  # type: ignore[operator]
        raise ValueError
