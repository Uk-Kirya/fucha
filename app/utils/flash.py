from fastapi import Request


async def set_flash(
    request: Request,
    messages: list,
    category: str = "info",
) -> None:
    """
    Тут мы записываем данные во flash сообщение
    :param request: Request instance
    :param messages: Messages list
    :param category: Category string
    :return: None
    """
    request.session["flash"] = {
        "messages": [item for item in messages],
        "category": category,
    }


async def set_form_data(request: Request, data: dict) -> None:
    """
    Тут мы записываем данные в форму, если валидация формы не прошла, чтобы данные в форме не стирались
    :param request: Request instance
    :param data: Form data
    :return: None
    """

    request.session["form_data"] = data
