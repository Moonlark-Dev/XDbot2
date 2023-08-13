from . import user


def _get_exp(user_id):
    return user.get_user_data(user_id)["exp"]


def get_level(exp):
    level = 1
    while True:
        if exp > level**2:
            level += 1
        else:
            break
    return level


def get_exp(user_id):
    exp = _get_exp(user_id)
    return exp - (get_level(exp) - 1)**2


def get_user_level(user_id):
    return get_level(_get_exp(user_id))


def add_exp(user_id, count):
    data = user.get_user_data(user_id)
    data["exp"] += count
    user.change_user_data(user_id, data)


def _set_exp(user_id, count):
    data = user.get_user_data(user_id)
    data["exp"] = count
    user.change_user_data(user_id, data)
