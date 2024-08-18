"""Helper module for a simple speckle object tree flattening."""

from collections.abc import Iterable
from typing import Optional, List, Tuple

from specklepy.objects import Base
from specklepy.objects.other import Instance, Transform


def flatten_base(base: Base) -> Iterable[Base]:
    """Flatten a base object into an iterable of bases.

    This function recursively traverses the `elements` or `@elements` attribute of the
    base object, yielding each nested base object.

    Args:
        base (Base): The base object to flatten.

    Yields:
        Base: Each nested base object in the hierarchy.
    """
    # Attempt to get the elements attribute, fallback to @elements if necessary
    elements = getattr(base, "elements", getattr(base, "@elements", None))

    if elements is not None:
        for element in elements:
            yield from flatten_base(element)

    yield base


def flatten_base_thorough(base: Base, parent_type: str = None) -> Iterable[Base]:
    """Take a base and flatten it to an iterable of bases.

    Args:
        base: The base object to flatten.
        parent_type: The type of the parent object, if any.

    Yields:
        Base: A flattened base object.
    """
    if isinstance(base, Base):
        base["parent_type"] = parent_type

    elements = getattr(base, "elements", getattr(base, "@elements", None))
    if elements:
        try:
            for element in elements:
                # Recursively yield flattened elements of the child
                yield from flatten_base_thorough(element, base.speckle_type)
        except KeyError:
            pass
    elif hasattr(base, "@Lines"):
        categories = base.get_dynamic_member_names()

        # could be old revit
        try:
            for category in categories:
                print(category)
                if category.startswith("@"):
                    category_object: Base = getattr(base, category)[0]
                    yield from flatten_base_thorough(
                        category_object, category_object.speckle_type
                    )

        except KeyError:
            pass

    yield base


def extract_base_and_transform(
    base: Base,
    inherited_instance_id: Optional[str] = None,
    transform_list: Optional[List[Transform]] = None,
) -> Tuple[Base, str, Optional[List[Transform]]]:
    """
    Traverses Speckle object hierarchies to yield `Base` objects and their transformations.
    Tailored to Speckle's AEC data structures, it covers both newer hierarchical structures
    with Collections and older Revit-specific data patterns.

    Parameters:
    - base (Base): The starting point `Base` object for traversal.
    - inherited_instance_id (str, optional): The inherited identifier for `Base` objects without a unique ID.
    - transform_list (List[Transform], optional): Accumulated list of transformations from parent to child objects.

    Yields:

    Returns:
        object:
    - tuple: A `Base` object, its identifier, and a list of applicable `Transform` objects or None.

    The ID of the `Base` object is either the inherited identifier for a definition from an instance
    or the one defined in the object.
    """
    current_id = getattr(base, "id", inherited_instance_id)
    transform_list = transform_list or []

    if isinstance(base, Instance):
        if base.transform:
            transform_list.append(base.transform)
        if base.definition:
            yield from extract_base_and_transform(
                base.definition, current_id, transform_list.copy()
            )
    else:
        yield base, current_id, transform_list

        elements_attr = getattr(base, "elements", []) or getattr(base, "@elements", [])
        for element in elements_attr:
            if isinstance(element, Base):
                yield from extract_base_and_transform(
                    element, current_id, transform_list.copy()
                )

        for attr_name in dir(base):
            if attr_name.startswith("@"):
                attr_value = getattr(base, attr_name)
                if isinstance(attr_value, Base) and hasattr(attr_value, "elements"):
                    yield from extract_base_and_transform(
                        attr_value, current_id, transform_list.copy()
                    )
