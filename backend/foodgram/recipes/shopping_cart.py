from io import BytesIO
from pathlib import Path

from django.db.models import CharField, Sum
from django.db.models.functions import Cast
from xhtml2pdf import pisa


def make_pdf(user):
    """Function, what creates pdf-file from sql-data"""
    carted_recipes = user.shopping_cart.all()

    ingredient_list = carted_recipes.values(
        'ingredientamount__ingredient__name',
        'ingredientamount__ingredient__measurement_unit'
    )
    ingredient_list_amount = ingredient_list.annotate(
        formatted_decimal=Cast(
            Sum('ingredientamount__amount'),
            CharField(max_length=10)
        ),
    )

    formatted_list = []

    for amounts in ingredient_list_amount:
        formatted_string = f"""
            <li> {amounts['ingredientamount__ingredient__name']}
            - {amounts['formatted_decimal']}
            {amounts['ingredientamount__ingredient__measurement_unit']} </li>
            """
        formatted_list.append(formatted_string)

    list_to_string = ''.join(formatted_list)
    path_to_font = Path('recipes/fonts/font.css').resolve()

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <link rel="stylesheet" type="text/css" href="{path_to_font}">
      </head>
    <body>
      <h1 style="font-family: 'MyCustomFont';">Ваш список покупок:</h1>
        <ul style="font-family: 'MyCustomFont';">
          {list_to_string}
        </ul>
      </body>
    </html>
    """

    buffer = BytesIO()
    pisa.CreatePDF(html.encode('utf-8'), buffer, encoding='utf-8')
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
