from __future__ import annotations

import typing as t


def _validate_key(key: str) -> None:
    if not key.isidentifier():
        raise ValueError(key)
    if key.startswith("_"):
        raise ValueError(key)


def _validate_kwargs(**kwargs: t.Iterable[str]) -> None:
    for key, value in kwargs.items():
        _validate_key(key)


# TODO(d.burmistrov): think about "prefix = 'garson_'" (note about logging)
class Info:

    def __init__(self, **kwargs):
        _validate_kwargs(**kwargs)
        object.__setattr__(self, "_data", kwargs)

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self):
        return bool(self._data)

    def __iter__(self) -> t.Iterator:
        return iter(self._data)

    def __getattr__(self, item: str) -> t.Any:
        _validate_key(item)
        if item in self._data:
            return self._data[item]
        raise AttributeError(item)

    def __setattr__(self, key: str, value: t.Any) -> None:
        _validate_kwargs(**{key: value})
        self._data[key] = value

    def __delattr__(self, item: str) -> None:
        raise NotImplementedError

    def do_touch(self, key: str, **kwargs: t.Any) -> Info:
        setattr(self, key, i := Info(**kwargs))
        return i

    def do_dict(self):
        return {k: (v._data if isinstance(v, Info) else v)
                for k, v in self._data.items()}

    def do_flat(self, sep: str = ".", prefix: t.Optional[str] = None):
        _prefix = [prefix] if prefix else []
        result = {}
        queue: list[tuple[t.Any, ...]] = [(self._data,)]
        while queue:
            *path, item = queue.pop()
            for k, v in item.items():
                if isinstance(v, Info):
                    queue.append((*path, k, v._data))
                else:
                    result[sep.join(_prefix + path + [k])] = v
        return result

    def do_clear(self):
        self._data.clear()

    def do_update(self, **kwargs):
        _validate_kwargs(**kwargs)
        self._data.update(**kwargs)
